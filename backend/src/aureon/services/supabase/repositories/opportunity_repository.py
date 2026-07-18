from datetime import datetime, timezone

from starlette.concurrency import run_in_threadpool
from supabase import Client

from aureon.domain.models.opportunity import Opportunity, OpportunityCategory
from aureon.services.supabase.client import get_supabase_client

#: Fields compared to decide whether a re-seeded/re-provided opportunity
#: genuinely changed (and therefore deserves a version bump) — everything
#: except id/version/created_at/updated_at, which are bookkeeping, not
#: real content.
_CONTENT_FIELDS = [
    name for name in Opportunity.model_fields if name not in {"id", "version", "created_at", "updated_at"}
]


class OpportunityRepository:
    """Data-access wrapper around ``opportunities`` — the Opportunity
    Knowledge Base. Same normalized-rows shape as CareerRepository/
    MentorRepository. This is a data-access layer only — it is wrapped
    by an OpportunityProvider (see providers/seeded.py), never called
    directly by OpportunityAgent."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client or get_supabase_client()

    async def list_opportunities(
        self,
        *,
        category: OpportunityCategory | None = None,
        is_remote: bool | None = None,
        country: str | None = None,
        is_active: bool | None = True,
    ) -> list[Opportunity]:
        def _fetch() -> list[dict]:
            query = self._client.table("opportunities").select("*")
            if category:
                query = query.eq("category", category)
            if is_remote is not None:
                query = query.eq("is_remote", is_remote)
            if is_active is not None:
                query = query.eq("is_active", is_active)
            result = query.execute()
            return result.data or []

        rows = await run_in_threadpool(_fetch)
        opportunities = [Opportunity.model_validate(row) for row in rows]
        if country:
            # countries is a jsonb array column — no server-side "contains"
            # filter wired at this seed size, same documented limitation
            # pattern InstitutionRepository already accepts for its own
            # narrower filters. Filtered in Python instead of faked server-side.
            opportunities = [o for o in opportunities if not o.countries or country in o.countries]
        return opportunities

    async def get_opportunity(self, opportunity_id: str) -> Opportunity | None:
        def _fetch() -> dict | None:
            row = (
                self._client.table("opportunities")
                .select("*")
                .eq("id", opportunity_id)
                .maybe_single()
                .execute()
            )
            return row.data if row is not None else None

        data = await run_in_threadpool(_fetch)
        return Opportunity.model_validate(data) if data else None

    async def upsert_opportunity(self, opportunity: Opportunity) -> Opportunity:
        """The one place version-bumping logic lives (used by the seed
        script and any future provider that writes back). Reads the
        existing row first; bumps `version` only when real content
        differs, so re-running the seed script with unchanged data is a
        true no-op (idempotent), and only a genuine content change
        advances the version real historical OpportunityEntry records
        can reference."""
        existing = await self.get_opportunity(opportunity.id)
        now = datetime.now(timezone.utc)

        if existing is None:
            to_write = opportunity.model_copy(update={"version": 1, "created_at": now, "updated_at": now})
        else:
            changed = any(
                getattr(existing, field) != getattr(opportunity, field) for field in _CONTENT_FIELDS
            )
            if changed:
                to_write = opportunity.model_copy(
                    update={"version": existing.version + 1, "created_at": existing.created_at, "updated_at": now}
                )
            else:
                to_write = existing

        def _write() -> None:
            self._client.table("opportunities").upsert(to_write.model_dump(mode="json")).execute()

        await run_in_threadpool(_write)
        return to_write
