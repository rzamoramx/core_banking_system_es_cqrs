import asyncio
from datetime import timedelta, datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
# for testing
settings.MONGO_DB_NAME = "testdb"
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.AccountService import AccountService
from unittest.mock import Mock, patch

client = TestClient(app)

# TODO: fix event loop is closed
@pytest.fixture(scope="session") # function
def event_loop():
    #Create an instance of the default event loop for the test session.
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def mongodb_client(event_loop):
    """Create a MongoDB client for the test."""
    dbclient = AsyncIOMotorClient(settings.MONGO_URL)
    yield dbclient
    await dbclient.drop_database(settings.MONGO_DB_NAME)
    dbclient.close()

@pytest.fixture(scope="function")
async def setup_balance_test_data(mongodb_client):
    collection = mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_BALANCE_COLLECTION]

    # Create test balance data
    test_balance = {
        "account_id": "123",
        "balance": 1000.0,
        "user_id": 456,
        "username": "test_user"
    }

    # Insert test data
    await collection.insert_one(test_balance)

@pytest.fixture(scope="function")
async def setup_history_test_data(mongodb_client):
    collection = mongodb_client[settings.MONGO_DB_NAME][settings.MONGO_TRANSACTION_COLLECTION]

    # Create test transactions with different timestamps
    base_time = datetime.now()
    test_transactions = [
        {
            "id": "tx123",
            "account_id": "123",
            "amount": 1000.0,
            "type": "DEPOSIT",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "status": "PENDING",
            "description": "Deposit of $1000",
            "version": 1
        },
        {
            "id": "tx124",
            "account_id": "123",
            "amount": 1500.0,
            "type": "DEPOSIT",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "status": "PENDING",
            "description": "Deposit of $1500",
            "version": 1
        },
        {
            "id": "tx125",
            "account_id": "123",
            "amount": 1300.0,
            "type": "WITHDRAWAL",
            "timestamp": base_time.isoformat(),
            "status": "PENDING",
            "description": "Withdrawal of $1300",
            "version": 1
        }
    ]

    # Insert test data
    await collection.insert_many(test_transactions)

@pytest.fixture
def mock_account_service():
    return Mock(spec=AccountService)

@pytest.mark.asyncio
async def test_get_balance(setup_balance_test_data):
    account_service = AccountService()

    with patch('app.api.routes.v1.account_handlers.get_account_service', return_value=account_service):
        response = client.get("/mybank/api/v1/account/123/balance")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["account_id"] == "123"
        assert response_data["balance"] == 1000.0
        assert response_data["user_id"] == 456
        assert response_data["username"] == "test_user"

@pytest.mark.asyncio
async def test_get_balance_not_found(mock_account_service):
    with patch('app.api.routes.v1.account_handlers.get_account_service', return_value=mock_account_service):
        mock_account_service.get_current_balance.side_effect = ValueError('Not Found')

        response = client.get("/mybank/api/v1/account/999/balance")
        assert response.status_code == 404
        assert response.json()["detail"] == "Balance for account id: 999 not found"

@pytest.mark.asyncio
async def test_get_transaction_history(setup_history_test_data):
    account_service = AccountService()

    with patch('app.api.routes.v1.account_handlers.get_account_service', return_value=account_service):
        response = client.get("/mybank/api/v1/account/123/history")

        # print response.json()
        print(response.json())

        assert response.status_code == 200
        transactions = response.json()

        assert len(transactions) == 3

        transaction_ids = [tx["id"] for tx in transactions]
        assert "tx123" in transaction_ids
        assert "tx124" in transaction_ids
        assert "tx125" in transaction_ids

        amounts = [tx["amount"] for tx in transactions]
        assert 1000.0 in amounts
        assert 1500.0 in amounts
        assert 1300.0 in amounts

        assert all(tx["account_id"] == "123" for tx in transactions)

        assert all(tx["status"] == "PENDING" for tx in transactions)

@pytest.mark.asyncio
async def test_get_transaction_history_not_found(mock_account_service):
    with patch('app.api.routes.v1.account_handlers.get_account_service', return_value=mock_account_service):
        mock_account_service.get_history_transactions.side_effect = ValueError('Not Found')

        response = client.get("/mybank/api/v1/account/999/history")

        # print response.json()
        print(response.json())

        assert response.status_code == 404
        assert response.json()["detail"] == "History for account id: 999 not found"
