from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config.settings import settings
from app.models.auth import TokenPayload
from app.db.deps import get_supabase
from supabase import Client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_access_token(subject: str) -> str:
    """
    Create a JWT access token.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Client = Depends(get_supabase)
) -> str:
    """
    Validate the JWT token and return the user ID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        # Verify user exists in database
        result = db.table("users").select("id").eq("id", token_data.sub).execute()

        if not result.data:
            raise credentials_exception

        return token_data.sub

    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


def verify_user_access(user_id: UUID, current_user_id: UUID) -> bool:
    """
    Verify if the current user has access to resources belonging to the specified user.
    This simple implementation only allows access if the current user is the owner of the resource.

    Args:
        user_id: ID of the user who owns the resource
        current_user_id: ID of the current authenticated user

    Returns:
        bool: True if access is allowed, False otherwise
    """
    return str(user_id) == str(current_user_id)
