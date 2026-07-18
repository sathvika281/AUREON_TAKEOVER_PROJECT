"""Responsibility: the shared career-timeline sub-model used by both
`Mentor` (an expert's own journey) and `CareerStory` (a Journey Story's
timeline, Connect Batch 2). Lives in its own module specifically so
neither `mentor.py` nor `career.py` has to import the other for it —
avoids a circular import between the two while still reusing one real
model, never two near-identical ones.
"""

from typing import Literal

from pydantic import BaseModel

CareerJourneyStage = Literal[
    "school",
    "university",
    "internship",
    "first_job",
    "career_transition",
    "failure",
    "turning_point",
    "promotion",
    "current_role",
]


class CareerJourneyMilestone(BaseModel):
    """One beat in a real career timeline — school through current role,
    including transitions and setbacks. Ordered as authored, never
    reordered/inferred."""

    stage: CareerJourneyStage
    label: str
    description: str
    year_label: str
