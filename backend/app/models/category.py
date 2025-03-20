from pydantic import BaseModel, UUID4
from datetime import datetime
from decimal import Decimal
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    allocated: Decimal = Decimal("0.00")


class CategoryCreate(CategoryBase):
    budget_id: UUID4


class CategoryRead(CategoryBase):
    id: UUID4
    budget_id: UUID4
    created_at: datetime


class Category(CategoryBase):
    id: UUID4
    budget_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
