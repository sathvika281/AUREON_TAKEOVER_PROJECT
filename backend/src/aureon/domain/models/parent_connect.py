"""Responsibility: Parent Connect's own data shape — a career explained
for a parent audience (`ParentCareerGuide`) and a seeded/live-askable
Q&A bank (`ParentQuestion`). Real, structured content, not prompt text,
same honesty convention as every other seeded knowledge base in this
codebase. Does NOT own Shared Sessions (`domain/models/shared_session.py`).
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

ParentQuestionCategory = Literal[
    "salary",
    "safety",
    "stability",
    "work_life_balance",
    "growth",
    "international",
    "career_switching",
    "other",
]


class ParentCareerGuide(BaseModel):
    """One entry per `Career` — a parent-framed explanation, deliberately
    distinct content from `Career.reality`/`Career.common_misconceptions`
    (same subject, different audience), never a duplicate."""

    id: str
    career_id: str
    common_misconceptions: list[str] = Field(default_factory=list)
    earning_reality: str
    career_stability: str
    work_life_balance: str
    growth_opportunities: str
    educational_pathways: list[str] = Field(default_factory=list)
    alternative_routes: list[str] = Field(default_factory=list)
    global_demand: str
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite guidance for Aureon's Parent Connect — "
        "not a claim of live, currently-verified labor-market data."
    )
    #: Connect restructuring — genuine translated content, not a display
    #: toggle. A Hindi/Telugu row is a real, separately-seeded row (own
    #: id), never the English row relabeled. See
    #: scripts/translate_parent_connect_content.py.
    language: str = "en"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParentQuestion(BaseModel):
    """One entry in the parent Q&A bank — either seeded (illustrative,
    real-concern-representative) or live-asked by a real parent, in
    which case `expert_response` starts empty pending a real reply."""

    id: str
    category: ParentQuestionCategory
    career_id: str | None = None
    question: str
    expert_response: str = ""
    responding_expert_id: str | None = None
    is_seeded: bool = True
    #: See ParentCareerGuide.language.
    language: str = "en"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
