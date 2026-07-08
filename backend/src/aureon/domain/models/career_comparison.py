from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ComparisonDimension(BaseModel):
    """One row of a comparison matrix. The factual ``per_career`` values
    are read directly from ``Career.reality``/``Career.future_lens`` — no
    LLM call needed to produce them. Only ``why_it_matters_to_you`` is
    LLM-reasoned, grounded in the student's own Career DNA/Evidence
    Graph."""

    dimension: str
    per_career: dict[str, str]  # career_id -> a short factual value/summary
    why_it_matters_to_you: str


class CareerComparison(BaseModel):
    """One comparison run — append-only history (each comparison is its
    own real event; re-comparing the same pair later is a genuinely new,
    distinct moment worth keeping, not an overwrite)."""

    id: str
    career_ids: list[str]
    career_names: dict[str, str]
    dimensions: list[ComparisonDimension]
    #: One-line human-readable takeaway, produced by the same LLM call as
    #: `dimensions` — feeds a Decision Memory entry, not a second call.
    summary_reason: str
    missing_evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ParallelUniverseBranch(BaseModel):
    career_id: str
    career_name: str
    daily_work: str
    lifestyle: str
    growth: str
    challenges: str
    future_opportunities: str


class ParallelUniverseScenario(BaseModel):
    """A simulated side-by-side of exactly two possible futures — never a
    prediction, always framed as "based on your current profile."
    Append-only, same reasoning as CareerComparison."""

    id: str
    branches: list[ParallelUniverseBranch]
    framing_note: str = "Based on your current profile — not a prediction."
    missing_evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
