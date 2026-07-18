"""Responsibility: read/write Career Memory through plain functions over
a ``StudentProfile`` — the ``domain/services/decision_memory.py``
convention (no class, no separate repository). Owns: every ``get_*``/
``record_*`` function below; each is the entire public surface (no
private helpers needed yet). Does NOT own: ``CareerMemory``'s shapes
(``domain/models/career_memory.py``) or ``StudentProfile``'s own fields,
which this module only reads. Consumed by: ``BuildOrchestrator`` (via
the Event Bus from Milestone C onward) and, in the future, any agent
that needs the student's cross-domain memory.

Extension point — to add a new Career Memory field, add it to the
matching model in ``domain/models/career_memory.py`` and a matching
``get_*``/``record_*`` function here; never touch ``StudentProfile``'s
existing fields.
"""

from datetime import datetime
from typing import Literal

from aureon.domain.models.career_memory import (
    CareerMemory,
    Connection,
    ConnectionsMemory,
    EvidenceArtifact,
    GrowthMission,
    GrowthSkill,
    IdentityMemory,
    InterviewPracticeRecord,
    OpportunityEntry,
)
from aureon.domain.models.opportunity import OpportunityCategory
from aureon.domain.models.student_profile import StudentProfile


_STAGE_TO_ACADEMIC_LEVEL: dict[str, Literal["high_school", "undergraduate", "graduate"]] = {
    "School": "high_school", "College": "undergraduate", "Professional": "graduate",
}


def record_academic_level(profile: StudentProfile, *, stage: str) -> None:
    """Maps Discover Batch 1 onboarding's "Current Stage" answer onto
    the real, already-scored-against IdentityMemory.academic_level field
    (agents/specialized/opportunity/scoring.py already reads it) — the
    first real writer this field has ever had."""
    profile.foundation_memory.identity.academic_level = _STAGE_TO_ACADEMIC_LEVEL.get(stage)


def get_identity(profile: StudentProfile) -> IdentityMemory:
    """A facade, not a copy — everything but ``preferred_industries`` is
    already real on ``StudentProfile`` (``interests``, ``strengths``,
    ``values``, ``goals``, ``career_dna``); callers needing those read
    them directly from the profile. This only surfaces the one field
    Career Memory actually owns."""
    return profile.foundation_memory.identity


def record_evidence_artifact(
    profile: StudentProfile,
    *,
    kind: Literal["project", "github_repo", "resume", "certificate", "research_paper", "portfolio", "achievement"],
    ref_id: str,
    title: str,
    now: datetime,
) -> EvidenceArtifact:
    artifact = EvidenceArtifact(kind=kind, ref_id=ref_id, title=title, added_at=now)
    profile.foundation_memory.evidence.artifacts.append(artifact)
    return artifact


def record_opportunity_entry(
    profile: StudentProfile,
    *,
    interaction: Literal["viewed", "saved", "applied", "withdrawn", "completed"],
    category: OpportunityCategory,
    ref_id: str | None,
    opportunity_version: int | None,
    title: str,
    now: datetime,
) -> OpportunityEntry:
    entry = OpportunityEntry(
        interaction=interaction, category=category, ref_id=ref_id,
        opportunity_version=opportunity_version, title=title, occurred_at=now,
    )
    profile.foundation_memory.opportunities.entries.append(entry)
    return entry


def get_opportunity_interactions(profile: StudentProfile, ref_id: str) -> list[OpportunityEntry]:
    """Makes the append-only Opportunities log genuinely queryable —
    e.g. "has the student already applied to this one?" is the most
    recent entry's `interaction` for this `ref_id`. Chronological,
    oldest first, same convention as every other Career Memory list."""
    return [entry for entry in profile.foundation_memory.opportunities.entries if entry.ref_id == ref_id]


def record_opportunity_score(profile: StudentProfile, *, opportunity_id: str, score: float) -> None:
    """Writes the real state behind Opportunity Hub's score-smoothing —
    see agents/specialized/opportunity/scoring.py's stability mechanism."""
    profile.foundation_memory.opportunities.score_history[opportunity_id] = score


def record_growth_skill(
    profile: StudentProfile, *, skill: str, status: Literal["in_progress", "mastered"], evidence: str
) -> GrowthSkill:
    record = GrowthSkill(skill=skill, status=status, evidence=evidence)
    profile.foundation_memory.growth.skills.append(record)
    return record


def record_growth_mission(
    profile: StudentProfile, *, mission_id: str, status: Literal["current", "completed"]
) -> GrowthMission:
    record = GrowthMission(mission_id=mission_id, status=status)
    profile.foundation_memory.growth.missions.append(record)
    return record


def record_interview_practice(
    profile: StudentProfile, *, weak_areas: list[str], feedback_summary: str, now: datetime
) -> InterviewPracticeRecord:
    record = InterviewPracticeRecord(conducted_at=now, weak_areas=weak_areas, feedback_summary=feedback_summary)
    profile.foundation_memory.growth.interview_practice.append(record)
    return record


def get_connections(profile: StudentProfile) -> ConnectionsMemory:
    """Fully derived, zero storage — real ``Connection``s come straight
    from ``mentor_matches`` (active only) and, where one exists, the most
    recent resolved ``mentor_interactions`` handoff for the same mentor
    supplies ``conversation_summary``."""
    resolved_by_mentor = {
        handoff.mentor_id: handoff
        for handoff in profile.mentor_interactions
        if handoff.resolved and handoff.mentor_id
    }
    connections = [
        Connection(
            mentor_id=match.mentor_id,
            mentor_name=match.mentor_name,
            connected_at=match.updated_at,
            conversation_summary=(
                resolved_by_mentor[match.mentor_id].reason if match.mentor_id in resolved_by_mentor else None
            ),
        )
        for match in profile.mentor_matches
        if match.status == "active"
    ]
    return ConnectionsMemory(connections=connections)


def get_career_memory_snapshot(profile: StudentProfile) -> CareerMemory:
    """The one combined read every future consumer uses — real fields
    from ``foundation_memory`` plus the fully-derived Connections
    domain, assembled fresh every call (never cached, always current)."""
    return CareerMemory(
        identity=get_identity(profile),
        evidence=profile.foundation_memory.evidence,
        opportunities=profile.foundation_memory.opportunities,
        connections=get_connections(profile),
        growth=profile.foundation_memory.growth,
        updated_at=profile.foundation_memory.updated_at,
    )
