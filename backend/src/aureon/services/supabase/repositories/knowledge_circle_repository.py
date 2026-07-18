from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.services.supabase.client import get_supabase_client


class KnowledgeCircleRepository:
    """Data-access wrapper around ``knowledge_circles``. Same normalized-
    rows shape as ``CareerWorldRepository`` — a small (~31 row) catalog,
    no pagination needed."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_circles(self, *, q: str | None = None) -> list[KnowledgeCircle]:
        def _fetch() -> list[dict]:
            query = self._client.table("knowledge_circles").select("*")
            if q:
                query = query.ilike("name", f"%{q}%")
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [KnowledgeCircle.model_validate(row) for row in rows]

    async def get_circle(self, circle_id: str) -> KnowledgeCircle | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("knowledge_circles")
                .select("*")
                .eq("id", circle_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return KnowledgeCircle.model_validate(data) if data else None
