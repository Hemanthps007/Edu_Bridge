"""
EduBridge — Supabase Client & Backend Service
Initializes and provides access to the Supabase client SDK for database,
auth, storage, and serverless backend communication.
"""
import os
from django.conf import settings

_supabase_client = None

def get_supabase_client():
    """
    Returns an initialized Supabase Python client instance if SUPABASE_URL
    and a valid key (anon key or service role key) are configured.
    Returns None if credentials are not provided.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = getattr(settings, 'SUPABASE_URL', None) or os.getenv('SUPABASE_URL')
    supabase_key = (
        getattr(settings, 'SUPABASE_KEY', None)
        or os.getenv('SUPABASE_KEY')
        or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        or os.getenv('SUPABASE_ANON_KEY')
    )

    if not supabase_url or not supabase_key:
        return None

    try:
        import importlib
        supabase_mod = importlib.import_module("supabase")
        create_client_fn = getattr(supabase_mod, "create_client")
        _supabase_client = create_client_fn(supabase_url, supabase_key)
        return _supabase_client
    except Exception as e:
        print(f"[EduBridge] Supabase client initialization warning: {e}")
        return None


def is_supabase_configured() -> bool:
    """Checks if Supabase credentials (URL and Key) or DB URL are set."""
    has_credentials = bool(
        (getattr(settings, 'SUPABASE_URL', None) or os.getenv('SUPABASE_URL'))
        and (getattr(settings, 'SUPABASE_KEY', None) or os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY'))
    )
    has_db = bool(os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL'))
    return has_credentials or has_db
