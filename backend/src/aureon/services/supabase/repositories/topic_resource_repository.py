from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.resource_domain import TopicResourceDomain
from aureon.services.supabase.client import get_supabase_client


class TopicResourceRepository:
    """Data-access wrapper around ``topic_resource_domains`` — the
    shared topic-keyed exploration resource catalog, composed into
    Knowledge Circles. Same normalized-rows shape as TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_domains(self) -> list[TopicResourceDomain]:
        def _fetch() -> list[dict]:
            result = self._client.table("topic_resource_domains").select("*").execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [TopicResourceDomain.model_validate(row) for row in rows]
