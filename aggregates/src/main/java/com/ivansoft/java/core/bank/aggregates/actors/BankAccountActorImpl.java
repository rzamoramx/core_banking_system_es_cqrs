package com.ivansoft.java.core.bank.aggregates.actors;

import io.dapr.actors.ActorId;
import io.dapr.actors.runtime.AbstractActor;
import io.dapr.actors.runtime.ActorRuntimeContext;
import reactor.core.publisher.Mono;
import com.ivansoft.java.core.bank.aggregates.models.TransactionType;
import java.util.NoSuchElementException;


public class BankAccountActorImpl extends AbstractActor implements BankAccountActor {
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

            var balance = 0.0;

            // get state manager
            try {
                balance = super.getActorStateManager().get("balance", Double.class).block();
            }
            catch (NoSuchElementException e) {
                // if no state balance, set one
                System.out.println("No balance found, setting to 0");
                super.getActorStateManager().set("balance", balance).block();
            }

            // for debug, print actual balance
            System.out.println("Actual balance: " + transactionDetails.getAmount());

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
            balance = super.getActorStateManager().get("balance", Double.class).block();
            System.out.println("New balance: " + balance);
            super.getActorStateManager().save().block();
            return Mono.just("Transaction successful");
        }
        return null;
    }
}
