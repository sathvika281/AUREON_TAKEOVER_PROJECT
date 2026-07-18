from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.learning_style import LearningStyle
from aureon.services.supabase.client import get_supabase_client


class LearningStyleRepository:
    """Data-access wrapper around ``learning_styles`` — the Learning
    Style Discovery catalog. Same normalized-rows shape as
    TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_styles(self) -> list[LearningStyle]:
        def _fetch() -> list[dict]:
            result = self._client.table("learning_styles").select("*").execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [LearningStyle.model_validate(row) for row in rows]
