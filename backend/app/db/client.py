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
        client.table("users").select("*").limit(1).execute()
        return client

    except Exception as e:
        raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")


@lru_cache()
def get_supabase_admin_client() -> Client:
    """
    Creates and returns a cached Supabase admin client with service role privileges.
    This client bypasses RLS policies and should only be used for admin operations.

    Returns:
        Client: Supabase admin client instance with service role privileges

    Raises:
        ConnectionError: If connection to Supabase fails
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ConnectionError(
                "Supabase service role credentials not properly configured"
            )

        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY,
        )

        # Test the connection
        client.table("users").select("*").limit(1).execute()
        return client

    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to Supabase with service role: {str(e)}"
        )


# Global client instances
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None


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


def get_admin_db() -> Client:
    """
    Returns the global Supabase admin client instance with service role privileges.
    Creates a new instance if none exists.

    Returns:
        Client: Supabase admin client instance with service role privileges
    """
    global supabase_admin
    if supabase_admin is None:
        supabase_admin = get_supabase_admin_client()
    return supabase_admin
