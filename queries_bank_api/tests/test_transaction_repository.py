import asyncio
from datetime import datetime, timedelta
from com_ivansoft_corebank_lib.models.Transaction import Transaction as TransactionModel
import pytest
from app.config import settings
# for testing
settings.MONGO_DB_NAME = "test_db"

from app.db.transaction.TransactionRepository import TransactionRepository
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def mongodb_client():
    """Create a MongoDB client for the test."""
    client = AsyncIOMotorClient(settings.MONGO_URL)
    yield client
    await client.drop_database(settings.MONGO_DB_NAME)
    client.close()

@pytest.fixture(autouse=True)
async def setup_test_data(mongodb_client):
    collection = mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_TRANSACTION_COLLECTION]

    # Create test transactions with different timestamps
    base_time = datetime.now()
    test_transactions = [
        {
            "id": "tx123",
            "account_id": "123",
            "amount": 1000.0,
            "type": "DEPOSIT",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "status": "PENDING",
            "description": "Deposit of $1000",
            "version": 1
        },
        {
            "id": "tx124",
            "account_id": "123",
            "amount": 1500.0,
            "type": "DEPOSIT",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "status": "PENDING",
            "description": "Deposit of $1500",
            "version": 1
        },
        {
            "id": "tx125",
            "account_id": "123",
            "amount": 1300.0,
            "type": "WITHDRAWAL",
            "timestamp": base_time.isoformat(),
            "status": "PENDING",
            "description": "Withdrawal of $1300",
            "version": 1
        }
    ]

    # Insert test data
    await collection.insert_many(test_transactions)

    yield

@pytest.fixture
async def transaction_repository(mongodb_client):
    repo = TransactionRepository()
    repo.client = mongodb_client  # Ensure we use the test client
    yield repo
    # Clean up
    await mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_TRANSACTION_COLLECTION].drop()

@pytest.mark.asyncio
async def test_get_history_success(transaction_repository):
    result = await transaction_repository.get_history("123")
    
    assert len(result) == 3
    assert all(isinstance(item, TransactionModel) for item in result)
    
    # Verify first transaction (oldest)
    assert result[0].account_id == "123"
    assert result[0].amount == 1000.0
    assert result[0].type == "DEPOSIT"
    
    # Verify second transaction
    assert result[1].account_id == "123"
    assert result[1].amount == 1500.0
    assert result[1].type == "DEPOSIT"
    
    # Verify third transaction (newest)
    assert result[2].account_id == "123"
    assert result[2].amount == 1300.0
    assert result[2].type == "WITHDRAWAL"

@pytest.mark.asyncio
async def test_get_history_empty(transaction_repository):
    result = await transaction_repository.get_history("12345678901234")
    assert result is None
