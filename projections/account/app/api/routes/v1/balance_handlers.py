
from fastapi import APIRouter
from app.services.AccountService import BalanceService

router = APIRouter()


@router.get("/account/{account_id}/balance")
async def get_actual_balance(account_id: str):
    balance_service = BalanceService()
    balance = await balance_service.get_current_balance(account_id)
    return balance.model_dump()


@router.get("/{account_id}/balance/history")
async def get_balance_history(account_id: str):
    balance_service = BalanceService()
    history = await balance_service.get_history_balance(account_id)
    return [balance.model_dump() for balance in history]
