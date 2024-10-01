from datetime import datetime
from com_ivansoft_corebank_lib.models.Transaction import TransactionType
from app.db.balance.BalanceRepository import BalanceRepository, BalanceModel
from app.db.user.UserRepository import UserRepository
from decimal import Decimal
from structlog import get_logger

logger = get_logger().bind(logger='BalanceService')


class BalanceService:
    def __init__(self):
        self.balance_repository = BalanceRepository()
        self.user_repository = UserRepository()

    async def get_history_balance(self, account_id: str):
        history = await self.balance_repository.get_history(account_id)
        return history

    async def get_current_balance(self, account_id: str) -> BalanceModel:
        balance = await self.balance_repository.get(account_id)
        if not balance:
            raise ValueError(f'Balance for account {account_id} not found')
        return balance

    async def update_balance(self, account_id: str, amount: Decimal, transaction_type: TransactionType):
        previous_balance = await self.balance_repository.get(account_id)
        user = self._get_user_by_account_id(account_id)

        logger.info('previous_balance', previous_balance=previous_balance)

        balance = self._create_balance_model(account_id, amount, user, previous_balance, transaction_type)
        logger.info('New balance', balance=balance)

        await self.balance_repository.save(balance)

    def _get_user_by_account_id(self, account_id: str):
        user = self.user_repository.get_by_account_id(account_id)
        if not user:
            raise ValueError(f'User for account {account_id} not found')
        return user

    def _create_balance_model(self, account_id: str, amount: Decimal, user, previous_balance, transaction_type: TransactionType) -> BalanceModel:
        balance = BalanceModel(
            balance=amount,
            account_id=account_id,
            user_id=user.user_id,
            username=user.username,
            created_at=previous_balance.created_at if previous_balance else datetime.now().isoformat(),
            updated_at=datetime.now().isoformat() if previous_balance else None
        )

        if previous_balance:
            balance.balance = self._calculate_new_balance(previous_balance.balance, amount, transaction_type)
        return balance

    def _calculate_new_balance(self, previous_amount: Decimal, amount: Decimal, transaction_type: TransactionType) -> Decimal:
        if transaction_type == TransactionType.DEPOSIT:
            return previous_amount + amount
        elif transaction_type == TransactionType.WITHDRAW:
            return previous_amount - amount
        else:
            raise ValueError(f'Invalid transaction type: {transaction_type}')