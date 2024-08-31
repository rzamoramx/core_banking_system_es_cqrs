package com.ivansoft.java.core.bank.aggregates.actors;

import com.ivansoft.core.bank.account.models.Transaction;
import com.ivansoft.java.core.bank.aggregates.services.EventSourceService;
import io.dapr.actors.ActorId;
import io.dapr.actors.runtime.AbstractActor;
import io.dapr.actors.runtime.ActorRuntimeContext;
import reactor.core.publisher.Mono;
import com.ivansoft.core.bank.account.models.TransactionType;

import java.util.Date;
import java.util.Optional;
import java.util.UUID;
import java.util.logging.Logger;


public class BankAccountActorImpl extends AbstractActor implements BankAccountActor {
    private static final Logger log = Logger.getLogger(BankAccountActorImpl.class.getName());
    private final String STATE_NAME = "balance";
    private final EventSourceService eventSourceService = new EventSourceService();

    public BankAccountActorImpl(ActorRuntimeContext runtimeContext, ActorId id) {
        super(runtimeContext, id);
    }

    @Override
    public Mono<String> transaction(TransactionDetails transactionDetails) {
        if (transactionDetails.getAmount() > 0) {
            // if type is not deposit or withdraw, return error
            if (!transactionDetails.getType().equals(TransactionType.DEPOSIT) &&
                    !transactionDetails.getType().equals(TransactionType.WITHDRAWAL)) {
                return Mono.just("Invalid transaction type");
            }

            // check if state balance exists
            if (super.getActorStateManager() == null) {
                return Mono.just("State manager not found");
            }

            var balance = Optional.ofNullable(super.getActorStateManager()
                            .get(STATE_NAME, Double.class).block())
                    .orElse(0.0);
            log.info("Actual balance: " + transactionDetails.getAmount());

            // dependent on transaction type, add or subtract amount from balance if balance is sufficient
            if (transactionDetails.getType().equals(TransactionType.DEPOSIT)) {
                balance += transactionDetails.getAmount();

            } else if (transactionDetails.getType().equals(TransactionType.WITHDRAWAL)) {
                if (balance < transactionDetails.getAmount()) {
                    return Mono.just("Insufficient funds");
                }
                balance -= transactionDetails.getAmount();
            }

            // save state
            super.getActorStateManager().set("balance", balance).block();
            balance = super.getActorStateManager().get(STATE_NAME, Double.class).block();
            log.info("New balance: " + balance);
            super.getActorStateManager().save().block();

            // publish it to event source service
            try {
                eventSourceService.publishTransaction(new Transaction(
                        UUID.randomUUID().toString(),
                        super.getId().toString(),
                        transactionDetails.getAmount(),
                        transactionDetails.getType(),
                        "completed",
                        "Transaction completed",
                        new Date()
                ));
            } catch (Exception e) {
                log.severe("Error publishing transaction");
                log.severe(e.getMessage());
                return Mono.just("Error publishing transaction");
            }

            return Mono.just("Transaction successful");
        }
        return null;
    }
}
