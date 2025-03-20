from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID4
    created_at: datetime


class User(UserBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
