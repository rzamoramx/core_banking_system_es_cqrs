# Account aggregate #

This is the aggreate that handles account operations (Deposits and Withdrawals) implementing the aggregate pattern where each account is an individual aggregate.

This aggregate is implemented as a Dapr Actor, which allows for atomic operations on a single account. It can be considered as a unit computation that can be executed in a distributed environment.

You can read Dapr's actor building block overview [here](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/).

Each account operation (command origanated from core bank api rest) the aggregate will evaluate business rules and generates events that are published to the event source.

## Prerequisites ##

Read global README prerequisites [here](../README.md#prerequisites).

## Installation ##

Read global README installation [here](../README.md#installation).

## Building the project ##

To build the project, locate into root_project/aggregates directory and execute the following command:

```bash
mvn clean package
```

## Running the project ##

Locate into root_project/aggregates in a terminal and execute the following command:

```bash
dapr run --app-id bankaccountactorservice --app-port 3000 -- java -jar target/bank_account_aggregate-0.0.1-SNAPSHOT.jar com.ivansoft.java.core.bank.aggregates.BankAccountActorService -p 3000
```
