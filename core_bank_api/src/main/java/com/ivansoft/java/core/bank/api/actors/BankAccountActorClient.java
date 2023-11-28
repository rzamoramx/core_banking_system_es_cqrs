package com.ivansoft.java.core.bank.api.actors;

import com.ivansoft.java.core.bank.api.models.TransactionType;
import io.dapr.actors.ActorId;
import io.dapr.actors.client.ActorClient;
import io.dapr.actors.client.ActorProxyBuilder;

import java.util.logging.Logger;


public class BankAccountActorClient {
    private static final Logger log = Logger.getLogger(BankAccountActorClient.class.getName());

    public String doTransaction(String accountId, TransactionType type, Double amount) {
        log.info(String.format("Creating transaction for account %s with type %s and amount %f", accountId, type.toString(), amount));

        try (ActorClient client = new ActorClient()) {
            ActorProxyBuilder<BankAccountActor> builder = new ActorProxyBuilder<>(BankAccountActor.class, client);
            ActorId actorId = new ActorId(accountId);
            BankAccountActor bankAccountActor = builder.build(actorId);

            return bankAccountActor.transaction(new TransactionDetails(type, amount)).block();
        } catch (Exception e) {
            return e.getMessage();
        }
    }
}
