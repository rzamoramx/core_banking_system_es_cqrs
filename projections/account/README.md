# Account Projections

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112-009688.svg)](https://fastapi.tiangolo.com/)
[![Dapr](https://img.shields.io/badge/Dapr-1.14.4-blue.svg)](https://dapr.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)

This service implements the Projection pattern for the Core Banking System, creating optimized read models from bank account events. It processes events broadcasted by the Event Source to maintain up-to-date views of account balances and transaction histories in MongoDB.

## 🏗️ Architecture

### Projection Implementation

The service maintains two primary projections:

- **Balance Projection**: Real-time account balance calculations
- **Transaction History**: Chronological record of all account operations

### Event Flow

```mermaid
graph LR
    A[Event Source] --> B[Projections Service]
    B --> C[Balance View]
    B --> D[Transaction History]
    C --> E[MongoDB]
    D --> E
    style B fill:#f9f,stroke:#333,stroke-width:4px
```

## 🚀 Setup

### Prerequisites

1. **Verify Python Installation**
   ```bash
   python --version  # Should be 3.12 or higher
   poetry --version # Should be 2.1.3 or higher
   ```
   Also you must have installed library located in `core_banking_system_es_cqrs/libraries/python/com-ivansoft-corebank-lib`
   Check the [README](../../README.md) for installation instructions.


2. **Verify MongoDB**
   ```bash
   mongosh --version
   ```

### Installation

1. **Navigate to Project Directory**
   ```bash
   cd core_banking_system_es_cqrs/projections/account
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Verify MongoDB Collections**
   
   Ensure the following collections exist in the `mydb` database:
   - `balance`
   - `transactions`

## 🏃‍♂️ Running the Service

### Docker Mode

You can build and run this component using Docker individually. Since it relies on the shared Python library, it must be built from the root of the repository:

```bash
cd ../../ # Go to the root of the repository
docker build -t mybank/projections -f projections/account/Dockerfile .
docker run -p 8000:8000 mybank/projections
```

> **_NOTE:_** Running the component individually via Docker will not connect it to Dapr automatically. Use Docker Compose from the root directory to run the full Dapr mesh.

### Development Mode

```bash
dapr run \
    --app-id accountprojections \
    --app-port 8000 \
    -- poetry run uvicorn app.main:app --port 8000
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--app-id` | Unique identifier for the service | `accountprojections` |
| `--app-port` | Port for the service to listen on | `8000` |
| `--port` | Application port (must match app-port) | `8000` |

## 💡 Implementation Details

### Event Handlers

The service subscribes to and processes the following events:
- `Deposit`: Updates balance and records transaction
- `Withdrawal`: Updates balance and records transaction

### MongoDB Schema

#### Balance Collection
```json
{
  "_id": ObjectId,
  "balance": String,
  "currency": String,
  "user_id": Integer,
  "username": String,
  "account_id": String,
  "created_at": DateTime,
  "updated_at": DateTime
}
```

#### Transactions Collection
```json
{
  "_id": ObjectId,
  "id": String,
  "account_id": String,
  "amount": Decimal,
  "type": String,
  "status": String,
  "description": String,
  "timestamp": DateTime,
  "version": Integer
}
```

## 🐛 Troubleshooting

Common issues and solutions:

1. **Event Processing Issues**
   ```bash
   dapr logs --app-id accountprojections
   ```

2. **MongoDB Connection Problems**
   - Verify MongoDB is running:
     ```bash
     docker ps | grep mongodb
     ```
   - Check MongoDB logs:
     ```bash
     docker logs mongodb-container
     ```

3. **Common Error Messages**

   | Error | Solution |
   |-------|----------|
   | `MongoDB connection failed` | Check MongoDB container status and credentials |
   | `Event subscription failed` | Verify Dapr pubsub component configuration |
   | `Projection update failed` | Check MongoDB write permissions |

## 📊 Monitoring

The service exposes the following metrics endpoints:

- [TODO]`/metrics`: Some metrics about the service
- [TODO]`/health`: Service health check

## 🔗 Related Components

- [Core Bank API](../../core_bank_api/README.md)
- [Bank Account Actor](../../aggregates/README.md)
- [Event Source](../../es/README.md)
- [Queries Bank API](../../queries_bank_api/README.md)

## 🛠️ Development

### Project Structure

```
account/
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── projections/      # Projection implementations
│   │   ├── balance.py    # Balance projection
│   │   └── history.py    # Transaction history projection
│   └── config.py         # Configuration management
├── tests/                # Unit and integration tests
├── poetry.lock          # Dependency lock file
└── pyproject.toml       # Project configuration
```

### Running Tests

[TODO] Add tests for projections

```bash
poetry run pytest
```