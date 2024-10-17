# Core bank API Rest Service #

This is the API rest for the core bank operations (Deposits and Withdrawals) implementing the CQRS pattern where each operation is a command.

Each command is orignated from a HTTP POST request to this API and it is sent to the account aggregate (Dapr Actor) that processes the operation, evaluates business rules and generates events that are published to the event source.

## Prerequisites ##

Read global README prerequisites [here](../README.md#prerequisites).

## Installation ##

Read global README installation [here](../README.md#installation).

## Building the project ##

To build the project, locate into root_project/core_bank_api directory and execute the following command:

```bash
mvn clean package
```

## Running the project ##

Locate into root_project/core_bank_api in a terminal and execute the following command:

```bash
dapr run --app-id corebankapi --app-protocol http --app-port 8081 -- java -jar target/api-0.0.1-SNAPSHOT.jar
```