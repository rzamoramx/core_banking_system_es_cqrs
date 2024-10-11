import json
from app.db.balance.BalanceModel import BalanceModel
from structlog import get_logger
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.MongoBase import MongoBase
from app.config.settings import MONGO_DB_NAME, MONGO_BALANCE_COLLECTION

logger = get_logger().bind(logger='BalanceRepository')


class BalanceRepository:
    _client: AsyncIOMotorClient = MongoBase.get_client()

    async def save(self, balance: BalanceModel):
        to_save = json.loads(balance.model_dump_json())
        logger.info('Saving balance', balance=balance)
        await BalanceRepository._client[MONGO_DB_NAME][MONGO_BALANCE_COLLECTION].insert_one(to_save)

    async def get(self, account_id: str) -> BalanceModel:
        logger.info('Retrieving balance', account_id=account_id)

        # Get last balance, order by updated_at field
        balance = await (BalanceRepository._client[MONGO_DB_NAME][MONGO_BALANCE_COLLECTION]
                         .find_one({'account_id': account_id}, sort=[('updated_at', -1)]))

        return BalanceModel(**balance) if balance else None

    async def get_history(self, account_id: str):
        logger.info('Retrieving balance history', account_id=account_id)

        # find all balances, order by updated_at field
        history = await (BalanceRepository._client[MONGO_DB_NAME][MONGO_BALANCE_COLLECTION]
                         .find({'account_id': account_id}).sort('updated_at', -1).to_list(length=None))

        return [BalanceModel(**balance) for balance in history]