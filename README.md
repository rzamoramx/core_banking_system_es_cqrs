# core_banking_system_es_cqrs

An experimental core banking system using Event Sourcing (ES) and Command Query Responsibility Segregation (CQRS) using Dapr, Python, Java, and Go.

## Table of Contents

- Overview
- Architecture
    - Logical Architecture
    - Physical Architecture
- Project Structure
- Getting Started
    - Prerequisites
    - Installation
- Usage
- Technologies Used
- Contributing
- License
- Acknowledgments

## Overview ##
> **_NOTE:_** This project is inspired by the blog series [A Core banking System Architecture](https://sites.google.com/view/rodrigozamora/blog/arquitectura-para-un-core-banking-system?authuser=0) (in Spanish).

This project demonstrates a simple core banking system that implements Event Sourcing, CQRS, Aggregates, and Projections patterns. It handles basic bank account operations such as deposits and withdrawals, exposing two REST APIs: one for commands and another for queries.
The system is built on Dapr (Distributed Application Runtime), showcasing how to leverage its components for building robust, scalable microservices.

For Dapr's official documentation
 [read here](https://docs.dapr.io/concepts/overview/) is neccesary to understand the whole project.

## Architecture ##

### Logical architecture ###

The system comprises the following high-level components:

- Commands: Utilizes the Aggregate pattern for deposit and withdrawal operations, ensuring write consistency with each bank account as an individual aggregate.
- Queries: Implements the Projection pattern to create "views" of bank account operations, stored separately from the write model.
- Event Source: Acts as a middleware between commands and queries, receiving events from aggregates and publishing them to consumers (Projections).
- APIs: Separate APIs for account operations (commands) and reading projections (queries).

TODO: [image]

### Physical architecture ###

The system is composed of the following components:

- Core Bank API (Java, Spring Boot): REST API for triggering command operations.
- Bank Account Actor (Java, Spring Boot): Processes bank account operations atomically using Dapr's Actor building block.
- Event Source (Go, Gorilla/mux): Handles system events using Dapr's pubsub building block and stores event logs in ImmuDB.
- Account Projections (Python, FastAPI): Processes bank account events to generate views (balance and transaction history).
- Queries API (Python, FastAPI): Serves read requests for projections.

TODO: [image]

## Project structure ##

```
core_banking_system_es_cqrs/
├── aggregates/           # Bank account actor (Java)
├── core_bank_api/        # Command API (Java)
├── es/                   # Event Source (Go)
├── libraries/            # Shared code for Java and Python projects
├── projections/
│   └── account/          # Account projections (Python)
└── queries_bank_api/     # Query API (Python)
```

## Getting started ##

### Prerequisites ###

- An IDE for Java with Maven (I suggests IntelliJ IDEA)
- Git
- Docker 27.2.0 (Docker desktop for Windows)
- Dapr 1.14.4 - Follow the instructions in the official documentation [here](https://docs.dapr.io/getting-started/install-dapr-cli/)
- Java 21
- Python 3.12
- Go 1.23
- Poetry 1.7.1 - Follow the instructions in the official documentation [here](https://python-poetry.org/docs/#installation)
- immudbclient and immudbadmin binaries from [here] (https://github.com/codenotary/immudb/releases)

### Installation ###

1- Clone the repository:

```bash
git clone https://github.com/rzamoramx/core_banking_system_es_cqrs.git
cd core_banking_system_es_cqrs
```

2- Setup docker containers:

```bash
docker run -d --name mongodb-container -p 27017:27017 mongo
docker run -d -it --name immudb -p 3322:3322 -p 9497:9497 codenotary/immudb:latest
```

3- Configure Dapr components:

Disable all other components in the Dapr runtime, you can do it by changing its file names in the "components" folder (normally it is installed under .dapr directory in the user home path), for example, change pubsub.yaml to pubsub.yaml.disabled and then create the following files:

evensource.yaml
``` yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: eventsource
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

statestore.yaml
``` yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

4- Setup immudb:

You'll need the immuadmin and immuclient binaries, the commands are the same in Linux, Windows, and MacOS.

``` bash
./immuadmin login immudb
... follow the instructions to change the password
./immuadmin database create eventsourcedb
./immuclient use eventstoredb
```

5- Follow the README instructions in each project subdirectory to set up and run individual components.


## Usage ##

Once all components are up and running, you can perform the following operations:

1- Start a command operation by sending a POST request to the Core Bank API:

2- Check the account balance by sending a GET request to the Queries API:

3- Check the account transaction history by sending a GET request to the Queries API:

## Technologies Used ##

- Dapr
- Spring Boot
- FastAPI
- Gorilla/mux
- MongoDB
- ImmuDB

## Contributing ##

Contributions are welcome! Please feel free to submit a Pull Request.

## License ##

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments ##

- The Dapr community for their amazing work on building a powerful runtime for microservices.
