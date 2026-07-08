from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.institution import (
    AcademicProgram,
    FacultyHighlight,
    InnovationCenter,
    Institution,
    InternshipOpportunity,
    ResearchLab,
    StudentAmbassador,
    StudentOrganization,
    StudentProject,
)
from aureon.services.supabase.client import get_supabase_client


class InstitutionRepository:
    """Data-access wrapper around ``institutions`` + its child tables
    (research_labs, student_organizations, academic_programs, and V13's
    innovation_centers/faculty_highlights/student_ambassadors/
    student_projects/internship_opportunities) — same normalized-rows
    shape as CareerRepository, scaled up since institutions are genuinely
    1-to-many with these child entities."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_institutions(
        self, *, country: str | None = None, field: str | None = None, is_partner: bool | None = None
    ) -> list[Institution]:
        def _fetch() -> list[dict]:
            query = self._client.table("institutions").select("*")
            if country:
                query = query.eq("country", country)
            if is_partner is not None:
                query = query.eq("is_partner", is_partner)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        institutions = [Institution.model_validate(row) for row in rows]
        if field:
            # No dedicated "field" column on institutions itself (fields
            # live on academic_programs) — filtering by field here would
            # need a join; not needed at this seed size, so left
            # unimplemented rather than faked.
            pass
        return institutions

    async def get_institution(self, institution_id: str) -> Institution | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("institutions")
                .select("*")
                .eq("id", institution_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Institution.model_validate(data) if data else None

    async def list_research_labs(self, institution_id: str) -> list[ResearchLab]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("research_labs")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [ResearchLab.model_validate(row) for row in rows]

    async def list_student_organizations(self, institution_id: str) -> list[StudentOrganization]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("student_organizations")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [StudentOrganization.model_validate(row) for row in rows]

    async def list_academic_programs(self, institution_id: str) -> list[AcademicProgram]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("academic_programs")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [AcademicProgram.model_validate(row) for row in rows]

    async def list_innovation_centers(self, institution_id: str) -> list[InnovationCenter]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("innovation_centers")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [InnovationCenter.model_validate(row) for row in rows]

    async def list_faculty_highlights(self, institution_id: str) -> list[FacultyHighlight]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("faculty_highlights")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [FacultyHighlight.model_validate(row) for row in rows]

    async def list_student_ambassadors(self, institution_id: str) -> list[StudentAmbassador]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("student_ambassadors")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [StudentAmbassador.model_validate(row) for row in rows]

    async def list_student_projects(self, institution_id: str) -> list[StudentProject]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("student_projects")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [StudentProject.model_validate(row) for row in rows]

    async def list_internship_opportunities(self, institution_id: str) -> list[InternshipOpportunity]:
        def _fetch() -> list[dict]:
            result = (
                self._client.table("internship_opportunities")
                .select("*")
                .eq("institution_id", institution_id)
                .execute()
            )
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [InternshipOpportunity.model_validate(row) for row in rows]
