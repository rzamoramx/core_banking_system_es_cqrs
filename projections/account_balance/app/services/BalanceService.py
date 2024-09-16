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

    async def get_balance(self, account_id: str) -> BalanceModel:
        balance = await self.balance_repository.get(account_id)
        if not balance:
            raise ValueError(f'Balance for account {account_id} not found')
        return balance

    async def update_balance(self, account_id: str, amount: Decimal, transaction_type: TransactionType):
        # retrieve previous balance of this account
        previous_balance = await self.balance_repository.get(account_id)

        # we can retrieve data from other collections here, this is not implemented in this example
        user = self.user_repository.get_by_account_id(account_id)

        if not user:
            raise ValueError(f'User for account {account_id} not found')

        balance = BalanceModel(balance=amount,
                               account_id=account_id,
                               user_id=user.user_id,
                               username=user.username)
        # TODO check why this is not working
        if not previous_balance:
            # set the created_at time, this is the first time this account is being updated
            balance.created_at = datetime.now()
        else:
            # set the created_at time to the previous balance created_at
            balance.updated_at = datetime.now()

        if transaction_type == TransactionType.DEPOSIT:
            balance.balance += previous_balance.balance
        elif transaction_type == TransactionType.WITHDRAW:
            balance.balance -= previous_balance.balance

        # update the balance in the database
        await self.balance_repository.save(balance)