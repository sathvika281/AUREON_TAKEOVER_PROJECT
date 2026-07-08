from aureon.domain.models.student_profile import StudentProfile

"""Shared deterministic recommendation helper (V13) — extracted from
Career Simulator's own private copy (V11) so it's reused, not
re-implemented, everywhere a real recommendation of already-matched
mentors/institutions is needed. No new AI reasoning happens here: it only
ever surfaces the top of what the student's own real Mentor Match/
Institution Match analysis (an LLM call the student explicitly
triggered) already produced."""

#: Same cap V11 established — never floods the student with every match,
#: just the strongest ones.
TOP_RECOMMENDATIONS = 2


def top_active_mentor_names(profile: StudentProfile, *, limit: int = TOP_RECOMMENDATIONS) -> list[str]:
    active = sorted(
        (m for m in profile.mentor_matches if m.status != "discarded"),
        key=lambda m: m.confidence, reverse=True,
    )
    return [m.mentor_name for m in active[:limit]]


def top_active_institution_names(
    profile: StudentProfile, *, limit: int = TOP_RECOMMENDATIONS, partner_ids: set[str] | None = None
) -> list[str]:
    """When ``partner_ids`` is given, only real ``is_partner`` institutions
    are eligible — this is how Career Intelligence/Comparison bias toward
    *collaborating* colleges specifically, per "highlights opportunities
    offered by collaborating institutions" rather than a generic ranking."""
    active = [m for m in profile.college_matches if m.status != "discarded"]
    if partner_ids is not None:
        active = [m for m in active if m.institution_id in partner_ids]
    active.sort(key=lambda m: m.confidence, reverse=True)
    return [m.institution_name for m in active[:limit]]
