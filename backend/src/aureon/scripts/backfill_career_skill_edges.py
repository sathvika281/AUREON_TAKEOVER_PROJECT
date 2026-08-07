"""One-time backfill for Sprint 1's Career -> Skill promotion
(docs/SPRINT_1.md). Run via: python -m aureon.scripts.backfill_career_skill_edges

Reads every real, live Career row and resolves its existing
`reality.required_skills` free-text entries into real `required_skill_ids`
via the alias map already used to seed the Skill catalog
(scripts/seed_skills.py). Only ever writes the new `required_skill_ids`
column — `reality.required_skills` is read, never modified, per the
sprint's explicit "additive alongside, not replacing" scope.

A career whose required_skills don't cleanly match anything in the alias
map simply gets an empty (or partial) required_skill_ids list — never a
guessed or forced match. Idempotent: safe to re-run after the Skill
catalog or alias map changes.

Depends on: migrations 0025/0026 applied, and scripts/seed_skills.py
already run (the Skill rows must exist for this to have anything real
to link to).
"""

import asyncio

from aureon.scripts.seed_skills import REQUIRED_SKILL_ALIASES
from aureon.services.supabase.client import get_supabase_client


async def backfill() -> None:
    client = get_supabase_client()

    def _fetch_careers() -> list[dict]:
        return client.table("careers").select("id,name,reality").execute().data

    careers = await asyncio.to_thread(_fetch_careers)

    updated = 0
    unmatched: dict[str, list[str]] = {}
    for career in careers:
        raw_skills = (career.get("reality") or {}).get("required_skills") or []
        resolved: list[str] = []
        for raw in raw_skills:
            skill_id = REQUIRED_SKILL_ALIASES.get(raw)
            if skill_id and skill_id not in resolved:
                resolved.append(skill_id)
            elif not skill_id:
                unmatched.setdefault(career["id"], []).append(raw)

        if not resolved:
            continue

        def _update(career_id: str = career["id"], skill_ids: list[str] = resolved) -> None:
            client.table("careers").update({"required_skill_ids": skill_ids}).eq("id", career_id).execute()

        await asyncio.to_thread(_update)
        updated += 1

    print(f"Backfilled required_skill_ids on {updated}/{len(careers)} careers.")
    if unmatched:
        total_unmatched = sum(len(v) for v in unmatched.values())
        print(
            f"{total_unmatched} raw required_skills strings across {len(unmatched)} careers had no alias "
            "match and were left unlinked (honest — not forced onto a nearest-guess skill)."
        )


if __name__ == "__main__":
    asyncio.run(backfill())
