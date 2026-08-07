from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.company import Company
from aureon.services.supabase.client import get_supabase_client


class CompanyRepository:
    """Data-access wrapper around ``companies`` — the Company Knowledge
    Base. Same normalized-rows shape as SkillRepository/TrendRepository."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_companies(
        self, *, industry: str | None = None, organization_kind: str | None = None
    ) -> list[Company]:
        def _fetch() -> list[dict]:
            query = self._client.table("companies").select("*")
            if industry:
                query = query.eq("industry", industry)
            if organization_kind:
                query = query.eq("organization_kind", organization_kind)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Company.model_validate(row) for row in rows]

    async def get_company(self, company_id: str) -> Company | None:
        def _fetch() -> dict | None:
            row = self._client.table("companies").select("*").eq("id", company_id).maybe_single().execute()
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Company.model_validate(data) if data else None

    async def list_by_ids(self, company_ids: list[str]) -> list[Company]:
        """Resolves a set of real company ids (e.g. a Career's
        ``company_ids``) into full ``Company`` objects — same pattern as
        SkillRepository.list_by_ids."""
        if not company_ids:
            return []

        def _fetch() -> list[dict]:
            result = self._client.table("companies").select("*").in_("id", company_ids).execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        return [Company.model_validate(row) for row in rows]
