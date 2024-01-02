package com.ivansoft.java.core.bank.api.actors;

import io.dapr.actors.ActorMethod;
import io.dapr.actors.ActorType;
import reactor.core.publisher.Mono;


@ActorType(name = "BankAccountActor")
public interface BankAccountActor {
    @ActorMethod(name = "transaction", returns = Integer.class)
    Mono<Integer> transaction(TransactionDetails transactionDetails);
}
