from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.project import Project
from aureon.services.supabase.client import get_supabase_client


class ProjectRepository:
    """Data-access wrapper around ``projects`` — the Project Knowledge
    Base. Same normalized-rows shape as SkillRepository/CompanyRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_projects(self, *, difficulty_level: str | None = None) -> list[Project]:
        def _fetch() -> list[dict]:
            query = self._client.table("projects").select("*")
            if difficulty_level:
                query = query.eq("difficulty_level", difficulty_level)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Project.model_validate(row) for row in rows]

    async def get_project(self, project_id: str) -> Project | None:
        def _fetch() -> dict | None:
            row = self._client.table("projects").select("*").eq("id", project_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Project.model_validate(data) if data else None

    async def list_by_ids(self, project_ids: list[str]) -> list[Project]:
        """Resolves a set of real project ids into full ``Project``
        objects — same pattern as SkillRepository/CompanyRepository's
        list_by_ids."""
        if not project_ids:
            return []

        def _fetch() -> list[dict]:
            result = self._client.table("projects").select("*").in_("id", project_ids).execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Project.model_validate(row) for row in rows]

    async def list_projects_for_career(self, career_id: str) -> list[Project]:
        """Sprint 3 — the reverse-lookup direction. Unlike Skill/Company
        (where Career holds the outgoing edge and CareerRepository does
        the filtering), Project holds its own related_career_ids edge, so
        this filter lives here instead. Same small-knowledge-base,
        filter-in-Python convention as CareerRepository.list_careers_
        requiring_skill (~20 rows, no jsonb-containment query needed)."""
        projects = await self.list_projects()
        return [p for p in projects if career_id in p.related_career_ids]
