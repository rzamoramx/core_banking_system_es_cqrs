
import json
from fastapi import APIRouter, Depends
from app.api.schemas.CloudEventModel import CloudEventModel
from com_ivansoft_corebank_lib.models.Transaction import Transaction
from decimal import Decimal
from app.services.AccountService import AccountService

router = APIRouter()

def get_account_service():
    service = AccountService()
    yield service

"""this endpoint handlers is for programmatic method to subscribe to a topic, check main.py for subscription"""

@router.post('/projection_balance/handler', response_model=None)
async def balance_handler(event: CloudEventModel, account_service: AccountService = Depends(get_account_service)):
    transaction = Transaction(**json.loads(event.data))

    print(f'Transaction received: {transaction}')

    # convert float to Decimal
    amount = Decimal(transaction.amount)

    # update the balance
    await account_service.update_balance(transaction.account_id, amount, transaction.type)

    return {"message": "Balance updated successfully"}


@router.post('/projection_history/handler', response_model=None)
async def history_transaction_handler(event: CloudEventModel, account_service: AccountService = Depends(get_account_service)):
    transaction = Transaction(**json.loads(event.data))

    print(f'Transaction received: {transaction}')

    # save the transaction to history
    await account_service.save_transaction(transaction)

    return {"message": "Transaction saved successfully"}