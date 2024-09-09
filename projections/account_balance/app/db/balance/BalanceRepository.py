
from app.db.balance.BalanceModel import BalanceModel
from structlog import get_logger
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.MongoBase import MongoBase
from app.config.settings import MONGO_DB_NAME, MONGO_BALANCE_COLLECTION

logger = get_logger().bind(logger='BalanceRepository')


class BalanceRepository:
    _client: AsyncIOMotorClient = MongoBase.get_client()

    async def save(self, balance: BalanceModel):
        to_save = balance.model_dump()
        logger.info('Saving balance', balance=balance)
        await BalanceRepository._client[MONGO_DB_NAME][MONGO_BALANCE_COLLECTION].insert_one(to_save)

    async def get(self, account_id: str) -> BalanceModel:
        logger.info('Retrieving balance', account_id=account_id)
        balance = await (BalanceRepository._client[MONGO_DB_NAME][MONGO_BALANCE_COLLECTION]
                         .find_one({'account_id': account_id}))

        return BalanceModel.model_load(balance) if balance else None