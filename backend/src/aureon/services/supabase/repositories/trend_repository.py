from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.trend import Trend
from aureon.services.supabase.client import get_supabase_client


class TrendRepository:
    """Data-access wrapper around ``trends`` — the Global Trends
    Knowledge Base. Same normalized-rows shape as CareerRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_trends(
        self, *, category: str | None = None, industry: str | None = None, region: str | None = None
    ) -> list[Trend]:
        def _fetch() -> list[dict]:
            query = self._client.table("trends").select("*")
            if category:
                query = query.eq("category", category)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        trends = [Trend.model_validate(row) for row in rows]
        # affected_industries/regions are small jsonb arrays on a small
        # (~15-20 row) knowledge base — filtered in Python, same
        # documented convention as CareerRepository's country filter.
        if industry:
            trends = [t for t in trends if industry.lower() in {i.lower() for i in t.affected_industries}]
        if region:
            trends = [t for t in trends if not t.regions or region in t.regions]
        return trends

    async def get_trend(self, trend_id: str) -> Trend | None:
        def _fetch() -> dict | None:
            row = self._client.table("trends").select("*").eq("id", trend_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Trend.model_validate(data) if data else None
