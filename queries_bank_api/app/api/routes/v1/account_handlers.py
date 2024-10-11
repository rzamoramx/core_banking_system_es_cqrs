
from fastapi import APIRouter, Depends
from app.services.AccountService import AccountService

router = APIRouter()

def get_account_service():
    service = AccountService()
    yield service


@router.get("/account/{account_id}/balance")
async def get_actual_balance(account_id: str, account_service: AccountService = Depends(get_account_service)):
    balance = await account_service.get_current_balance(account_id)
    return balance.model_dump()


@router.get("/account/{account_id}/history")
async def get_balance_history(account_id: str, account_service: AccountService = Depends(get_account_service)):
    history = await account_service.get_history_transactions(account_id)
    return [balance.model_dump() for balance in history]
