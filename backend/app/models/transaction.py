from pydantic import BaseModel, UUID4
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class TransactionBase(BaseModel):
    date: date
    payee: str
    amount: Decimal
    note: Optional[str] = None
    cleared: bool = False


class TransactionCreate(TransactionBase):
    budget_id: UUID4
    account_id: UUID4
    category_id: Optional[UUID4] = None


class TransactionRead(TransactionBase):
    id: UUID4
    budget_id: UUID4
    account_id: UUID4
    category_id: Optional[UUID4] = None
    created_at: datetime


class Transaction(TransactionBase):
    id: UUID4
    budget_id: UUID4
    account_id: UUID4
    category_id: Optional[UUID4] = None
    created_at: datetime

    class Config:
        from_attributes = True
