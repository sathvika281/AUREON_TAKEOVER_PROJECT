from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.experiment import Experiment

LearningStyleTier = Literal["still_emerging", "growing", "strong"]
LearningStyleEvidenceSource = Literal["career_dna", "experiment", "reflection", "evidence_graph", "hidden_potential"]


class LearningStyle(BaseModel):
    """One entry in the Learning Style Discovery catalog — one of the 12
    real learning dimensions. Data, not prompt text — same illustrative-
    composite honesty convention as every other seeded knowledge base.
    Purely data-driven: domain/services/learning_style_evidence.py reads
    only `keywords`/`name`, never a style's identity, so a new dimension
    is a seed-row insert, never a code change."""

    id: str
    name: str
    description: str
    strengths: list[str] = Field(default_factory=list)
    excels_in: list[str] = Field(default_factory=list)
    common_struggles: list[str] = Field(default_factory=list)
    study_strategies: list[str] = Field(default_factory=list)
    note_taking_techniques: list[str] = Field(default_factory=list)
    memory_strategies: list[str] = Field(default_factory=list)
    active_learning_methods: list[str] = Field(default_factory=list)
    project_ideas: list[str] = Field(default_factory=list)
    practice_routines: list[str] = Field(default_factory=list)
    collaboration_techniques: list[str] = Field(default_factory=list)
    learning_environments: list[str] = Field(default_factory=list)
    productivity_systems: list[str] = Field(default_factory=list)
    recommended_books: list[str] = Field(default_factory=list)
    research_backed_resources: list[str] = Field(default_factory=list)
    online_courses: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    ways_to_strengthen: list[str] = Field(default_factory=list)
    #: Cross-reference tags used by learning_style_evidence.py's matching
    #: heuristic — case-insensitive substring overlap against real
    #: student signal fragments.
    keywords: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite overview compiled for exploration — real, "
        "research-backed techniques and resources, not a continuously "
        "verified or exhaustive directory."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningStyleEvidenceItem(BaseModel):
    """A single real, concrete fact backing a LearningStylePattern —
    never a generic platitude. Same shape as domain/models/talent.py's
    TalentEvidenceItem, applied to a different evidence domain."""

    source: LearningStyleEvidenceSource
    description: str
    observed_at: datetime


class LearningStylePattern(BaseModel):
    """Output of
    domain/services/learning_style_analysis_service.py::analyze_learning_styles.
    ``tier`` is never a numeric score and never claims certainty; a
    student can show several styles at once, none exclusive of another."""

    style: LearningStyle
    tier: LearningStyleTier
    explanation: str
    evidence: list[LearningStyleEvidenceItem]
    recommended_experiments: list[Experiment] = Field(default_factory=list)
