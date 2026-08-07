"""One-time backfill for Sprint 2's Career -> Company promotion
(docs/SPRINT_2.md). Run via: python -m aureon.scripts.backfill_career_company_edges

Reads every real, live Career row and resolves its existing `companies`
free-text entries into real `company_ids` via the alias map already used
to seed the Company catalog (scripts/seed_companies.py). Only ever
writes the new `company_ids` column — the top-level `companies` string
list is read, never modified, per the sprint's "additive alongside, not
replacing" scope. Same honest, fail-open matching discipline as Sprint
1's Skill backfill: a career whose companies don't cleanly match
anything in the alias map simply gets a partial (or empty) company_ids
list, never a guessed match.

Depends on: migrations 0027/0028 applied, and scripts/seed_companies.py
already run.
"""

import asyncio

from aureon.scripts.seed_companies import COMPANY_ALIASES
from aureon.services.supabase.client import get_supabase_client


async def backfill() -> None:
    client = get_supabase_client()

    def _fetch_careers() -> list[dict]:
        return client.table("careers").select("id,name,companies").execute().data

    careers = await asyncio.to_thread(_fetch_careers)

    updated = 0
    unmatched: dict[str, list[str]] = {}
    for career in careers:
        raw_companies = career.get("companies") or []
        resolved: list[str] = []
        for raw in raw_companies:
            company_id = COMPANY_ALIASES.get(raw)
            if company_id and company_id not in resolved:
                resolved.append(company_id)
            elif not company_id:
                unmatched.setdefault(career["id"], []).append(raw)

        if not resolved:
            continue

        def _update(career_id: str = career["id"], company_ids: list[str] = resolved) -> None:
            client.table("careers").update({"company_ids": company_ids}).eq("id", career_id).execute()

        await asyncio.to_thread(_update)
        updated += 1

    print(f"Backfilled company_ids on {updated}/{len(careers)} careers.")
    if unmatched:
        total_unmatched = sum(len(v) for v in unmatched.values())
        print(
            f"{total_unmatched} raw companies strings across {len(unmatched)} careers had no alias "
            "match and were left unlinked (honest — not forced onto a nearest-guess company)."
        )


if __name__ == "__main__":
    asyncio.run(backfill())
