from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class SimulatedJourneyPhaseOutput(BaseModel):
    phase: str = Field(description='One of: "Year 1", "Year 2", "Year 3+"')
    focus: str
    milestones: list[str] = Field(default_factory=list)


class TradeOffOutput(BaseModel):
    advantages: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    sacrifices: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class CareerSimulationTurnOutput(BaseModel):
    """One independently-generated career simulation. The 9 fact
    dimensions + 3 alignment dimensions are already real and deterministic
    (simulation_facts.py + simulation_alignment.py) — this call only
    reasons about the illustrative journey on top of them, never
    re-deriving or contradicting the facts it was given."""

    learning_journey: str
    expected_milestones: list[str] = Field(default_factory=list)
    timeline: list[SimulatedJourneyPhaseOutput] = Field(default_factory=list)
    trade_offs: TradeOffOutput = Field(default_factory=TradeOffOutput)
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


SIMULATION_TOOL = LLMTool(
    name="record_career_simulation",
    description="Record one independent, evidence-informed simulation of what a career path could look like — never a prediction or a guarantee.",
    parameters=CareerSimulationTurnOutput.model_json_schema(),
)


class DecisionInsightsTurnOutput(BaseModel):
    """Cross-career synthesis, reading only the already-generated
    independent simulations. Encourages exploration, never forces a
    decision."""

    strongest_match_career_id: str | None = Field(
        default=None, description="Must be one of the given career IDs, or null — never invented."
    )
    why: str = ""
    possible_risks: list[str] = Field(default_factory=list)
    questions_to_explore: list[str] = Field(default_factory=list)
    recommended_next_investigation: str = ""
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


DECISION_INSIGHTS_TOOL = LLMTool(
    name="record_decision_insights",
    description="Record cross-career decision insights synthesized from already-generated independent career simulations.",
    parameters=DecisionInsightsTurnOutput.model_json_schema(),
)
