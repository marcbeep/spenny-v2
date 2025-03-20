from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from uuid import UUID

from app.db.client import get_supabase_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    pass


def verify_user_access(user_id: UUID, current_user_id: UUID) -> bool:
    pass
