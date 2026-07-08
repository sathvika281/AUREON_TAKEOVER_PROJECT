from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.mentor import Mentor
from aureon.services.supabase.client import get_supabase_client


class MentorRepository:
    """Data-access wrapper around the ``mentors`` table — the Mentor
    Knowledge Base. Same normalized-rows shape as CareerRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_mentors(
        self, *, role_type: str | None = None, field: str | None = None
    ) -> list[Mentor]:
        def _fetch() -> list[dict]:
            query = self._client.table("mentors").select("*")
            if role_type:
                query = query.eq("role_type", role_type)
            if field:
                query = query.eq("field", field)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Mentor.model_validate(row) for row in rows]

    async def get_mentor(self, mentor_id: str) -> Mentor | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("mentors")
                .select("*")
                .eq("id", mentor_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Mentor.model_validate(data) if data else None
