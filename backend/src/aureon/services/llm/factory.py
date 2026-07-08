from functools import lru_cache

from aureon.core.config import Settings, get_settings
from aureon.services.llm.base import LLMClient
from aureon.services.llm.providers.groq_client import GroqClient


@lru_cache
def _cached_client(provider: str, api_key: str, model: str) -> LLMClient:
    if provider == "groq":
        return GroqClient(api_key=api_key, model=model)
    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    """Returns the configured ``LLMClient`` adapter. Swapping providers
    later means adding a branch here plus a new class under
    ``services/llm/providers/`` that implements the same protocol — no
    changes anywhere else in the codebase.
    """
    settings = settings or get_settings()
    return _cached_client(settings.llm_provider, settings.groq_api_key, settings.groq_model)
