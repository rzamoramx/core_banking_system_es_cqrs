
from motor.motor_asyncio import AsyncIOMotorClient
from structlog import get_logger
from app.config.settings import MONGO_URL

logger = get_logger().bind(logger='MongoBase')


class MongoBase:
    _client: AsyncIOMotorClient = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if not cls._client:
            cls.connect()
        return cls._client

    @classmethod
    def connect(cls):
        logger.info('Connecting to MongoDB')
        cls._client = AsyncIOMotorClient(MONGO_URL)

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info('MongoDB connection closed')
        else:
            logger.warning('MongoDB connection already closed')
