import pytest
from unittest.mock import Mock
from app.services.AccountService import AccountService
from app.db.balance.BalanceRepository import BalanceRepository
from app.db.transaction.TransactionRepository import TransactionRepository
from com_ivansoft_corebank_lib.models.Balance import Balance as BalanceModel

@pytest.fixture
def mock_balance_repo():
    return Mock(spec=BalanceRepository)

@pytest.fixture
def mock_transaction_repo():
    return Mock(spec=TransactionRepository)

@pytest.fixture
def account_service(mock_balance_repo, mock_transaction_repo):
    service = AccountService()
    service.balance_repository = mock_balance_repo
    service.transaction_repository = mock_transaction_repo
    return service

@pytest.mark.asyncio
async def test_get_current_balance_success(account_service, mock_balance_repo):
    mock_balance = BalanceModel(
        account_id="123",
        balance=1000.0,
        user_id=456,
        username="test_user"
    )
    mock_balance_repo.get.return_value = mock_balance
    
    result = await account_service.get_current_balance("123")
    assert result == mock_balance
    mock_balance_repo.get.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_get_current_balance_not_found(account_service, mock_balance_repo):
    mock_balance_repo.get.return_value = None
    
    with pytest.raises(ValueError, match='Not Found'):
        await account_service.get_current_balance("999")
    mock_balance_repo.get.assert_called_once_with("999")

@pytest.mark.asyncio
async def test_get_history_transactions_success(account_service, mock_transaction_repo):
    mock_history = [
        BalanceModel(
            account_id="123",
            balance=1000.0,
            user_id="456",
            username="test_user"
        ),
        BalanceModel(
            account_id="123",
            balance=1100.0,
            user_id="456",
            username="test_user"
        )
    ]
    mock_transaction_repo.get_history.return_value = mock_history
    
    result = await account_service.get_history_transactions("123")
    assert result == mock_history
    mock_transaction_repo.get_history.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_get_history_transactions_error(account_service, mock_transaction_repo):
    mock_transaction_repo.get_history.side_effect = Exception("Database error")
    
    with pytest.raises(ValueError, match='Not Found'):
        await account_service.get_history_transactions("123")
    mock_transaction_repo.get_history.assert_called_once_with("123")
