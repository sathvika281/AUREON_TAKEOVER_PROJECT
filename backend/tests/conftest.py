import os

import pytest

# Settings fields have no defaults by design (core/config.py is the only
# place allowed to read env vars) — tests must supply values before any
# module that calls get_settings()/get_llm_client()/get_supabase_client() is
# imported. These are dummy values; no network calls are made in this suite.
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-supabase-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")


@pytest.fixture
def settings():
    from aureon.core.config import get_settings

    return get_settings()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from aureon.main import app

    return TestClient(app)
