from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

ExperimentCategory = Literal[
    "read_abstract", "debug_code", "analyze_problem", "observe_design", "reflect_on_workflow"
]


class ExperimentEvidence(BaseModel):
    """Structured self-report signals, not a score. Each flag is a real
    reported signal; absence is never treated as negative, only as
    'not reported' — same fairness discipline as Opportunity Hub's
    missing-evidence handling."""

    enjoyment: bool = False
    curiosity: bool = False
    frustration: bool = False
    persistence: bool = False
    confidence: bool = False
    reflection: str = ""


class Experiment(BaseModel):
    """One entry in the Career Experiments catalog — real structured
    content, not prompt text, same honesty convention as every other
    seeded knowledge base (e.g. domain/models/trend.py)."""

    id: str
    title: str
    category: ExperimentCategory
    description: str
    instructions: str
    estimated_minutes: int
    age_appropriate_note: str
    #: One of the 7 onboarding World names — AI/Space/Healthcare/Business/
    #: Design/Arts/Psychology — used to reinforce the matching WorldSignal
    #: on completion (see domain/services/experiment_result.py).
    related_world: str
    #: Which of CareerDNA's TRAIT_NAMES/talent_pattern_engine's
    #: TALENT_NAMES this experiment can surface real evidence for.
    target_traits: list[str] = Field(default_factory=list)
    #: Editorial link to LifeMission.id — deliberately separate from the
    #: generous related_tags substring matching life_mission_engine.py
    #: already does for *evidence* gathering. This field decides curated
    #: UI grouping ("Mission Experiences"), which must be an intentional
    #: relationship, not accidental string overlap. Empty for ordinary
    #: career-oriented experiments.
    related_life_mission_ids: list[str] = Field(default_factory=list)
    reflection_prompt: str
    source_note: str = (
        "Illustrative composite activity for Aureon's Career Experiments — "
        "not a claim of a professionally-validated assessment."
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExperimentCompletion(BaseModel):
    """One real completion event. Denormalizes experiment_title/
    related_world/target_traits at completion time — same historical-
    truthfulness precedent as career_experience's ExpertSessionBooking/
    OpportunityEntry: a completion record stays truthful even if the
    catalog entry it references later changes."""

    id: str
    experiment_id: str
    experiment_title: str
    related_world: str
    target_traits: list[str]
    completed_at: datetime
    evidence: ExperimentEvidence
