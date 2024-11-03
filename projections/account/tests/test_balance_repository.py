import pytest
from datetime import datetime
from decimal import Decimal
from app.config import settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
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

@pytest.fixture
async def balance_repository(mongodb_client):
    """Create a balance repository instance."""
    repo = BalanceRepository()
    repo.client = mongodb_client  # Ensure we use the test client
    yield repo
    # Clean up
    await mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_BALANCE_COLLECTION].drop()

@pytest.fixture
def sample_balance():
    return BalanceModel(
        account_id="test_account_123",
        balance=Decimal("1000.00"),
        currency="MXN",
        user_id=456,  # Integer user_id
        username="testuser",
        created_at=datetime.now().isoformat()
    )

@pytest.mark.asyncio
async def test_save_balance_success(balance_repository, sample_balance):
    # Act
    await balance_repository.save(sample_balance)

    # Assert - Verify we can retrieve the saved balance
    saved_balance = await balance_repository.get(sample_balance.account_id)
    assert saved_balance is not None
    assert saved_balance.account_id == sample_balance.account_id
    assert saved_balance.balance == sample_balance.balance
    assert saved_balance.user_id == sample_balance.user_id
    assert saved_balance.username == sample_balance.username
    assert saved_balance.currency == "MXN"

@pytest.mark.asyncio
async def test_get_nonexistent_balance(balance_repository):
    # Act
    balance = await balance_repository.get("nonexistent_account")

    # Assert
    assert balance is None

@pytest.mark.asyncio
async def test_update_existing_balance(balance_repository, sample_balance):
    # Arrange
    await balance_repository.save(sample_balance)
    
    # Update the balance
    updated_balance = BalanceModel(
        account_id=sample_balance.account_id,
        balance=Decimal("2000.00"),
        currency="MXN",
        user_id=sample_balance.user_id,
        username=sample_balance.username,
        created_at=sample_balance.created_at,
        updated_at=datetime.now().isoformat()
    )

    # Act
    await balance_repository.save(updated_balance)

    # Assert
    retrieved_balance = await balance_repository.get(sample_balance.account_id)
    assert retrieved_balance is not None
    assert retrieved_balance.balance == Decimal("2000.00")
    assert retrieved_balance.updated_at is not None

@pytest.mark.asyncio
async def test_save_balance_with_decimal_precision(balance_repository):
    # Arrange
    balance = BalanceModel(
        account_id="test_precision_account",
        balance=Decimal("1000.45"),  # Test decimal precision
        currency="MXN",
        user_id=789,
        username="precisionuser",
        created_at=datetime.now().isoformat()
    )

    # Act
    await balance_repository.save(balance)

    # Assert
    saved_balance = await balance_repository.get(balance.account_id)
    assert saved_balance is not None
    assert saved_balance.balance == Decimal("1000.45")
    assert isinstance(saved_balance.balance, Decimal)

@pytest.mark.asyncio
async def test_save_multiple_balances(balance_repository):
    # Arrange
    balances = [
        BalanceModel(
            account_id=f"test_account_{i}",
            balance=Decimal(f"{i}000.00"),
            currency="MXN",
            user_id=i,  # Integer user_id
            username=f"testuser_{i}",
            created_at=datetime.now().isoformat()
        )
        for i in range(1, 4)  # Starting from 1 to avoid user_id 0
    ]

    # Act
    for balance in balances:
        await balance_repository.save(balance)

    # Assert
    for balance in balances:
        saved_balance = await balance_repository.get(balance.account_id)
        assert saved_balance is not None
        assert saved_balance.account_id == balance.account_id
        assert saved_balance.balance == balance.balance
        assert isinstance(saved_balance.user_id, int)

@pytest.mark.asyncio
async def test_invalid_user_id_type():
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        BalanceModel(
            account_id="test_account",
            balance=Decimal("1000.00"),
            currency="MXN",
            user_id="invalid_string_id",  # This should raise an error
            username="testuser",
            created_at=datetime.now().isoformat()
        )
