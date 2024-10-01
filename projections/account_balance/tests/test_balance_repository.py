import pytest
from app.db.balance.BalanceRepository import BalanceRepository
from app.db.balance.BalanceModel import BalanceModel


@pytest.mark.asyncio
async def test_save_balance_success():
    # Arrange
    balance = BalanceModel(account_id="123", balance=100.0, user_id="456", username="test")
    repo = BalanceRepository()

    # Act
    await repo.save(balance)

@pytest.mark.asyncio
async def test_get_balance_success():
    # Arrange
    account_id = "123"
    expected_balance = BalanceModel(account_id=account_id, balance=100.0, user_id="456", username="test")
    repo = BalanceRepository()

    # Act
    result = await repo.get(account_id)

    # Assert
    assert result == expected_balance

@pytest.mark.asyncio
async def test_get_balance_not_found():
    # Arrange
    account_id = "456"
    repo = BalanceRepository()

    # Act
    result = await repo.get(account_id)

    # Assert
    assert result is None