from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.entrance_exam import EntranceExam
from aureon.services.supabase.client import get_supabase_client


class EntranceExamRepository:
    """Data-access wrapper around ``entrance_exams`` — Entrance Hub's
    content, merged into College Explorer (no separate navigation)."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_entrance_exams(self) -> list[EntranceExam]:
        def _fetch() -> list[dict]:
            result = self._client.table("entrance_exams").select("*").execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [EntranceExam.model_validate(row) for row in rows]

    async def list_for_institution(self, institution_id: str) -> list[EntranceExam]:
        """Membership filtered in Python — small catalog, same documented
        convention as CareerRepository's country filter."""
        all_exams = await self.list_entrance_exams()
        return [exam for exam in all_exams if institution_id in exam.accepted_institution_ids]
