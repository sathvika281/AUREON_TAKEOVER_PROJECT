from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.life_mission import LifeMission
from aureon.services.supabase.client import get_supabase_client


class LifeMissionRepository:
    """Data-access wrapper around ``life_missions`` — the Life Missions
    catalog. Same normalized-rows shape as TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_missions(self) -> list[LifeMission]:
        def _fetch() -> list[dict]:
            result = self._client.table("life_missions").select("*").execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [LifeMission.model_validate(row) for row in rows]

    async def get_mission(self, mission_id: str) -> LifeMission | None:
        def _fetch() -> dict | None:
            row = self._client.table("life_missions").select("*").eq("id", mission_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return LifeMission.model_validate(data) if data else None
