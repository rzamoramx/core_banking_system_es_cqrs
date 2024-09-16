
from datetime import datetime
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Any


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Transaction(BaseModel):
    id: str
    account_id: str
    amount: float
    type: TransactionType
    status: str
    description: str
    timestamp: datetime
    version: int

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_date(cls, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                # Try to parse the date with the format of the date in the database
                return datetime.strptime(value, '%a %b %d %H:%M:%S CST %Y')
            except ValueError:
                # if the date is not in the database format, try to parse it as an ISO date
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"Invalid date format: {value}")
        elif isinstance(value, datetime):
            return value
        raise ValueError(f"Invalid date type: {type(value)}")
