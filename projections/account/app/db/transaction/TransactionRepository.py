import json
from com_ivansoft_corebank_lib.models.Transaction import Transaction as TransactionModel
from structlog import get_logger
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.MongoBase import MongoBase
from app.config.settings import MONGO_DB_NAME, MONGO_TRANSACTION_COLLECTION

logger = get_logger().bind(logger='TransactionRepository')


class TransactionRepository:
    _client: AsyncIOMotorClient = MongoBase.get_client()

    async def save(self, transaction: TransactionModel):
        to_save = json.loads(transaction.model_dump_json())
        logger.info('Saving transaction', balance=transaction)
        await TransactionRepository._client[MONGO_DB_NAME][MONGO_TRANSACTION_COLLECTION].insert_one(to_save)