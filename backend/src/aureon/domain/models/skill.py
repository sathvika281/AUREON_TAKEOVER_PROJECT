"""Responsibility: the Skill Knowledge Base's own data shape. A Skill is
the connective tissue Career/Opportunity/Project/Mentor/Learning Resource
all point at instead of each carrying an independent free-text list —
see docs/AUREON_DATA_ARCHITECTURE.md §3 for the full rationale.

Unlike Trend/CareerWorld/Opportunity, a Skill is factual taxonomy (a
name and a real definition), not illustrative composite narrative — it
carries no ``source_note`` disclaimer for the same reason a dictionary
entry doesn't need one.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

SkillCategory = Literal["technical", "domain_knowledge", "soft_skill", "tool"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Skill(BaseModel):
    """One entry in the Skill Knowledge Base. ``evidence_types_that_count``
    is deliberately a plain list of short human-readable descriptions
    (e.g. "a completed project," "a verified certificate") rather than a
    structured scoring system — Sprint 1 introduces the entity and one
    real promoted relationship (Career), not a skill-evidence scoring
    engine; see docs/SPRINT_1.md's explicit out-of-scope list.
    """

    id: str
    name: str
    category: SkillCategory
    description: str
    #: Optional nesting (e.g. "React" under "Frontend Development") —
    #: never a forced rigid taxonomy; most skills have none.
    parent_skill_id: str | None = None
    related_skill_ids: list[str] = Field(default_factory=list)
    #: What honestly counts as proof of this skill — carries forward the
    #: evidence-honesty discipline established elsewhere in this codebase
    #: (e.g. life_mission_engine.py): a skill is never "acquired" just
    #: because a student said so in conversation.
    evidence_types_that_count: list[str] = Field(default_factory=list)
    #: False marks an alias later merged into a canonical entry — skill
    #: taxonomies always accumulate near-duplicates; planned for from the
    #: start rather than retrofitted once the catalog is large.
    is_canonical: bool = True

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
