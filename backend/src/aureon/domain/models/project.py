"""Responsibility: the Project Knowledge Base's own data shape. Distinct
from `Experiment` (domain/models/experiment.py) — Experiment answers
"did the student explore this," Project answers "did the student
demonstrate this." See docs/SPRINT_3.md's Design Checkpoint for the full
reasoning; the two stay structurally separate rather than merging into
one generic "activity" concept.

`difficulty_level` reuses `DifficultyLevel` from `domain.models.opportunity`
rather than defining a second, parallel enum — the same "prefer existing
patterns" reuse already applied to `OrganizationKind` in Sprint 2.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.opportunity import DifficultyLevel

#: What "completing" this project actually means to submit — determines
#: what the completion form asks for.
SubmissionType = Literal["github_repo", "writeup", "demo_link", "reflection_only"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(BaseModel):
    """One entry in the Project Knowledge Base — a real, attemptable
    build, not a short reflective activity (see Experiment for that)."""

    id: str
    title: str
    brief: str
    difficulty_level: DifficultyLevel
    estimated_hours: float
    #: Real edges into the Skill Knowledge Base — what this project
    #: genuinely builds/proves, and what a real completion produces
    #: evidence for.
    target_skill_ids: list[str] = Field(default_factory=list)
    related_career_ids: list[str] = Field(default_factory=list)
    #: Optional — only where a project genuinely resembles real work at a
    #: specific company; never forced onto every project.
    related_company_ids: list[str] = Field(default_factory=list)
    submission_type: SubmissionType = "reflection_only"

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class ProjectAttemptEvidence(BaseModel):
    """What a student submits to mark a Project attempted — structurally
    distinct from `ExperimentEvidence` (domain/models/experiment.py).
    Experiment captures self-reported *feeling* (enjoyment/curiosity/
    frustration/persistence/confidence); Project captures a *demonstrated
    artifact* (a real link) or a written account of what was built.
    Genuine-engagement gate: at least one of the two fields must carry
    real content — see complete_project_attempt() in
    domain/services/project_result.py."""

    artifact_url: str | None = None
    reflection: str = ""


class ProjectAttempt(BaseModel):
    """One real attempt/completion event. Denormalizes project_title/
    target_skill_ids at attempt time — same historical-truthfulness
    precedent as ExperimentCompletion: an attempt record stays truthful
    even if the catalog entry it references later changes."""

    id: str
    project_id: str
    project_title: str
    target_skill_ids: list[str]
    attempted_at: datetime
    evidence: ProjectAttemptEvidence
