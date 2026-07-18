from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for environment-driven configuration.

    Every other module (LLM factory, Supabase client, logging) receives
    values from here via dependency injection rather than reading
    environment variables directly.
    """

    environment: Literal["local", "staging", "production"] = "local"

    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str | None = None

    llm_provider: Literal["groq"] = "groq"
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Hard deterministic safety floor: recommendation-stage agents (Career
    # Intelligence, Decision, Roadmap) are never routed to below this
    # confidence score, regardless of the orchestrator LLM's own judgment.
    min_recommendation_confidence: float = 0.6

    cors_origins: list[str] = ["http://localhost:5173"]

    # Gates the reviewer-facing suggestion endpoints (api/v1/suggestions.py).
    # There is no admin/staff role anywhere in this system to hook into
    # instead — unset means the reviewer endpoints are unreachable, not
    # silently open.
    suggestion_reviewer_secret: str | None = None

    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
