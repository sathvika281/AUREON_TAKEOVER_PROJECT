"""Responsibility: Journey Stories' read-time composition — resolves
``CareerStory.career_id``/``linked_expert_id``/``linked_life_mission_id``
against their real catalogs, never denormalized onto the story row
itself (same discipline as ``expert_profile_service.py`` resolving
``career_ids``). Owns: ``build_journey_story_view``, ``personalize_stories``,
``record_story_reflection``. Does NOT own persistence
(``journey_story_repository.py``) or evidence/gap logic
(``decision_workspace_service.py``, unchanged by this batch). Consumed by:
``api/v1/journey_stories.py``.
"""

from dataclasses import dataclass
from datetime import datetime

from aureon.domain.models.career import Career, CareerStory
from aureon.domain.models.career_journey import CareerJourneyMilestone
from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.world_signal_alignment import compute_tag_alignment


@dataclass(frozen=True)
class LinkedExpertRef:
    id: str
    name: str
    profession: str


@dataclass(frozen=True)
class JourneyStoryView:
    id: str
    career_id: str
    career_name: str
    person_label: str
    background: str
    journey: str
    challenges: str
    turning_points: str
    advice: str
    lessons_learned: str
    trait_tags: list[str]
    timeline: list[CareerJourneyMilestone]
    career_switch: bool
    gap_year: bool
    uncertainty_period: str
    current_outcome: str
    industry: str
    story_type: str
    source_reference: str
    discovery_themes: list[str]
    linked_expert: LinkedExpertRef | None = None
    linked_life_mission_name: str | None = None


def build_journey_story_view(
    story: CareerStory,
    *,
    career: Career | None,
    linked_expert: Mentor | None = None,
    linked_mission: LifeMission | None = None,
) -> JourneyStoryView:
    return JourneyStoryView(
        id=story.id,
        career_id=story.career_id,
        career_name=career.name if career else "",
        person_label=story.person_label,
        background=story.background,
        journey=story.journey,
        challenges=story.challenges,
        turning_points=story.turning_points,
        advice=story.advice,
        lessons_learned=story.lessons_learned,
        trait_tags=story.trait_tags,
        timeline=story.timeline,
        career_switch=story.career_switch,
        gap_year=story.gap_year,
        uncertainty_period=story.uncertainty_period,
        current_outcome=story.current_outcome,
        industry=story.industry,
        story_type=story.story_type,
        source_reference=story.source_reference,
        discovery_themes=story.discovery_themes,
        linked_expert=(
            LinkedExpertRef(id=linked_expert.id, name=linked_expert.name, profession=linked_expert.profession)
            if linked_expert
            else None
        ),
        linked_life_mission_name=linked_mission.name if linked_mission else None,
    )


def personalize_stories(
    stories: list[CareerStory], world_signals: list[WorldSignal], *, limit: int = 3
) -> list[CareerStory]:
    """"Stories You May Relate To" — reuses ``compute_tag_alignment``
    verbatim (the same deterministic, real-signal-only utility Career
    Explorer/Exposure Universe/Opportunity Equality already use), never a
    new recommendation engine. Zero-alignment stories are excluded
    entirely rather than padded in — "you may relate to this" must mean
    there's real overlap, never a guess."""
    scored = [(story, compute_tag_alignment(story.trait_tags, world_signals)) for story in stories]
    relevant = [(story, score) for story, score in scored if score > 0]
    relevant.sort(key=lambda pair: -pair[1])
    return [story for story, _score in relevant[:limit]]


def record_story_reflection(
    profile: StudentProfile, *, prompt: str, response: str, now: datetime
) -> None:
    """Appends a real ``ReflectionEntry`` to the student's existing
    Reflection Journal — the same model/field
    ``decision_workspace_service.py::_has_relevant_reflection`` already
    reads, generically, regardless of where a reflection came from.
    Mutates ``profile`` in place; the caller persists (same contract as
    ``exposure_recommendation.py::record_exposure_interaction``).
    Reading a story writes nothing here — only an explicit, submitted
    reflection does, and it only becomes evidence later if its own
    content genuinely matches a career's terms (unchanged existing
    keyword-match logic, no new evidence pathway)."""
    profile.reflection_journal.append(
        ReflectionEntry(prompt=prompt, response=response, created_at=now, answered_at=now)
    )
