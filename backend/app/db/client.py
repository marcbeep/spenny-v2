from typing import Optional
from supabase import create_client, Client
from app.config.settings import settings
from functools import lru_cache


class DatabaseError(Exception):
    """Base exception for database errors"""

    pass


class ConnectionError(DatabaseError):
    """Exception for connection errors"""

    pass


@lru_cache()
def get_supabase_client() -> Client:
    """
    Creates and returns a cached Supabase client instance.
    Uses lru_cache to maintain a single instance throughout the application.

    Returns:
        Client: Supabase client instance

    Raises:
        ConnectionError: If connection to Supabase fails
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ConnectionError("Supabase credentials not properly configured")

        client = create_client(
            supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_KEY
        )

        # Test the connection
        client.table("user").select("*").limit(1).execute()
        return client

    except Exception as e:
        raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")


# Global client instance
supabase: Optional[Client] = None


def get_db() -> Client:
    """
    Returns the global Supabase client instance.
    Creates a new instance if none exists.

    Returns:
        Client: Supabase client instance
    """
    global supabase
    if supabase is None:
        supabase = get_supabase_client()
    return supabase
