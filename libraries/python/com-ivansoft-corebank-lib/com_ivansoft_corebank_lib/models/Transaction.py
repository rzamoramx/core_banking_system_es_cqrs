
from datetime import datetime
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Any


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAWAL"


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
            # First try ISO format
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                pass

            # Try common Java toString() formats (e.g., Wed Apr 08 17:26:53 UTC 2026)
            # We try to parse the bits we know and ignore the timezone string if it's not CST
            try:
                # Format: %a %b %d %H:%M:%S %Z %Y
                # Strptime %Z is sometimes problematic, so we try a few common patterns
                for tz in ['UTC', 'CST', 'GMT', 'EST', 'PST']:
                    try:
                        return datetime.strptime(value, f'%a %b %d %H:%M:%S {tz} %Y')
                    except ValueError:
                        continue
                
                # If still failing, it might be an ISO-like format without separators or something else
                raise ValueError(f"No matching format for date string: {value}")
            except Exception as e:
                raise ValueError(f"Invalid date format: {value}. Error: {str(e)}")
        elif isinstance(value, datetime):
            return value
        raise ValueError(f"Invalid date type: {type(value)}")
