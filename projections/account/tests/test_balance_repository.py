import pytest
from app.db.balance.BalanceRepository import BalanceRepository
from com_ivansoft_corebank_lib.models.Balance import Balance as BalanceModel


@pytest.mark.asyncio
async def test_save_balance_success():
    # Arrange
    balance = BalanceModel(account_id="123", balance=100.0, user_id="456", username="test")
    repo = BalanceRepository()

    # Act
    await repo.save(balance)