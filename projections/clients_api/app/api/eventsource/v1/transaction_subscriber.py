
import json
from fastapi import APIRouter
from app.api.schemas.CloudEventModel import CloudEventModel
from com_ivansoft_corebank_lib.models.Transaction import Transaction

router = APIRouter()


# this method is for programmatic method to subscribe to a topic, check main.py for subscription
@router.post('/handler', response_model=None)
def transaction_handler(event: CloudEventModel):
    transaction = Transaction(**json.loads(event.data))

    print(f'Transaction received: {transaction}')

    return {"message": "Transaction received successfully"}