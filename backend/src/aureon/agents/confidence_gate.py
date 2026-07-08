from aureon.agents.registry import AgentRegistry
from aureon.agents.state import AureonState
from aureon.core.config import Settings
from aureon.shared.types import AgentName, Mode


def apply_confidence_gate(state: AureonState, *, settings: Settings) -> AureonState:
    """Deterministic safety floor enforcing "MUST NOT recommend careers on
    low confidence" at the code level, not as a prompt instruction.

    Runs unconditionally after the planner has chosen a route and before
    that agent node executes. If the chosen agent is recommendation-stage
    (Career Intelligence, Decision, Roadmap — flagged via
    ``BaseAgent.is_recommendation_stage``) and the student's confidence
    score is below ``settings.min_recommendation_confidence``, the route is
    overridden back to Discovery/Exploration regardless of the orchestrator
    LLM's own reasoning. Mentor is deliberately NOT recommendation-stage:
    human handoff must stay reachable at any confidence level.
    """
    chosen = state.get("active_agent")
    if chosen is None:
        return state

    descriptor = next(
        (d for d in AgentRegistry.describe_all() if d.name == chosen), None
    )
    if descriptor is None or not descriptor.is_recommendation_stage:
        return state

    if state["confidence_score"] >= settings.min_recommendation_confidence:
        return state

    state["active_agent"] = AgentName.DISCOVERY.value
    state["mode"] = Mode.EXPLORATION.value
    return state
