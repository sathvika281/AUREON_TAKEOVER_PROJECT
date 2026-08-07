from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.skill import Skill
from aureon.services.supabase.client import get_supabase_client


class SkillRepository:
    """Data-access wrapper around ``skills`` — the Skill Knowledge Base.
    Same normalized-rows shape as TrendRepository/OpportunityRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_skills(self, *, category: str | None = None) -> list[Skill]:
        def _fetch() -> list[dict]:
            query = self._client.table("skills").select("*").eq("is_canonical", True)
            if category:
                query = query.eq("category", category)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Skill.model_validate(row) for row in rows]

    async def get_skill(self, skill_id: str) -> Skill | None:
        def _fetch() -> dict | None:
            row = self._client.table("skills").select("*").eq("id", skill_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Skill.model_validate(data) if data else None

    async def list_by_ids(self, skill_ids: list[str]) -> list[Skill]:
        """Resolves a set of real skill ids (e.g. a Career's
        ``required_skill_ids``) into full ``Skill`` objects — the same
        small-list-of-ids-to-rows pattern ExpertRepository.get_expert
        already establishes for a single id, generalized to a batch."""
        if not skill_ids:
            return []

        def _fetch() -> list[dict]:
            result = self._client.table("skills").select("*").in_("id", skill_ids).execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Skill.model_validate(row) for row in rows]
