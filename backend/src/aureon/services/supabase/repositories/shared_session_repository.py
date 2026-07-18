from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.shared_session import SharedSession, SharedSessionNote
from aureon.services.supabase.client import get_supabase_client


class SharedSessionRepository:
    """Data-access wrapper around the ``shared_sessions``/
    ``shared_session_notes`` tables. A session is reachable either by
    its owning student (auth-gated, by ``student_id``) or by anyone
    holding its ``access_token`` (no auth — the second participant's
    only way in)."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def create_session(self, session: SharedSession) -> SharedSession:
        def _insert() -> dict:
            result = (
                self._client.table("shared_sessions")
                .insert(session.model_dump(mode="json"))
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_insert)
        return SharedSession.model_validate(data)

    async def get_by_token(self, access_token: str) -> SharedSession | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("shared_sessions")
                .select("*")
                .eq("access_token", access_token)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return SharedSession.model_validate(data) if data else None

    async def get_by_id(self, session_id: str) -> SharedSession | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("shared_sessions")
                .select("*")
                .eq("id", session_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return SharedSession.model_validate(data) if data else None

    async def list_for_student(self, student_id: str) -> list[SharedSession]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("shared_sessions")
                .select("*")
                .eq("student_id", student_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [SharedSession.model_validate(row) for row in rows]

    async def update_session(self, session: SharedSession) -> SharedSession:
        def _update() -> dict:
            result = (
                self._client.table("shared_sessions")
                .update(session.model_dump(mode="json"))
                .eq("id", session.id)
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_update)
        return SharedSession.model_validate(data)

    async def add_note(self, note: SharedSessionNote) -> SharedSessionNote:
        def _insert() -> dict:
            result = (
                self._client.table("shared_session_notes")
                .insert(note.model_dump(mode="json"))
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_insert)
        return SharedSessionNote.model_validate(data)

    async def list_notes(self, session_id: str) -> list[SharedSessionNote]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("shared_session_notes")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at")
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [SharedSessionNote.model_validate(row) for row in rows]
