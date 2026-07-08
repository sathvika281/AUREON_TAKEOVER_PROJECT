from functools import lru_cache

from supabase import Client, create_client

from aureon.core.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Singleton Supabase client factory. ``supabase-py`` is used
    synchronously here (its async support currently lags); repository
    methods wrap calls in ``starlette.concurrency.run_in_threadpool`` so
    the FastAPI/LangGraph event loop is never blocked.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)
