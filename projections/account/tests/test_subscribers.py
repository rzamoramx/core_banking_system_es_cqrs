import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from decimal import Decimal
from app.api.eventsource.v1.subscribers import router, get_account_service
from app.api.schemas.CloudEventModel import CloudEventModel
from app.services.AccountService import AccountService
from com_ivansoft_corebank_lib.models.Transaction import TransactionType
import json

@pytest.fixture
def mock_account_service():
    service = AccountService()
    service.update_balance = AsyncMock()
    service.save_transaction = AsyncMock()
    return service

@pytest.fixture
def test_app():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    
    # Override the dependency
    async def override_get_account_service():
        service = AccountService()
        service.update_balance = AsyncMock()
        service.save_transaction = AsyncMock()
        return service
    
    app.dependency_overrides[get_account_service] = override_get_account_service
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_account_projections_handler_success(client):
    # Arrange
    transaction_data = {
        "id": "tx123",
        "account_id": "acc123",
        "amount": 100.0,
        "type": TransactionType.DEPOSIT,
        "status": "PENDING",
        "description": "Deposit of $100",
        "timestamp": "2024-03-20T12:00:00Z",
        "version": 1,
    }
    
    cloud_event = {
        "specversion": "1.0",
        "type": "com.dapr.event.sent",
        "source": "test",
        "id": "123",
        "datacontenttype": "application/json",
        "data": json.dumps(transaction_data),
        "topic": "transaction".capitalize(),
        "pubsubname": "eventsource",
        "tracestate": "test",
        "traceid": "test",
    }

    # Act
    response = client.post("/account_projections/handler", json=cloud_event)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Projections processed successfully"}

def test_account_projections_handler_invalid_transaction_data(client):
    # Arrange
    invalid_transaction_data = {
        # Missing required fields
        "account_id": "acc123",
        "amount": 100.0,
    }
    
    cloud_event = {
        "specversion": "1.0",
        "type": "com.dapr.event.sent",
        "source": "test",
        "id": "123",
        "topic": "transaction",
        "datacontenttype": "application/json",
        "data": json.dumps(invalid_transaction_data),
        "pubsubname": "eventsource",
        "tracestate": "test",
        "traceid": "test",
    }

    # this will fail due pydantic validation, so we expect an exception not a 422
    with pytest.raises(Exception):
        # Act
        client.post("/account_projections/handler", json=cloud_event)


@pytest.mark.asyncio
async def test_account_projections_handler_service_integration(mock_account_service):
    # Arrange
    transaction_data = {
        "id": "tx123",
        "account_id": "acc123",
        "amount": 100.0,
        "type": TransactionType.DEPOSIT,
        "status": "PENDING",
        "description": "Deposit of $100",
        "timestamp": "2024-03-20T12:00:00Z",
        "version": 1,
    }
    
    cloud_event = CloudEventModel(
        specversion="1.0",
        type="com.dapr.event.sent",
        source="test",
        id="123",
        datacontenttype="application/json",
        data=json.dumps(transaction_data),
        topic="transaction",
        pubsubname="eventsource",
        tracestate="test",
        traceid="test",
    )

    # Act
    with patch('app.api.eventsource.v1.subscribers.AccountService', return_value=mock_account_service):
        from app.api.eventsource.v1.subscribers import account_projections_handler
        await account_projections_handler(cloud_event, mock_account_service)

    # Assert
    mock_account_service.update_balance.assert_called_once_with(
        "acc123",
        Decimal("100.0"),
        TransactionType.DEPOSIT
    )
    mock_account_service.save_transaction.assert_called_once()

@pytest.mark.asyncio
async def test_account_projections_handler_decimal_precision(mock_account_service):
    # Arrange
    transaction_data = {
        "id": "tx123",
        "account_id": "acc123",
        "amount": 100.45,  # Test decimal precision
        "type": TransactionType.DEPOSIT,
        "status": "PENDING",
        "description": "Deposit of $100",
        "timestamp": "2024-03-20T12:00:00Z",
        "version": 1,
    }
    
    cloud_event = CloudEventModel(
        specversion="1.0",
        type="com.dapr.event.sent",
        source="test",
        id="123",
        datacontenttype="application/json",
        data=json.dumps(transaction_data),
        topic="transaction",
        pubsubname="eventsource",
        tracestate="test",
        traceid="test",
    )

    # Act
    with patch('app.api.eventsource.v1.subscribers.AccountService', return_value=mock_account_service):
        from app.api.eventsource.v1.subscribers import account_projections_handler
        await account_projections_handler(cloud_event, mock_account_service)

    # Assert
    mock_account_service.update_balance.assert_called_once_with(
        "acc123",
        100.45,
        TransactionType.DEPOSIT
    )
