
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

"""this endpoint handlers is for programmatic method to subscribe to a topic, check main.py for subscription details"""

@router.post('/account_projections/handler', response_model=None)
async def account_projections_handler(event: CloudEventModel, account_service: AccountService = Depends(get_account_service)):
    transaction = Transaction(**json.loads(event.data))

    print(f'Start procressing balance projection')

    # convert float to Decimal
    amount = Decimal(transaction.amount)

    # update the balance
    await account_service.update_balance(transaction.account_id, amount, transaction.type)

    print(f'Start procressing transaction history projection')

    # save the transaction to history
    await account_service.save_transaction(transaction)

    return {"message": "Projections processed successfully"}