from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.career_world import CareerWorld
from aureon.services.supabase.client import get_supabase_client


class CareerWorldRepository:
    """Data-access wrapper around ``career_worlds`` — the Missing Worlds
    catalog. Same normalized-rows shape as TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_worlds(self) -> list[CareerWorld]:
        def _fetch() -> list[dict]:
            result = self._client.table("career_worlds").select("*").execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [CareerWorld.model_validate(row) for row in rows]

    async def get_world(self, world_id: str) -> CareerWorld | None:
        def _fetch() -> dict | None:
            row = self._client.table("career_worlds").select("*").eq("id", world_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return CareerWorld.model_validate(data) if data else None
