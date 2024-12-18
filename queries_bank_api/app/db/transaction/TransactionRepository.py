
from com_ivansoft_corebank_lib.models.Transaction import Transaction as TransactionModel
from structlog import get_logger
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.MongoBase import MongoBase
from app.config.settings import MONGO_DB_NAME, MONGO_TRANSACTION_COLLECTION

logger = get_logger().bind(logger='TransactionRepository')


class TransactionRepository:
    _client: AsyncIOMotorClient = MongoBase.get_client()

    async def get(self, account_id: str) -> TransactionModel:
        logger.info('Retrieving transaction', account_id=account_id)

        # Get last balance, order by updated_at field
        transaction = await (TransactionRepository._client[MONGO_DB_NAME][MONGO_TRANSACTION_COLLECTION]
                         .find_one({'account_id': account_id}, sort=[('updated_at', -1)]))

        return TransactionModel(**transaction) if transaction else None

    async def get_history(self, account_id: str):
        logger.info('Retrieving transaction history', account_id=account_id)

        # find all balances, order by updated_at field
        history = await (TransactionRepository._client[MONGO_DB_NAME][MONGO_TRANSACTION_COLLECTION]
                         .find({'account_id': account_id}).sort('updated_at', -1).to_list(length=None))

        if not history:
            return None

        return [TransactionModel(**transaction) for transaction in history]