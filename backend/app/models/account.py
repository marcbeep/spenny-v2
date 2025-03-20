from pydantic import BaseModel, UUID4
from datetime import datetime
from decimal import Decimal
from typing import Optional


class AccountBase(BaseModel):
    name: str
    type: str
    balance: Decimal = Decimal("0.00")


class AccountCreate(AccountBase):
    budget_id: UUID4


class AccountRead(AccountBase):
    id: UUID4
    budget_id: UUID4
    created_at: datetime


class Account(AccountBase):
    id: UUID4
    budget_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
