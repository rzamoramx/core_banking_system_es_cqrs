
from app.db.balance.BalanceRepository import BalanceRepository, BalanceModel
from app.db.transaction.TransactionRepository import TransactionRepository
from structlog import get_logger

logger = get_logger().bind(logger='BalanceService')


class AccountService:
    def __init__(self):
        self.balance_repository = BalanceRepository()
        self.transaction_repository = TransactionRepository()

    async def get_history_transactions(self, account_id: str):
        try:
            history = await self.transaction_repository.get_history(account_id)
        except Exception as e:
            logger.error('Error getting history transactions', account_id=account_id, error=str(e))
            raise ValueError('Exception')
        if not history:
            raise ValueError('Not Found')
        return history

    async def get_current_balance(self, account_id: str) -> BalanceModel:
        balance = await self.balance_repository.get(account_id)
        if not balance:
            raise ValueError('Not Found')
        return balance