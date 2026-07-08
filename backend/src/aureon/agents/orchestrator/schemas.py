from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class PlannerDecision(BaseModel):
    next_agent: str | None = Field(
        description=(
            "Exact name of the agent that should act next this turn, or "
            "null to end the turn and send the reply already produced "
            "back to the student now."
        )
    )
    rationale: str = Field(description="Brief internal reasoning for this routing choice")


PLANNER_TOOL = LLMTool(
    name="route_turn",
    description=(
        "Decide which registered agent should act next this turn, or "
        "signal that the turn is complete."
    ),
    parameters=PlannerDecision.model_json_schema(),
)
