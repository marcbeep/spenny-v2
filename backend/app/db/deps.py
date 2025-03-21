from typing import Generator
from supabase import Client
from fastapi import Depends, HTTPException, status
from app.db.client import get_db, get_admin_db


def get_supabase() -> Generator[Client, None, None]:
    """
    FastAPI dependency that provides a Supabase client.
    Handles connection errors and yields a client instance.

    Yields:
        Client: Supabase client instance

    Raises:
        HTTPException: If database connection fails
    """
    try:
        db = get_db()
        yield db
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )


def get_supabase_admin() -> Generator[Client, None, None]:
    """
    FastAPI dependency that provides a Supabase admin client with service role privileges.
    This client bypasses RLS policies and should only be used for admin operations.

    Yields:
        Client: Supabase admin client with service role privileges

    Raises:
        HTTPException: If database connection fails
    """
    try:
        db = get_admin_db()
        yield db
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Admin database connection failed: {str(e)}",
        )
