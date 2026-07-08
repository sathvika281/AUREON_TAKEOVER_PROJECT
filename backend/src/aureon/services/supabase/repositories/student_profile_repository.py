from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.student_profile import StudentProfile
from aureon.services.supabase.client import get_supabase_client


class StudentProfileRepository:
    """Data-access wrapper around the ``student_profiles`` table — the
    long-term, cross-session record of a student.

    Loaded once per session start and persisted after every turn (see
    ``domain/services/conversation_service.py``), so understanding of a
    student accumulates across conversations instead of resetting each
    session, per the product's memory-design principle.
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def get_or_create(self, student_id: str) -> StudentProfile:
        def _fetch() -> dict | None:
            # maybe_single().execute() returns None outright (not a response
            # object with .data = None) when zero rows match, in this
            # supabase-py version.
            row = (
                self._client.table("student_profiles")
                .select("*")
                .eq("student_id", student_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        if data:
            return StudentProfile.model_validate(data)

        profile = StudentProfile(student_id=student_id)
        await self.save(profile)
        return profile

    async def save(self, profile: StudentProfile) -> None:
        def _upsert() -> None:
            self._client.table("student_profiles").upsert(
                profile.model_dump(mode="json")
            ).execute()

        await run_in_threadpool(_upsert)
