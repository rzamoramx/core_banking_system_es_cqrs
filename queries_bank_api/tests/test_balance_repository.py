import asyncio
from decimal import Decimal
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
# for testing
settings.MONGO_DB_NAME = "testdb"

from app.db.balance.BalanceRepository import BalanceRepository
from com_ivansoft_corebank_lib.models.Balance import Balance as BalanceModel

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
async def setup_test_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URL)
    collection = client[settings.MONGO_DB_NAME][settings.MONGO_BALANCE_COLLECTION]

    # Create test balance data
    test_balance = {
        "account_id": "123",
        "balance": 100.0,
        "user_id": 456,
        "username": "test"
    }

    # Insert test data
    await collection.insert_one(test_balance)

    yield

    # Cleanup test data
    await collection.delete_many({"account_id": "123"})
    client.close()

@pytest.fixture
async def balance_repository(mongodb_client):
    """Create a balance repository instance."""
    repo = BalanceRepository()
    repo.client = mongodb_client
    yield repo
    # Clean up
    await mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_BALANCE_COLLECTION].drop()

@pytest.mark.asyncio
async def test_get_balance_success(balance_repository):
    # Arrange
    account_id = "123"
    expected_balance = BalanceModel(account_id=account_id, balance=Decimal("100.0"), user_id=456, username="test")

    # Act
    result = await balance_repository.get(account_id)

    # Assert
    assert result == expected_balance

@pytest.mark.asyncio
async def test_get_balance_not_found(balance_repository):
    # Arrange
    account_id = "4562313423581201920383241"

    # Act
    result = await balance_repository.get(account_id)

    # Assert
    assert result is None
