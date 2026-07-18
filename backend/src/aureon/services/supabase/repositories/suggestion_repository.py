from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.suggestion import Suggestion
from aureon.services.supabase.client import get_supabase_client


class SuggestionRepository:
    """Data-access wrapper around ``suggestions``."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def create(self, suggestion: Suggestion) -> Suggestion:
        def _insert() -> dict:
            result = self._client.table("suggestions").insert(suggestion.model_dump(mode="json")).execute()
            return result.data[0]

        data = await run_in_threadpool(_insert)
        return Suggestion.model_validate(data)

    async def get_by_id(self, suggestion_id: str) -> Suggestion | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("suggestions")
                .select("*")
                .eq("id", suggestion_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Suggestion.model_validate(data) if data else None

    async def list_for_student(self, student_id: str) -> list[Suggestion]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("suggestions")
                .select("*")
                .eq("student_id", student_id)
                .order("created_at", desc=True)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Suggestion.model_validate(row) for row in rows]

    async def list_all(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Suggestion]:
        """Reviewer-facing listing — never scoped to one student. ``search``
        matches ``title``/``description`` via a simple case-insensitive
        ``ilike``, no clustering or embeddings."""

        def _fetch() -> list[dict]:
            query = self._client.table("suggestions").select("*")
            if status:
                query = query.eq("status", status)
            if category:
                query = query.eq("category", category)
            if search:
                escaped = search.replace(",", " ").replace("%", "")
                query = query.or_(f"title.ilike.%{escaped}%,description.ilike.%{escaped}%")
            result = (
                query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Suggestion.model_validate(row) for row in rows]

    async def update(self, suggestion: Suggestion) -> Suggestion:
        def _update() -> dict:
            result = (
                self._client.table("suggestions")
                .update(suggestion.model_dump(mode="json"))
                .eq("id", suggestion.id)
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_update)
        return Suggestion.model_validate(data)
