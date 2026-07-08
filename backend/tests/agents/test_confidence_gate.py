import aureon.agents.specialized  # noqa: F401  (registers every agent)
from aureon.agents.confidence_gate import apply_confidence_gate
from aureon.agents.state import new_state
from aureon.shared.types import AgentName, Mode


def _state_with_route(active_agent: str, confidence_score: float):
    state = new_state(conversation_id="c1", student_id="s1")
    state["active_agent"] = active_agent
    state["confidence_score"] = confidence_score
    state["mode"] = Mode.RECOMMENDATION.value
    return state


def test_gate_blocks_recommendation_stage_agent_below_floor(settings):
    state = _state_with_route(AgentName.ROADMAP.value, confidence_score=0.1)

    result = apply_confidence_gate(state, settings=settings)

    assert result["active_agent"] == AgentName.DISCOVERY.value
    assert result["mode"] == Mode.EXPLORATION.value


def test_gate_allows_recommendation_stage_agent_above_floor(settings):
    state = _state_with_route(
        AgentName.ROADMAP.value,
        confidence_score=settings.min_recommendation_confidence + 0.1,
    )

    result = apply_confidence_gate(state, settings=settings)

    assert result["active_agent"] == AgentName.ROADMAP.value


def test_gate_never_blocks_mentor_regardless_of_confidence(settings):
    state = _state_with_route(AgentName.MENTOR.value, confidence_score=0.0)

    result = apply_confidence_gate(state, settings=settings)

    assert result["active_agent"] == AgentName.MENTOR.value
