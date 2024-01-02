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
            log.info("actor id: " + accountId);
            ActorId actorId = new ActorId(accountId);
            log.info("building actor: " + actorId);
            BankAccountActor bankAccountActor = builder.build(actorId);
            log.info("actor built: " + bankAccountActor.toString());
            var result = bankAccountActor.transaction(new TransactionDetails(type, amount)).block();
            if (result == null) {
                return "Transaction return null";
            } else if (result == 0) {
                return "Transaction successful";
            } else if (result == 1) {
                return "Invalid transaction type";
            } else if (result == 2) {
                return "Insufficient funds";
            } else if (result == 3) {
                return "Invalid amount";
            } else return String.format("Unknown error: %d", result);
        } catch (Exception e) {
            return e.getMessage();
        }
    }
}
