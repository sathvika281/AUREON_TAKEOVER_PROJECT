from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.career_event import CareerEvent
from aureon.services.supabase.client import get_supabase_client


class CareerEventRepository:
    """Data-access wrapper around the ``career_events`` table — presented
    to students as "Experience Events." Shared by institution-hosted
    (workshops/hackathons/open days) and mentor-hosted (career talks)
    events; same table, same repository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_career_events(
        self, *, institution_id: str | None = None, mentor_id: str | None = None
    ) -> list[CareerEvent]:
        def _fetch() -> list[dict]:
            query = self._client.table("career_events").select("*")
            if institution_id:
                query = query.eq("institution_id", institution_id)
            if mentor_id:
                query = query.eq("mentor_id", mentor_id)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [CareerEvent.model_validate(row) for row in rows]

    async def get_career_event(self, event_id: str) -> CareerEvent | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("career_events")
                .select("*")
                .eq("id", event_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return CareerEvent.model_validate(data) if data else None
