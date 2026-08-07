from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.career import Career, CareerStory
from aureon.services.supabase.client import get_supabase_client


class CareerRepository:
    """Data-access wrapper around the ``careers``/``career_stories``
    tables — the Career Knowledge Base. Unlike ``student_profiles`` (one
    jsonb blob per student, always read/written whole), these are
    normalized rows meant to be searched/filtered/joined, so plain
    column-level queries are used rather than a single blob read.
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_careers(
        self,
        *,
        category: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        q: str | None = None,
    ) -> list[Career]:
        def _fetch() -> list[dict]:
            query = self._client.table("careers").select("*")
            if category:
                query = query.eq("category", category)
            if industry:
                query = query.eq("industry", industry)
            if q:
                query = query.ilike("name", f"%{q}%")
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        careers = [Career.model_validate(row) for row in rows]
        if country:
            # Countries list is small per career and the whole knowledge
            # base is small (~30 rows) — filtering client-side avoids a
            # jsonb-containment query for a case this simple.
            careers = [c for c in careers if not c.countries or country in c.countries]
        return careers

    async def get_career(self, career_id: str) -> Career | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("careers")
                .select("*")
                .eq("id", career_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Career.model_validate(data) if data else None

    async def list_careers_requiring_skill(self, skill_id: str) -> list[Career]:
        """Sprint 1 — Skill promotion. Same small-knowledge-base,
        filter-in-Python convention ``country`` filtering above already
        uses, applied to the new ``required_skill_ids`` edge rather than
        a jsonb-containment query, since the whole catalog is ~30 rows."""
        careers = await self.list_careers()
        return [c for c in careers if skill_id in c.required_skill_ids]

    async def list_careers_hiring_from_company(self, company_id: str) -> list[Career]:
        """Sprint 2 — Company promotion. Same convention as
        list_careers_requiring_skill above, applied to company_ids —
        the pattern generalizing to a second entity, as intended."""
        careers = await self.list_careers()
        return [c for c in careers if company_id in c.company_ids]

    async def list_stories_for_career(self, career_id: str) -> list[CareerStory]:
        """"Human Stories" on the career detail page — professional/workplace
        narratives only. Excludes composite_student_discovery/student_discovery
        rows (the standalone Journey Stories screen's content) so the two
        purposes never blur even when they share a career_id."""

        def _fetch() -> list[dict]:
            result = (
                self._client.table("career_stories")
                .select("*")
                .eq("career_id", career_id)
                .in_("story_type", ["composite", "publicly_documented"])
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [CareerStory.model_validate(row) for row in rows]
