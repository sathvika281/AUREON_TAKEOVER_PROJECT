from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool

#: Fixed dimension keys — mirrors Decision Lab's COMPARISON_DIMENSIONS
#: pattern (agents/specialized/decision/schemas.py): the LLM only ever
#: supplies the "why" narrative for each; which dimensions exist and
#: their direction are always computed deterministically in
#: evidence_summary.py, never invented by the model.
PROGRESS_DIMENSIONS = [
    "exploration",
    "career_clarity",
    "decision_confidence",
    "reflection_consistency",
    "skill_development",
]


class DimensionReasoningOutput(BaseModel):
    dimension: str = Field(description=f"Must be one of: {', '.join(PROGRESS_DIMENSIONS)}")
    reasoning: str = Field(
        description="Explains WHY this dimension moved the way it did, grounded only in the evidence given"
    )


class PriorityOutput(BaseModel):
    rank: int
    action: str = Field(description="One concrete next action, e.g. 'Explore two more AI research careers'")
    evidence: str = Field(description="The specific evidence this action is grounded in — never a bare tip")


class ProgressTurnOutput(BaseModel):
    """Structured contract for one Progress Intelligence report. The
    per-dimension directions and evidence counts are already known
    (computed deterministically in evidence_summary.py) — this call only
    produces the personalized narrative, strengths/slowdowns, and a
    ranked list of evidence-cited next priorities."""

    overall_narrative: str
    dimension_reasoning: list[DimensionReasoningOutput] = Field(default_factory=list)
    growing_strengths: list[str] = Field(default_factory=list)
    areas_slowing_down: list[str] = Field(default_factory=list)
    recent_improvements: list[str] = Field(default_factory=list)
    next_priorities: list[PriorityOutput] = Field(default_factory=list)


PROGRESS_TOOL = LLMTool(
    name="record_progress_report",
    description="Record the reasoning behind a student's Progress Intelligence report, grounded only in the evidence given.",
    parameters=ProgressTurnOutput.model_json_schema(),
)
