from aureon.domain.models.career import Career
from aureon.domain.models.student_profile import StudentProfile

"""Deterministic 'Next Best Actions' per simulated career path — every
action traces to a real gap or real existing data on the profile, never
generic motivational advice and never sent to or produced by the LLM."""


def _has_search_investigation_for(profile: StudentProfile, career: Career) -> bool:
    name = career.name.lower()
    return any(
        inv.related_career_id == career.id or name in inv.question.lower()
        for inv in profile.career_investigations
    )


def _has_github_evidence(profile: StudentProfile) -> bool:
    return any(e.source == "github" for e in profile.evidence_graph)


def _top_active(matches: list, *, name_attr: str) -> str | None:
    active = [m for m in matches if m.status != "discarded"]
    if not active:
        return None
    top = max(active, key=lambda m: m.confidence)
    return getattr(top, name_attr)


def build_next_actions(
    career: Career, other_career_names: list[str], profile: StudentProfile
) -> list[str]:
    actions: list[str] = []

    if not _has_search_investigation_for(profile, career):
        actions.append(f"Investigate {career.name} through Search Intelligence.")

    if not _has_github_evidence(profile):
        actions.append("Upload your latest projects through GitHub Intelligence to add real skill evidence.")

    top_mentor = _top_active(profile.mentor_matches, name_attr="mentor_name")
    if top_mentor:
        actions.append(f"Connect with {top_mentor}, your strongest current mentor match.")
    else:
        actions.append("Run Mentor Match to find mentors aligned with this path.")

    top_institution = _top_active(profile.college_matches, name_attr="institution_name")
    if top_institution:
        actions.append(f"Explore {top_institution}, your strongest current institution match.")
    else:
        actions.append("Run Institution Match to find universities aligned with this path.")

    if other_career_names:
        actions.append(f"Compare {career.name} with {', '.join(other_career_names)}.")

    return actions
