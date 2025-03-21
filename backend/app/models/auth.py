from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserRegister(UserLogin):
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int  # expiration timestamp
