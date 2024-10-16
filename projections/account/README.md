# Core banking system rest API for clients like mobile apps #

According to CQRS pattern, this API handle event source messages (transactions) and process 
them according to balance and transactions history projections.

Each projection saves the data in its own store

## Dependencies ##

- Python 3.12
- poetry 1.7.1
- docker 27.2.0
- dapr 1.14

## Setup ##

Run this command to install dependencies:

```poetry install```

## Run ##

```bash
dapr run --app-id accountprojections --app-port 8000 -- poetry run uvicorn app.main:app --port 8000
```