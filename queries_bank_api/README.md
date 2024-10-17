# queries bank API #

This project implements a Rest API for queries to projections, in this case queries to the account balance and transaction history projections.

This makes reads to mongodb collections where the data is stored by the account and transaction history projections (projections/account).

## Prerequisites ##

Read global README prerequisites [here](../../README.md#prerequisites).

## Installation ##

Read global README installation [here](../../README.md#installation).

Also you will need to install dependencies for the project:

```bash
poetry install
```

## Running the project ##

Locate into root_project/queries_bank_api in a terminal and execute the following command:

```bash
dapr run --app-id queriesbankapi --app-port 8003 -- poetry run uvicorn app.main:app --port 8003
```
