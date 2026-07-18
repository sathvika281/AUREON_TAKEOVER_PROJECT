from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.parent_connect import ParentCareerGuide, ParentQuestion
from aureon.services.supabase.client import get_supabase_client


class ParentConnectRepository:
    """Data-access wrapper around the ``parent_career_guides``/
    ``parent_questions`` tables."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def get_guide(self, career_id: str, *, language: str = "en") -> ParentCareerGuide | None:
        """Falls back to English when a translated row genuinely doesn't
        exist for the requested language — a defensive safety net, not a
        substitute for real translation coverage (every guide is
        translated for every officially supported language by
        scripts/translate_parent_connect_content.py).

        Also tolerates the `language` column not existing yet on this
        environment's live database (migration 0023 pending manual
        application — see the migration file) by falling back to an
        unfiltered query. Without this, adding the language filter would
        regress the *existing*, already-live English content to a hard
        500 the moment this code ships, not just leave the new
        multilingual feature inert — a real behavior change this
        repository must not allow.
        """

        def _fetch(lang: str | None) -> dict | None:
            query = self._client.table("parent_career_guides").select("*").eq("career_id", career_id)
            if lang is not None:
                query = query.eq("language", lang)
            row = query.maybe_single().execute()
            return row.data if row is not None else None

        try:
            data = await run_in_threadpool(_fetch, language)
            if data is None and language != "en":
                data = await run_in_threadpool(_fetch, "en")
        except Exception:
            data = await run_in_threadpool(_fetch, None)
        return ParentCareerGuide.model_validate(data) if data else None

    async def list_questions(
        self, *, category: str | None = None, career_id: str | None = None, language: str = "en"
    ) -> list[ParentQuestion]:
        """See get_guide's docstring for why the `language` column-missing
        case falls back to an unfiltered query rather than erroring."""

        def _fetch(lang: str | None) -> list[dict]:
            query = self._client.table("parent_questions").select("*")
            if lang is not None:
                query = query.eq("language", lang)
            if category:
                query = query.eq("category", category)
            if career_id:
                query = query.eq("career_id", career_id)
            result = query.execute()
            return result.data or []

        try:
            rows = await run_in_threadpool(_fetch, language)
            if not rows and language != "en":
                rows = await run_in_threadpool(_fetch, "en")
        except Exception:
            rows = await run_in_threadpool(_fetch, None)
        return [ParentQuestion.model_validate(row) for row in rows]

    async def add_question(self, question: ParentQuestion) -> ParentQuestion:
        def _insert() -> dict:
            result = (
                self._client.table("parent_questions")
                .insert(question.model_dump(mode="json"))
                .execute()
            )
            return result.data[0]

        data = await run_in_threadpool(_insert)
        return ParentQuestion.model_validate(data)
