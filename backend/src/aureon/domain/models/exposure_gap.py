from typing import Literal

from pydantic import BaseModel, Field


class ExposureGapInsight(BaseModel):
    """Opportunity Equality's own dimension — deliberately separate from
    Opportunity Hub's ``OpportunityFitResult`` (never merged into its
    ``overall_score``/``rank``, same precedent as Opportunity Hub's own
    Opportunity Cost). ``likelihood_of_self_discovery`` is the real
    signal ranking is built on: "low" means genuinely easy to miss —
    exactly what Opportunity Equality exists to surface."""

    likelihood_of_self_discovery: Literal["low", "medium", "high"]
    #: Hedged language always — "could be," "believes," never asserted
    #: certainty. Cites real, named contributing factors only.
    why_shown: str
    contributing_factors: list[str] = Field(default_factory=list)
