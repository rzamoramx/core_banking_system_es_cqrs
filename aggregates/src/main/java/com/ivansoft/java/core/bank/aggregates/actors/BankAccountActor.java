package com.ivansoft.java.core.bank.aggregates.actors;

import io.dapr.actors.ActorMethod;
import io.dapr.actors.ActorType;
import reactor.core.publisher.Mono;


@ActorType(name = "bankaccount")
public interface BankAccountActor {
    @ActorMethod(name = "transaction", returns = String.class)
    Mono<String> transaction(TransactionDetails transactionDetails);
}
