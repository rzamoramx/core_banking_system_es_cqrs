
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class BalanceModel(BaseModel):
    balance: Decimal
    currency: str = 'MXN'
    user_id: int
    username: str
    account_id: str
    # optional fields
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }
