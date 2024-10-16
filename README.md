# core_banking_system_es_cqrs

An experimental core banking system using ES/CQRS architecture built on Dapr, using Python, Java and Go programming 
languages.

## Context ##

This is a practical approach of a blog serial posts here: 
[A Core banking System Architecture](https://sites.google.com/view/rodrigozamora/blog/arquitectura-para-un-core-banking-system?authuser=0) (Spanish) is not necessary to read it before to understand this example.

## Overview ##

The system is a simple core bank system that implementes Event Source, CQRS, Aggreates and Projections patterns, this handle
very basic bank account operations, deposits and withdrawals, for that this system exposes two API rests, one for commands
and other for reads (queries).

This system was built on Dapr (a distributed applications runtime). For official documentation
 [read here](https://docs.dapr.io/concepts/overview/) is neccesary to understand the whole project.

## Logical architecture ##

Main high level componentes in the system:

- Commands: using aggregates pattern for deposits and withdrawals operations to ensure write consistency in which every 
bank account is an aggregate that have its own store.

- Queries: using projetions pattern to create "views" of operations ocours in the bank accounts, also they have its own 
stores. We have two projections for this example, balance and history transactions.

- Event source: In middle of them (commands and queries) we have an Event Source that recives events produced from 
aggregates and publish it to consumers (Projections). Also it store event in its own inmutable store (append only)

- APIs: And API for create operations on bank accounts (commands) and APIs for read projections (queries)

TODO: [image]

## Physical architecture ##

The components that participates in the system are:

- An API Rest for trigger commands (deposits and withdrawals) operations on bank accounts, called "core bank api", written
 in Java and using spring boot framework. 

- An Aggregate for process bank account operations in a isolated and atomic manner, called "bank account actor", written in
 Java with SpringBoot, this is invoked by "core bank api". It's built using a Dapr's component called Actor and also 
 uses a Dapr's State store component to save account state.

- An Event source for handle events in the system (bank account operations) that uses Dapr's component called pubsub, also 
uses ImmuDB as immutable database to store events log, this was written in Go with Gorilla/mux.

- Account projections called "account" for process bank account operations (events that comes from ES) and generates 
views (interpretation of events), there are two of them, balance and history transactions and stores its data in its own
store (mongo collection) it was written in Python with FastAPI.

- A Queries API Rest for serve reads to projections (balance and history transactions), it was written in Python with
FastAPI.

TODO: [image]

## Project structure ##

This is a monorepo that embraces multiple projects with differents languages and frameworks to demostrate flexibility of this
architecure and Dapr runtime.

- aggregates: there is the bank acocunt actor.
    - ... the typical spring boot project structure.
- core_bank_api: there is the API rest for commands.
    - ... the typical spring boot project structure.
- es: there is the event source.
    - ... Go project.
- libraries: there is a common code for Java and Python projects.
- projections: there is all projections, grouped by domain.
    - account: all projections related to bank accounts, in our use case, balance and history transactions.
        - ... typical FastAPI project.
- queries_bank_api: this is the API Rest to read projections
    - ... typical FastAPI project.

## Global dependencies ##

- Git 2.46.2
- Docker 27.2.0 (Docker desktop for Windows)
- Dapr 1.14.4 - Follow the instructions in the official documentation [here](https://docs.dapr.io/getting-started/install-dapr-cli/)
- Java 21
- Python 3.12
- Go 1.23
- Poetry 1.7.1 - Follow the instructions in the official documentation [here](https://python-poetry.org/docs/#installation)

## Docker images dependencies ##

- MongoDB 8.0.0 community - its recommended to use docker image, follow the instructions [here](https://hub.docker.com/_/mongo) for short you can use this: ```docker run -d --name mongodb-container -p 27017:27017 mongo```
- ImmuDB 1.9.5 - Follow the instructions in the official documentation [here](https://docs.immudb.io/master/running/download.html) please don't run with --rm flag, because you will lose all data neither --net host flag. For short you can use this: ```docker run -d -it --name immudb -p 3322:3322 -p 9497:9497 codenotary/immudb:latest```

## Prerequisites ##

Once you have installed all global dependencies and docker images, you'll need configure two Dapr components, one for pubsub and other for state store.