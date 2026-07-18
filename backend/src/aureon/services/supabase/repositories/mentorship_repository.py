from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.mentorship import Mentorship
from aureon.services.supabase.client import get_supabase_client


class MentorshipRepository:
    """Data-access wrapper around ``mentorships``. Unlike
    ``SharedSessionRepository``, notes live embedded as jsonb on the row
    itself (``Mentorship.progress_notes``) rather than a second table —
    see ``domain/models/mentorship.py`` for why."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def create(self, mentorship: Mentorship) -> Mentorship:
        def _insert() -> dict:
            result = self._client.table("mentorships").insert(mentorship.model_dump(mode="json")).execute()
            return result.data[0]

        data = await run_in_threadpool(_insert)
        return Mentorship.model_validate(data)

    async def get_by_id(self, mentorship_id: str) -> Mentorship | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("mentorships")
                .select("*")
                .eq("id", mentorship_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Mentorship.model_validate(data) if data else None

    async def get_by_token(self, review_token: str) -> Mentorship | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("mentorships")
                .select("*")
                .eq("review_token", review_token)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Mentorship.model_validate(data) if data else None

    async def list_for_student(self, student_id: str) -> list[Mentorship]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("mentorships")
                .select("*")
                .eq("student_id", student_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Mentorship.model_validate(row) for row in rows]

    async def list_for_expert(self, expert_id: str) -> list[Mentorship]:
        """An expert must review requests across every student — this is
        exactly the query a per-student jsonb blob could never support,
        the reason ``Mentorship`` is its own table."""

        def _fetch() -> list[dict]:
            result = (
                self._client.table("mentorships")
                .select("*")
                .eq("expert_id", expert_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Mentorship.model_validate(row) for row in rows]

    async def update(self, mentorship: Mentorship) -> Mentorship:
        def _update() -> dict:
            result = (
                self._client.table("mentorships")
                .update(mentorship.model_dump(mode="json"))
                .eq("id", mentorship.id)
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_update)
        return Mentorship.model_validate(data)
