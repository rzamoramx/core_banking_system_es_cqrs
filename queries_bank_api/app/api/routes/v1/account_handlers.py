from fastapi import APIRouter, Depends, HTTPException
from app.services.AccountService import AccountService

router = APIRouter()

def get_account_service():
    service = AccountService()
    yield service

@router.get("/account/{account_id}/balance")
async def get_balance(account_id: str, account_service: AccountService = Depends(get_account_service)):
    try:
        balance = await account_service.get_current_balance(account_id)
        return balance.model_dump()
    except ValueError as e:
        if str(e) == 'Not Found':
            raise HTTPException(status_code=404, detail=f"Balance for account id: {account_id} not found")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/account/{account_id}/history")
async def get_transaction_history(account_id: str, account_service: AccountService = Depends(get_account_service)):
    try:
        history = await account_service.get_history_transactions(account_id)
        return [balance.model_dump() for balance in history]
    except ValueError as e:
        if str(e) == 'Not Found':
            raise HTTPException(status_code=404, detail=f"History for account id: {account_id} not found")
        raise HTTPException(status_code=500, detail=str(e))