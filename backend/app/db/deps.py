from typing import Generator
from supabase import Client
from fastapi import Depends, HTTPException, status
from app.db.client import get_db


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
