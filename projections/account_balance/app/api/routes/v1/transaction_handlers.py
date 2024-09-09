
from fastapi import APIRouter

router = APIRouter()


@router.get("/{client_id}/transactions")
async def get_transactions(client_id: str):
    return {"client_id": client_id, "transactions": []}
