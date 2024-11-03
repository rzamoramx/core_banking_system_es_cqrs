import asyncio

import pytest
from datetime import datetime
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
# db for testing
settings.MONGO_DB_NAME = "testdb"

from app.db.transaction.TransactionRepository import TransactionRepository
from com_ivansoft_corebank_lib.models.Transaction import Transaction, TransactionType


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

@pytest.fixture(scope="function")
async def transaction_repository(mongodb_client):
    repo = TransactionRepository()
    repo.client = mongodb_client  # Ensure we use the test client
    yield repo
    # Clean up
    await mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_TRANSACTION_COLLECTION].drop()

@pytest.fixture
def sample_transaction():
    return Transaction(
        id="tx123",
        account_id="acc123",
        amount=100.0,
        type=TransactionType.DEPOSIT,
        status="PENDING",
        description="Deposit of $100",
        timestamp=datetime.now(),
        version=1,
    )

@pytest.mark.asyncio
async def test_save_transaction_success(transaction_repository, sample_transaction):
    # Act
    await transaction_repository.save(sample_transaction)

    # Assert - Verify transaction was saved by retrieving it
    transactions = await transaction_repository.get_by_account_id(sample_transaction.account_id)
    assert len(transactions) == 1
    saved_tx = transactions[0]
    assert saved_tx.id == sample_transaction.id
    assert saved_tx.account_id == sample_transaction.account_id
    assert Decimal(str(saved_tx.amount)) == Decimal(str(sample_transaction.amount))
    assert saved_tx.type == sample_transaction.type

@pytest.mark.asyncio
async def test_get_transactions_nonexistent_account(transaction_repository):
    # Act
    transactions = await transaction_repository.get_by_account_id("nonexistent_account")

    # Assert
    assert transactions == []

@pytest.mark.asyncio
async def test_save_multiple_transactions(transaction_repository):
    # Arrange
    transactions = [
        Transaction(
            id=f"tx_{i}",
            account_id="test_account_123",
            amount=float(i * 100),
            type=TransactionType.DEPOSIT if i % 2 == 0 else TransactionType.WITHDRAW,
            created_at=datetime.now().isoformat(),
            status="PENDING",
            description="Deposit of $100",
            timestamp=datetime.now(),
            version=1,
        )
        for i in range(1, 4)
    ]

    # Act
    for tx in transactions:
        await transaction_repository.save(tx)

    # Assert
    saved_transactions = await transaction_repository.get_by_account_id("test_account_123")
    assert len(saved_transactions) == 3
    
    # Verify all transactions were saved correctly
    saved_tx_ids = {tx.id for tx in saved_transactions}
    original_tx_ids = {tx.id for tx in transactions}
    assert saved_tx_ids == original_tx_ids

@pytest.mark.asyncio
async def test_save_transaction_with_decimal_precision(transaction_repository):
    # Arrange
    transaction = Transaction(
        id="tx_precision",
        account_id="test_account_123",
        amount=1000.45,  # Test decimal precision
        type=TransactionType.DEPOSIT,
        created_at=datetime.now().isoformat(),
        status="PENDING",
        description="Deposit of $100",
        timestamp=datetime.now(),
        version=1,
    )

    # Act
    await transaction_repository.save(transaction)

    # Assert
    saved_transactions = await transaction_repository.get_by_account_id(transaction.account_id)
    assert len(saved_transactions) == 1
    saved_tx = saved_transactions[0]
    assert Decimal(str(saved_tx.amount)) == Decimal("1000.45")

@pytest.mark.asyncio
async def test_save_transactions_different_accounts(transaction_repository):
    # Arrange
    transactions = [
        Transaction(
            id=f"tx_{i}",
            account_id=f"account_{i}",
            amount=1000.00,
            type=TransactionType.DEPOSIT,
            created_at=datetime.now().isoformat(),
            status="PENDING",
            description="Deposit of $100",
            timestamp=datetime.now(),
            version=1,
        )
        for i in range(3)
    ]

    # Act
    for tx in transactions:
        await transaction_repository.save(tx)

    # Assert
    for tx in transactions:
        saved_transactions = await transaction_repository.get_by_account_id(tx.account_id)
        assert len(saved_transactions) == 1
        saved_tx = saved_transactions[0]
        assert saved_tx.id == tx.id
        assert saved_tx.account_id == tx.account_id

@pytest.mark.asyncio
async def test_transaction_types(transaction_repository):
    # Arrange
    account_id = "test_account_types"
    transactions = [
        Transaction(
            id=f"tx_deposit_{i}",
            account_id=account_id,
            amount=1000.00,
            type=tx_type,
            created_at=datetime.now().isoformat(),
            status="PENDING",
            description="Deposit of $100",
            timestamp=datetime.now(),
            version=1,
        )
        for i, tx_type in enumerate([TransactionType.DEPOSIT, TransactionType.WITHDRAW])
    ]

    # Act
    for tx in transactions:
        await transaction_repository.save(tx)

    # Assert
    saved_transactions = await transaction_repository.get_by_account_id(account_id)
    assert len(saved_transactions) == 2
    
    # Verify we have both types of transactions
    saved_types = {tx.type for tx in saved_transactions}
    assert saved_types == {TransactionType.DEPOSIT, TransactionType.WITHDRAW}
