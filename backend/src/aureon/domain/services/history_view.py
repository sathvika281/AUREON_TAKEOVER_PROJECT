from dataclasses import dataclass
from datetime import datetime

from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import AgentName

"""Investigation History (V12) — a pure read-aggregation over already-
persisted records, same philosophy as decision_timeline.py: every item
traces to a real, already-stored investigation. Status is always
"completed" because every pipeline this aggregates over only ever
persists on success — a failed/insufficient-evidence run leaves the
profile untouched, so there is nothing else to honestly report."""


@dataclass
class HistoryItem:
    id: str
    mission_name: str
    mission_type: str
    owning_specialist: str
    timestamp: datetime
    status: str
    artifact_id: str


def build_history_items(profile: StudentProfile) -> list[HistoryItem]:
    items: list[HistoryItem] = []

    for comp in profile.career_comparisons:
        names = " vs ".join(comp.career_names.get(cid, cid) for cid in comp.career_ids)
        items.append(HistoryItem(
            id=comp.id, mission_name=f"Compared {names}", mission_type="career_comparison",
            owning_specialist=AgentName.DECISION.value, timestamp=comp.created_at,
            status="completed", artifact_id=comp.id,
        ))

    for scenario in profile.parallel_universe_scenarios:
        names = " vs ".join(b.career_name for b in scenario.branches)
        items.append(HistoryItem(
            id=scenario.id, mission_name=f"Simulated futures: {names}", mission_type="parallel_universe",
            owning_specialist=AgentName.DECISION.value, timestamp=scenario.created_at,
            status="completed", artifact_id=scenario.id,
        ))

    for inv in profile.career_investigations:
        items.append(HistoryItem(
            id=inv.id, mission_name=inv.question, mission_type="search_investigation",
            owning_specialist=AgentName.CAREER_INTELLIGENCE.value, timestamp=inv.created_at,
            status="completed", artifact_id=inv.id,
        ))

    for sim in profile.career_simulations:
        names = ", ".join(sim.career_names.get(cid, cid) for cid in sim.career_ids)
        items.append(HistoryItem(
            id=sim.id, mission_name=f"Simulated {names}", mission_type="career_simulation",
            owning_specialist=AgentName.DECISION.value, timestamp=sim.created_at,
            status="completed", artifact_id=sim.id,
        ))

    for repo in profile.github_investigations:
        items.append(HistoryItem(
            id=repo.id, mission_name=f"Investigated {repo.owner}/{repo.repo}", mission_type="github_investigation",
            owning_specialist=AgentName.DISCOVERY.value, timestamp=repo.created_at,
            status="completed", artifact_id=repo.id,
        ))

    for doc in profile.document_investigations:
        items.append(HistoryItem(
            id=doc.id, mission_name=f"Analyzed {doc.filename}", mission_type="document_investigation",
            owning_specialist=doc.owning_specialist, timestamp=doc.created_at,
            status="completed", artifact_id=doc.id,
        ))

    for match in profile.mentor_matches:
        items.append(HistoryItem(
            id=match.id, mission_name=f"Matched with {match.mentor_name}", mission_type="mentor_match",
            owning_specialist=AgentName.MENTOR.value, timestamp=match.created_at,
            # artifact_id is the mentor's catalog id, not the match record's
            # own id — the MentorMatchDTO the frontend already has never
            # exposes the latter, only mentor_id/mentor_name.
            status="completed", artifact_id=match.mentor_id,
        ))

    for match in profile.college_matches:
        items.append(HistoryItem(
            id=match.id, mission_name=f"Matched with {match.institution_name}", mission_type="institution_match",
            owning_specialist=AgentName.INSTITUTION.value, timestamp=match.created_at,
            status="completed", artifact_id=match.institution_id,
        ))

    items.sort(key=lambda i: i.timestamp, reverse=True)
    return items
