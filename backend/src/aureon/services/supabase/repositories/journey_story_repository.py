from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.career import CareerStory
from aureon.services.supabase.client import get_supabase_client

DEFAULT_LIMIT = 100


class JourneyStoryRepository:
    """Search/filter/pagination data-access layer for Journey Stories —
    reads the same ``career_stories`` table as ``CareerRepository`` (a
    Journey Story IS a ``CareerStory``; see ``domain/models/career.py``),
    but ``CareerRepository.list_stories_for_career`` is left untouched so
    the existing ``/careers/{id}`` detail route carries zero risk from
    this batch. Mirrors ``ExpertRepository``'s real offset-pagination
    shape, the first precedent for a collection large enough to need it.
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def search_stories(
        self,
        *,
        q: str | None = None,
        career_id: str | None = None,
        industry: str | None = None,
        career_switch: bool | None = None,
        story_type: str | None = None,
        discovery_theme: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> tuple[list[CareerStory], int]:
        def _fetch() -> tuple[list[dict], int]:
            query = self._client.table("career_stories").select("*", count="exact")
            if q:
                query = query.or_(
                    f"person_label.ilike.%{q}%,journey.ilike.%{q}%,advice.ilike.%{q}%"
                )
            if career_id:
                query = query.eq("career_id", career_id)
            if industry:
                query = query.eq("industry", industry)
            if career_switch is not None:
                query = query.eq("career_switch", career_switch)
            if story_type:
                query = query.eq("story_type", story_type)
            if discovery_theme:
                query = query.contains("discovery_themes", [discovery_theme])
            result = query.range(offset, offset + limit - 1).execute()
            return result.data or [], result.count or 0

        rows, total = await run_in_threadpool(_fetch)
        return [CareerStory.model_validate(row) for row in rows], total

    async def get_story(self, story_id: str) -> CareerStory | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("career_stories")
                .select("*")
                .eq("id", story_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return CareerStory.model_validate(data) if data else None

    async def list_filter_values(self, *, story_type: str | None = None) -> tuple[list[str], list[str], list[str]]:
        """Distinct industry/career_id/discovery_themes values present in
        the catalog today — real data only, so "do not create empty
        filters" holds automatically: a theme with zero stories simply
        never appears. Scoped by ``story_type`` (the standalone Journey
        Stories screen always passes its own default) so a filter option
        is never offered for content that screen doesn't actually show —
        without this, an industry covered only by professional stories
        would appear as a selectable filter yet return zero results.
        Career *names* are deliberately not resolved here — that needs
        the Career catalog, which the API route already has via
        ``CareerRepository``; this repository stays join-free, joining
        only the columns it actually owns."""

        def _fetch() -> list[dict]:
            query = self._client.table("career_stories").select("industry,career_id,discovery_themes")
            if story_type:
                query = query.eq("story_type", story_type)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        industries = sorted({r["industry"] for r in rows if r.get("industry")})
        career_ids = sorted({r["career_id"] for r in rows if r.get("career_id")})
        discovery_themes = sorted({theme for r in rows for theme in (r.get("discovery_themes") or [])})
        return industries, career_ids, discovery_themes
