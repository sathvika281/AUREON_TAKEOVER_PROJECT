from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool

#: Fixed dimension keys for Decision Lab's comparison matrix — the LLM
#: only ever supplies `why_it_matters_to_you` for each; the factual
#: `per_career` values are always read directly from Career.reality/
#: future_lens (see comparison_facts.py), never invented by the model.
COMPARISON_DIMENSIONS = [
    "work_style",
    "creativity",
    "research",
    "collaboration",
    "work_life_balance",
    "growth",
    "future_demand",
    "required_education",
    "skills",
    "lifestyle",
    "salary",
    "travel",
    "stress",
    "flexibility",
    "entrepreneurship_potential",
]


class ComparisonDimensionReasoning(BaseModel):
    dimension: str = Field(description=f"Must be one of: {', '.join(COMPARISON_DIMENSIONS)}")
    why_it_matters_to_you: str = Field(
        description="Grounded in the student's own Career DNA/evidence — never a generic statement"
    )


class ComparisonTurnOutput(BaseModel):
    """Structured contract for one Decision Lab comparison. The facts
    being compared are already known (read from the Career Knowledge
    Base) — this call only produces the personalized reasoning for each
    dimension plus an overall one-line takeaway."""

    reply_to_student: str
    dimension_reasoning: list[ComparisonDimensionReasoning] = Field(default_factory=list)
    summary_reason: str = Field(
        description="One-line, evidence-grounded takeaway comparing these careers for this specific student"
    )
    missing_evidence: list[str] = Field(default_factory=list)


COMPARISON_TOOL = LLMTool(
    name="record_career_comparison",
    description="Record the personalized reasoning behind a career comparison, dimension by dimension.",
    parameters=ComparisonTurnOutput.model_json_schema(),
)


class ParallelUniverseBranchOutput(BaseModel):
    career_id: str
    daily_work: str
    lifestyle: str
    growth: str
    challenges: str
    future_opportunities: str


class ParallelUniverseTurnOutput(BaseModel):
    """A simulated side-by-side of exactly two possible futures — never a
    prediction, always grounded in the student's current evidence and
    framed as "based on your current profile.\""""

    reply_to_student: str
    branches: list[ParallelUniverseBranchOutput] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)


PARALLEL_UNIVERSE_TOOL = LLMTool(
    name="record_parallel_universe_scenario",
    description="Record a simulated side-by-side of two possible futures, grounded in the student's evidence.",
    parameters=ParallelUniverseTurnOutput.model_json_schema(),
)
