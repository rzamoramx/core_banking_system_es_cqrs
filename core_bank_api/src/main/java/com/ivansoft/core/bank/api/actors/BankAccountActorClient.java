package com.ivansoft.core.bank.api.actors;

import com.ivansoft.core.bank.account.models.TransactionType;
import io.dapr.actors.ActorId;
import io.dapr.actors.client.ActorClient;
import io.dapr.actors.client.ActorProxyBuilder;

import java.util.logging.Logger;

public class BankAccountActorClient {
    private static final Logger log = Logger.getLogger(BankAccountActorClient.class.getName());

    public String doTransaction(String accountId, TransactionType type, Double amount) {
        log.info(String.format("Creating transaction for account %s with type %s and amount %f", accountId, type != null ? type.toString() : "null", amount != null ? amount : 0.0));

        try (ActorClient client = createActorClient()) {
            ActorProxyBuilder<BankAccountActor> builder = new ActorProxyBuilder<>(BankAccountActor.class, client);
            ActorId actorId = new ActorId(accountId);
            BankAccountActor bankAccountActor = builder.build(actorId);

            // todo: use reactor to handle async and avoid blocking
            return bankAccountActor.transaction(new TransactionDetails(type, amount)).block();
        } catch (Exception e) {
            log.severe("Error in doTransaction: " + e.getMessage());
            return e.getMessage();
        }
    }

    // Protected method to allow overriding in tests
    protected ActorClient createActorClient() {
        return new ActorClient();
    }
}
