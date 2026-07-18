from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.mentor import Mentor
from aureon.services.supabase.client import get_supabase_client

DEFAULT_LIMIT = 100


class ExpertRepository:
    """Search/filter/pagination data-access layer for Expert Connect —
    reads the same ``mentors`` table as ``MentorRepository`` (an expert
    IS a Mentor; see ``domain/models/mentor.py``), but ``MentorRepository``
    itself is left untouched so Decision Lab's mentor-matching and the
    existing ``/mentors`` routes carry zero risk from this batch.

    First repository in this backend with real offset pagination — every
    other repository fetches its whole (small) table. Scoped here only,
    since the Expert catalog (100+ rows) is the first collection large
    enough to warrant it.
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def search_experts(
        self,
        *,
        q: str | None = None,
        specialization: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        min_years_experience: int | None = None,
        accepts_mentorship: bool | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> tuple[list[Mentor], int]:
        def _fetch() -> tuple[list[dict], int]:
            query = self._client.table("mentors").select("*", count="exact")
            if q:
                query = query.or_(
                    f"name.ilike.%{q}%,profession.ilike.%{q}%,specialization.ilike.%{q}%"
                )
            if specialization:
                query = query.eq("specialization", specialization)
            if industry:
                query = query.contains("industries", [industry])
            if country:
                query = query.eq("country", country)
            if min_years_experience is not None:
                query = query.gte("years_experience", min_years_experience)
            if accepts_mentorship is not None:
                query = query.eq("accepts_mentorship", accepts_mentorship)
            result = query.range(offset, offset + limit - 1).execute()
            return result.data or [], result.count or 0

        rows, total = await run_in_threadpool(_fetch)
        return [Mentor.model_validate(row) for row in rows], total

    async def get_expert(self, expert_id: str) -> Mentor | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("mentors")
                .select("*")
                .eq("id", expert_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Mentor.model_validate(data) if data else None

    async def list_filter_values(self) -> tuple[list[str], list[str], list[str]]:
        """Distinct specialization/industries/country values present in
        the catalog today, for populating frontend filter buttons
        without a separate hardcoded list."""

        def _fetch() -> list[dict]:
            result = self._client.table("mentors").select(
                "specialization,industries,country"
            ).execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        specializations = sorted({r["specialization"] for r in rows if r.get("specialization")})
        industries = sorted({i for r in rows for i in (r.get("industries") or [])})
        countries = sorted({r["country"] for r in rows if r.get("country")})
        return specializations, industries, countries
