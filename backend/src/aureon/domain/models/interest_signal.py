from datetime import datetime
from typing import Literal

from pydantic import BaseModel

InterestEvidenceSource = Literal[
    "world_signal", "experiment", "reflection", "evidence_graph", "life_missions", "hidden_potential",
]


class InterestEvidenceItem(BaseModel):
    """A single real, concrete fact backing a RelevantInterest — never a
    generic platitude."""

    source: InterestEvidenceSource
    description: str
    observed_at: datetime


class RelevantInterest(BaseModel):
    """Output of domain/services/interest_signal_engine.py::
    analyze_relevant_interests — a real, dynamically-discovered topic the
    student has genuine evidence for, used by Decision Lab's "Relevant
    Interests" strength signal and its Career Comparison "Interest
    alignment" dimension. ``topic`` is a real discovered string, never a
    fixed catalog id."""

    topic: str
    explanation: str
    evidence: list[InterestEvidenceItem]
