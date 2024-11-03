import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from app.services.AccountService import AccountService
from com_ivansoft_corebank_lib.models.Transaction import Transaction, TransactionType
from com_ivansoft_corebank_lib.models.Balance import Balance as BalanceModel
from com_ivansoft_corebank_lib.models.User import User
from app.config import settings
# db for testing
settings.MONGO_DB_NAME = "testdb"

@pytest.fixture
def account_service():
    service = AccountService()
    # Mock repositories
    service.balance_repository = Mock()
    service.balance_repository.get = AsyncMock()
    service.balance_repository.save = AsyncMock()
    service.user_repository = Mock()
    service.history_transaction_repository = Mock()
    service.history_transaction_repository.save = AsyncMock()
    return service

@pytest.fixture
def mock_user():
    return User(user_id=1, username="testuser", account_id="acc123")

@pytest.fixture
def mock_balance():
    return BalanceModel(
        balance=Decimal("1000.0"),
        account_id="acc123",
        user_id=1,
        username="testuser",
        created_at=datetime.now().isoformat()
    )

@pytest.mark.asyncio
async def test_save_transaction(account_service):
    # Arrange
    transaction = Transaction(
        id="tx123",
        account_id="acc123",
        amount=100.0,
        type=TransactionType.DEPOSIT,
        status="PENDING",
        description="Deposit of $100",
        timestamp=datetime.now(),
        version=1,
    )

    # Act
    await account_service.save_transaction(transaction)

    # Assert
    account_service.history_transaction_repository.save.assert_called_once_with(transaction)

@pytest.mark.asyncio
async def test_update_balance_deposit(account_service, mock_user, mock_balance):
    # Arrange
    account_service.balance_repository.get.return_value = mock_balance
    account_service.user_repository.get_by_account_id.return_value = mock_user
    
    # Act
    await account_service.update_balance("acc123", Decimal("500.0"), TransactionType.DEPOSIT)

    # Assert
    account_service.balance_repository.save.assert_called_once()
    saved_balance = account_service.balance_repository.save.call_args[0][0]
    assert saved_balance.balance == Decimal("1500.0")
    assert saved_balance.account_id == "acc123"

@pytest.mark.asyncio
async def test_update_balance_withdraw(account_service, mock_user, mock_balance):
    # Arrange
    account_service.balance_repository.get.return_value = mock_balance
    account_service.user_repository.get_by_account_id.return_value = mock_user
    
    # Act
    await account_service.update_balance("acc123", Decimal("300.0"), TransactionType.WITHDRAW)

    # Assert
    account_service.balance_repository.save.assert_called_once()
    saved_balance = account_service.balance_repository.save.call_args[0][0]
    assert saved_balance.balance == Decimal("700.0")
    assert saved_balance.account_id == "acc123"
    assert saved_balance.user_id == 1

@pytest.mark.asyncio
async def test_update_balance_new_account(account_service, mock_user):
    # Arrange
    account_service.balance_repository.get.return_value = None
    account_service.user_repository.get_by_account_id.return_value = mock_user
    
    # Act
    await account_service.update_balance("acc123", Decimal("500.0"), TransactionType.DEPOSIT)

    # Assert
    account_service.balance_repository.save.assert_called_once()
    saved_balance = account_service.balance_repository.save.call_args[0][0]
    assert saved_balance.balance == Decimal("500.0")
    assert saved_balance.account_id == "acc123"
    assert saved_balance.user_id == 1
    assert saved_balance.updated_at is None

@pytest.mark.asyncio
async def test_update_balance_invalid_user(account_service):
    # Arrange
    account_service.user_repository.get_by_account_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="User for account acc123 not found"):
        await account_service.update_balance("acc123", Decimal("500.0"), TransactionType.DEPOSIT)

@pytest.mark.asyncio
async def test_update_balance_invalid_transaction_type(account_service, mock_user, mock_balance):
    # Arrange
    account_service.balance_repository.get.return_value = mock_balance
    account_service.user_repository.get_by_account_id.return_value = mock_user
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid transaction type"):
        await account_service.update_balance("acc123", Decimal("500.0"), "INVALID_TYPE")
