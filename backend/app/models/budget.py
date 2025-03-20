from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


class BudgetBase(BaseModel):
    name: str
    is_default: bool = False


class BudgetCreate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime


class Budget(BudgetBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
