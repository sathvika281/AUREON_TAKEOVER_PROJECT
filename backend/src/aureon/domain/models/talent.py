from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TalentTier = Literal["still_discovering", "emerging", "growing"]
TalentEvidenceSource = Literal["career_dna", "experiment", "reflection"]


class TalentEvidenceItem(BaseModel):
    """A single real, concrete fact backing a TalentPattern — never a
    generic platitude. This is the 'Talent Evidence Model' the Discover
    Batch 2 spec asks for."""

    source: TalentEvidenceSource
    description: str
    observed_at: datetime


class TalentPattern(BaseModel):
    """Output of domain/services/talent_pattern_engine.py::analyze_talents.
    ``tier`` is never a numeric score and never claims certainty —
    ``explanation`` must always cite the real evidence behind it."""

    talent: str
    tier: TalentTier
    explanation: str
    evidence: list[TalentEvidenceItem]
