from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class InvestigationFinding(BaseModel):
    """One claim the Cross-Verification step produced, always grounded in
    real collected Evidence — never a bare assertion."""

    claim: str
    status: Literal["supported", "contradicted", "mixed", "insufficient_evidence"]
    citing_sources: list[str] = Field(default_factory=list)
    explanation: str


class CareerInvestigationRecord(BaseModel):
    """One Multi-Source Search Intelligence investigation — append-only
    history, same reasoning as CareerComparison/ParallelUniverseScenario:
    each investigation is its own real event, never overwritten. This is
    also the "previous investigations" memory a later investigation's
    Mission can be preloaded with via
    ``MissionOrchestrator.create_mission(..., prior_artifacts=...)``."""

    id: str
    question: str
    overall_summary: str
    findings: list[InvestigationFinding] = Field(default_factory=list)
    related_career_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
