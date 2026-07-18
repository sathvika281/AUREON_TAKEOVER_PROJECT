"""Responsibility: Life Mission Engine — infers which real-world-impact
missions a student resonates with from real accumulated evidence
(Career DNA, Career Experiments, Reflection Journal, the Evidence
Graph), with a tier (never a score) and a trend derived from real
timestamps. Pure and stateless: recomputed on every call, no LLM, no
persistence — same philosophy as talent_pattern_engine.py. Purely
data-driven over `related_tags`; a new LifeMission row needs no change
here.

Trend classification mirrors the recent-vs-previous bucket-count
comparison already established in
agents/specialized/growth/evidence_summary.py's `_direction_from_counts`
— reimplemented locally (that helper is private and agent-scoped, not
meant for cross-module import), using wider 30/90-day windows since
purpose discovery evolves slower than weekly progress check-ins.
"""

from datetime import datetime, timedelta

from aureon.domain.models.experiment import ExperimentEvidence
from aureon.domain.models.life_mission import (
    LifeMission,
    MissionEvidenceItem,
    MissionResonance,
    MissionTier,
    MissionTrend,
)
from aureon.domain.models.student_profile import StudentProfile

RECENT_WINDOW_DAYS = 30
PREVIOUS_WINDOW_DAYS = 90


def _evidence_from_career_dna(mission: LifeMission, profile: StudentProfile) -> list[MissionEvidenceItem]:
    tags = [tag.lower() for tag in mission.related_tags]
    items = []
    for trait_name, signal in profile.career_dna.traits.items():
        haystack = f"{trait_name} {signal.summary}".lower()
        if signal.summary and any(tag in haystack for tag in tags):
            items.append(
                MissionEvidenceItem(
                    source="career_dna",
                    description=f"Career DNA shows a real signal connected to {mission.name.lower()}: {signal.summary}",
                    observed_at=signal.updated_at,
                )
            )
    return items


def _has_genuine_engagement(evidence: ExperimentEvidence) -> bool:
    """Completion alone is not evidence a mission resonates — a completed
    experience only supports a mission's resonance when the student
    actually reported something real: genuine positive engagement, or a
    real reflection. Absence of any signal is treated as 'not enough to
    say,' the same fairness discipline ExperimentEvidence itself already
    applies to each individual flag."""
    return (
        evidence.enjoyment
        or evidence.curiosity
        or evidence.persistence
        or evidence.confidence
        or bool(evidence.reflection.strip())
    )


def _evidence_from_experiments(mission: LifeMission, profile: StudentProfile) -> list[MissionEvidenceItem]:
    tags = [tag.lower() for tag in mission.related_tags]
    items = []
    for completion in profile.career_experiments:
        if not _has_genuine_engagement(completion.evidence):
            continue
        haystack = " ".join([completion.experiment_title, completion.related_world, *completion.target_traits]).lower()
        if any(tag in haystack for tag in tags):
            items.append(
                MissionEvidenceItem(
                    source="experiment",
                    description=f"Completed '{completion.experiment_title}', an experience connected to {mission.name.lower()}",
                    observed_at=completion.completed_at,
                )
            )
    return items


def _evidence_from_reflections(mission: LifeMission, profile: StudentProfile) -> list[MissionEvidenceItem]:
    tags = [tag.lower() for tag in mission.related_tags]
    items = []
    for entry in profile.reflection_journal:
        if not entry.response:
            continue
        lowered = entry.response.lower()
        if any(tag in lowered for tag in tags):
            items.append(
                MissionEvidenceItem(
                    source="reflection",
                    description=f"A reflection response touched on {mission.name.lower()}",
                    observed_at=entry.answered_at or entry.created_at,
                )
            )
    return items


#: experiment_result.py::complete_experiment writes this exact fallback
#: string into the Evidence Graph whenever a completion reports no
#: genuine flags and no reflection — real, honest evidence for the
#: general Evidence Graph (e.g. Hidden Potential's trait evidence), but
#: not a genuine signal that a *mission* resonates: without this
#: exclusion, a mission-relevant experiment title alone (e.g. "Analyze a
#: climate problem") would leak through here even on a completion
#: _evidence_from_experiments already correctly excluded above.
_GENERIC_COMPLETION_PREFIX = "Completed '"


def _evidence_from_evidence_graph(mission: LifeMission, profile: StudentProfile) -> list[MissionEvidenceItem]:
    """Maps to "conversations" — the Evidence Graph is the durable,
    already-established interpreted trace of conversations used
    everywhere else in this codebase; there is no separate raw-transcript
    input."""
    tags = [tag.lower() for tag in mission.related_tags]
    items = []
    for record in profile.evidence_graph:
        if record.source == "experiment" and record.text.startswith(_GENERIC_COMPLETION_PREFIX):
            continue
        lowered = record.text.lower()
        if any(tag in lowered for tag in tags):
            items.append(
                MissionEvidenceItem(
                    source="evidence_graph",
                    description=f"A conversation surfaced something connected to {mission.name.lower()}: {record.text}",
                    observed_at=record.created_at,
                )
            )
    return items


def _tier_for(evidence: list[MissionEvidenceItem]) -> MissionTier | None:
    if not evidence:
        return None
    source_types = {item.source for item in evidence}
    if len(evidence) >= 3 and len(source_types) >= 2:
        return "strong"
    if len(evidence) >= 2:
        return "growing"
    return "still_emerging"


def _trend_for(evidence: list[MissionEvidenceItem], now: datetime) -> MissionTrend:
    if not evidence:
        return "not_enough_evidence"

    recent = [e for e in evidence if (now - e.observed_at).days <= RECENT_WINDOW_DAYS]
    previous = [
        e for e in evidence if RECENT_WINDOW_DAYS < (now - e.observed_at).days <= PREVIOUS_WINDOW_DAYS
    ]

    if not recent and not previous:
        return "not_enough_evidence"
    if len(recent) > len(previous):
        return "emerging"
    if len(recent) < len(previous):
        return "fading"
    return "steady"


_SOURCE_LABELS: dict[str, str] = {
    "career_dna": "Career DNA",
    "experiment": "recent experiences",
    "reflection": "reflections",
    "evidence_graph": "conversations",
}


def _build_explanation(mission: LifeMission, evidence: list[MissionEvidenceItem], tier: MissionTier) -> str:
    source_types = sorted({item.source for item in evidence}, key=list(_SOURCE_LABELS).index)
    source_phrase = " and ".join(_SOURCE_LABELS[s] for s in source_types)
    if tier == "strong":
        return f"Aureon has repeatedly observed real interest in {mission.name.lower()} across your {source_phrase}."
    if tier == "growing":
        return f"Aureon has started to notice real signs of interest in {mission.name.lower()} in your {source_phrase}."
    return f"Aureon has noticed one early sign of interest in {mission.name.lower()} in your {source_phrase} — not enough yet to say much, but worth watching."


def analyze_life_missions(
    profile: StudentProfile, missions: list[LifeMission], *, now: datetime
) -> list[MissionResonance]:
    resonances: list[MissionResonance] = []
    for mission in missions:
        evidence: list[MissionEvidenceItem] = []
        evidence.extend(_evidence_from_career_dna(mission, profile))
        evidence.extend(_evidence_from_experiments(mission, profile))
        evidence.extend(_evidence_from_reflections(mission, profile))
        evidence.extend(_evidence_from_evidence_graph(mission, profile))

        tier = _tier_for(evidence)
        if tier is None:
            continue

        resonances.append(
            MissionResonance(
                mission=mission,
                tier=tier,
                trend=_trend_for(evidence, now),
                explanation=_build_explanation(mission, evidence, tier),
                evidence=evidence,
            )
        )
    return resonances
