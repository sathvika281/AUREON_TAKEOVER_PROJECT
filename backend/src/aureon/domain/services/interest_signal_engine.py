"""Responsibility: Interest Signal Engine — discovers the real, dynamic
topic universe a student has actually touched (never a fixed catalog)
and gathers real, timestamped evidence per topic, then composes that
into a plain, evidence-grounded list of relevant interests. Reuses
Missing Worlds/Life Missions/Hidden Potential's own already-computed
outputs as additional evidence — those engines are called once each by
the caller and passed in here, never re-derived. Consumed by Decision
Lab (`decision_workspace_service.py`'s "Relevant Interests" strength
signal and `decision_comparison_extra_dimensions.py`'s "Interest
alignment" comparison dimension) — deliberately carries no lifecycle/
bucket classification and no resource-catalog matching, since neither
is ever displayed by its one real consumer.
"""

from aureon.domain.models.interest_signal import InterestEvidenceItem, RelevantInterest
from aureon.domain.models.life_mission import MissionResonance
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentPattern
from aureon.domain.services.missing_worlds_engine import WorldExploration

_SOURCE_LABELS: dict[str, str] = {
    "world_signal": "your real World Signals",
    "evidence_graph": "conversations",
    "reflection": "reflections",
    "experiment": "Experience Lab",
    "life_missions": "Life Missions",
    "hidden_potential": "Hidden Potential",
}


def _overlaps(topic: str, text: str) -> bool:
    if not topic or not text:
        return False
    lowered_topic = topic.lower()
    lowered_text = text.lower()
    return lowered_topic in lowered_text or lowered_text in lowered_topic


def discover_topics(
    profile: StudentProfile,
    world_explorations: list[WorldExploration],
    mission_resonances: list[MissionResonance],
    talent_patterns: list[TalentPattern],
) -> list[str]:
    """The union of every real topic string the student has actually
    touched — free-text interests, World Signal names, Experience Lab
    world tags, Missing Worlds' explored/partially-explored worlds, Life
    Missions' resonant missions, and Hidden Potential's strong talents.
    """
    topics: set[str] = set()
    topics.update(t for t in profile.interests if t)
    topics.update(s.world for s in profile.discovery_onboarding.world_signals)
    topics.update(c.related_world for c in profile.career_experiments if c.related_world)
    topics.update(
        e.world.name for e in world_explorations if e.level in ("explored", "partially_explored")
    )
    topics.update(r.mission.name for r in mission_resonances)
    #: TalentPattern's real tier vocabulary is still_discovering/emerging/
    #: growing (Discover Batch 2) — "growing" is its top tier, not "strong".
    topics.update(
        p.talent.replace("_", " ").title() for p in talent_patterns if p.tier == "growing"
    )
    return sorted(topics)


def evidence_for_topic(
    topic: str,
    profile: StudentProfile,
    mission_resonances: list[MissionResonance],
    talent_patterns: list[TalentPattern],
) -> list[InterestEvidenceItem]:
    items: list[InterestEvidenceItem] = []

    for signal in profile.discovery_onboarding.world_signals:
        if _overlaps(topic, signal.world):
            items.append(
                InterestEvidenceItem(
                    source="world_signal",
                    description=f"A real, reinforced World Signal for {signal.world}",
                    observed_at=signal.last_reinforced,
                )
            )

    for record in profile.evidence_graph:
        if _overlaps(topic, record.text):
            items.append(
                InterestEvidenceItem(
                    source="evidence_graph",
                    description=f"A conversation touched on {topic}: {record.text}",
                    observed_at=record.created_at,
                )
            )

    for entry in profile.reflection_journal:
        if entry.response and _overlaps(topic, entry.response):
            items.append(
                InterestEvidenceItem(
                    source="reflection", description=f"A reflection touched on {topic}",
                    observed_at=entry.answered_at or entry.created_at,
                )
            )

    for completion in profile.career_experiments:
        haystack = " ".join([completion.experiment_title, completion.related_world, *completion.target_traits])
        if _overlaps(topic, haystack):
            items.append(
                InterestEvidenceItem(
                    source="experiment",
                    description=f"Completed '{completion.experiment_title}', connected to {topic}",
                    observed_at=completion.completed_at,
                )
            )

    #: Reused verbatim from Life Missions' own real, timestamped
    #: evidence — never re-derived.
    for resonance in mission_resonances:
        if _overlaps(topic, resonance.mission.name):
            for item in resonance.evidence:
                items.append(
                    InterestEvidenceItem(
                        source="life_missions", description=f"Life Missions noticed: {item.description}",
                        observed_at=item.observed_at,
                    )
                )

    #: Reused verbatim from Hidden Potential's Talent Pattern Engine.
    for pattern in talent_patterns:
        if _overlaps(topic, pattern.talent.replace("_", " ")):
            for item in pattern.evidence:
                items.append(
                    InterestEvidenceItem(
                        source="hidden_potential", description=f"Hidden Potential noticed: {item.description}",
                        observed_at=item.observed_at,
                    )
                )

    return items


def _build_explanation(evidence: list[InterestEvidenceItem]) -> str:
    sources = {e.source for e in evidence}
    source_phrase = " and ".join(_SOURCE_LABELS.get(s, s) for s in sorted(sources))
    return f"A real, recurring interest — seen across {source_phrase}."


def analyze_relevant_interests(
    profile: StudentProfile,
    world_explorations: list[WorldExploration],
    mission_resonances: list[MissionResonance],
    talent_patterns: list[TalentPattern],
) -> list[RelevantInterest]:
    """Real topics the student has genuine evidence for — no lifecycle
    classification, no resource-catalog matching, no suggested activity:
    Decision Lab (this function's one real consumer) never displays any
    of those, so none are computed."""
    topics = discover_topics(profile, world_explorations, mission_resonances, talent_patterns)

    interests: list[RelevantInterest] = []
    for topic in topics:
        evidence = evidence_for_topic(topic, profile, mission_resonances, talent_patterns)
        if not evidence:
            continue
        interests.append(RelevantInterest(topic=topic, explanation=_build_explanation(evidence), evidence=evidence))
    return interests
