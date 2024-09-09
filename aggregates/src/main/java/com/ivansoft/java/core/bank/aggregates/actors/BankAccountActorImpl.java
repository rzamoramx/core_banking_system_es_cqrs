package com.ivansoft.java.core.bank.aggregates.actors;

import com.ivansoft.core.bank.account.models.Transaction;
import com.ivansoft.java.core.bank.aggregates.services.EventSourceService;
import io.dapr.actors.ActorId;
import io.dapr.actors.runtime.AbstractActor;
import io.dapr.actors.runtime.ActorRuntimeContext;
import reactor.core.publisher.Mono;
import com.ivansoft.core.bank.account.models.TransactionType;
import reactor.util.retry.Retry;
import java.time.Duration;
import java.util.Date;
import java.util.Optional;
import java.util.UUID;
import java.util.logging.Logger;


public class BankAccountActorImpl extends AbstractActor implements BankAccountActor {
    private static final Logger log = Logger.getLogger(BankAccountActorImpl.class.getName());
    private final String STATE_NAME = "balance";
    private final int MAX_RETRIES = 3;
    private final Duration RETRY_DELAY = Duration.ofSeconds(1);
    private final EventSourceService eventSourceService = new EventSourceService();

    public BankAccountActorImpl(ActorRuntimeContext runtimeContext, ActorId id) {
        super(runtimeContext, id);
    }

    @Override
    public Mono<String> transaction(TransactionDetails transactionDetails) {
        var errors = validations(transactionDetails);
        if (errors != null) {
            return Mono.just(errors);
        }

        return Mono.fromCallable(() -> {
            Double currentBalance = getCurrentBalance();
            log.info("Current balance: " + currentBalance);

            Double newBalance = calculateNewBalance(currentBalance, transactionDetails);

            return new Object[]{currentBalance, newBalance};
        })
        .flatMap(balances -> {
            Double currentBalance = (Double) balances[0];
            Double newBalance = (Double) balances[1];

            return publishEventWithRetry(transactionDetails)
                .flatMap(published -> {
                    if (published) {
                        return saveNewBalance(newBalance)
                           .then(Mono.just("Transaction successful. New balance: " + newBalance))
                           .onErrorResume(e -> Mono.just("Transaction failed: Unable to save new balance. Balance unchanged: " + currentBalance));
                    } else {
                        log.severe("Failed to publish event. Transaction cancelled.");
                        return Mono.just("Transaction failed: Unable to publish event. Balance unchanged: " + currentBalance);
                    }
                });
        }).onErrorResume(e -> Mono.just("Error: " + e.getMessage()));
    }

    private String validations(TransactionDetails transactionDetails) {
        // if amount is less than or equal to 0, return error
        if (transactionDetails.getAmount() <= 0) {
            return "Invalid amount";
        }

        // if type is not deposit or withdraw, return error
        if (!transactionDetails.getType().equals(TransactionType.DEPOSIT) &&
                !transactionDetails.getType().equals(TransactionType.WITHDRAWAL)) {
            return "Invalid transaction type";
        }

        // check if state balance doesn't exist
        if (super.getActorStateManager() == null) {
            return "State manager not found";
        }

        return null;
    }

    private double getCurrentBalance() {
        return Optional.ofNullable(super.getActorStateManager()
                .get(STATE_NAME, Double.class).block())
                .orElse(0.0);
    }

    private Mono<Object> saveNewBalance(Double newBalance) {
        return Mono.fromRunnable(() -> {
                    super.getActorStateManager().set(STATE_NAME, newBalance).block();
                    super.getActorStateManager().save().block();
                    log.info("New balance saved: " + newBalance);
                })
                .retryWhen(Retry.fixedDelay(MAX_RETRIES, RETRY_DELAY)
                        .doBeforeRetry(retrySignal ->
                                log.warning("Retrying to save new balance. Attempt: " + (retrySignal.totalRetries() + 1))
                        )
                )
                .onErrorResume(e -> {
                    log.severe("Failed to save new balance after " + MAX_RETRIES + " attempts: " + e.getMessage());
                    return Mono.error(new RuntimeException("Failed to save new balance", e));
                });
    }

    private Double calculateNewBalance(Double currentBalance, TransactionDetails transactionDetails) {
        if (transactionDetails.getType().equals(TransactionType.DEPOSIT)) {
            return currentBalance + transactionDetails.getAmount();
        }
        else if (transactionDetails.getType().equals(TransactionType.WITHDRAWAL)) {
            if (currentBalance < transactionDetails.getAmount()) {
                throw new IllegalStateException("Insufficient funds");
            }
            return currentBalance - transactionDetails.getAmount();
        }
        throw new IllegalArgumentException("Invalid transaction type");
    }

    private Mono<Boolean> publishEventWithRetry(TransactionDetails transaction) {
        return Mono.fromCallable(() -> {
            eventSourceService.publishTransaction(new Transaction(
                    UUID.randomUUID().toString(),
                    super.getId().toString(),
                    transaction.getAmount(),
                    transaction.getType(),
                    "completed",
                    "Transaction completed",
                    new Date(),
                    1
            ));
            return true;
        })
        .retryWhen(Retry.fixedDelay(MAX_RETRIES, RETRY_DELAY)
               .doBeforeRetry(retrySignal ->
                       log.warning("Retrying event publish. Attempt: " + (retrySignal.totalRetries() + 1))
               )
        )
        .onErrorResume(e -> {
              log.severe("Failed to publish event after " + MAX_RETRIES + " attempts: " + e.getMessage());
              return Mono.just(false);
        });
    }
}
