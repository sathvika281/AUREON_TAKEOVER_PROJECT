from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

TrendCategory = Literal[
    "emerging_industry",
    "declining_industry",
    "future_technology",
    "skill_shift",
    "hiring_shift",
    "ai_influence",
    "research_direction",
]
TrendTimeHorizon = Literal["near_term", "mid_term", "long_term"]


class Trend(BaseModel):
    """One entry in the Global Trends Knowledge Base — industry/market-
    level, deliberately distinct from ``FutureLens`` (a single career's
    own static outlook narrative). Data, not prompt text — same
    illustrative-composite honesty convention as every other seeded
    knowledge base in this codebase, critical here specifically since
    trend/labor-market claims are exactly the kind of thing that could
    read as fabricated authority if unlabeled."""

    id: str
    title: str
    category: TrendCategory
    summary: str
    description: str
    affected_industries: list[str] = Field(default_factory=list)
    affected_skills: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)  # empty = global
    time_horizon: TrendTimeHorizon
    source_note: str = (
        "Illustrative composite trend for Aureon's Global Trends knowledge base — "
        "not a claim of live, currently-verified labor-market data."
    )

    #: Explore Polish Batch — additive, defaulted. Backfilled onto every
    #: trend via scripts/enrich_trends.py, not this original creation
    #: script. `key_milestones` is the "Timeline" section.
    key_milestones: list[str] = Field(default_factory=list)
    countries_leading: list[str] = Field(default_factory=list)
    affected_careers: list[str] = Field(default_factory=list)
    research_papers: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    startups: list[str] = Field(default_factory=list)
    government_initiatives: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
