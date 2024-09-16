
from pydantic import BaseModel
from decimal import Decimal


class BalanceModel(BaseModel):
    balance: Decimal
    currency: str = 'MXN'
    user_id: int
    username: str
    account_id: str
    # optional fields
    created_at: str = None
    updated_at: str = None
