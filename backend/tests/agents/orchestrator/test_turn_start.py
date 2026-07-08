from aureon.agents.orchestrator.graph import turn_start_node
from aureon.agents.state import new_state
from aureon.domain.models.agent_output import AgentOutput


def test_turn_start_resets_per_turn_fields_but_preserves_cross_turn_state():
    state = new_state(conversation_id="c1", student_id="s1")
    # Simulate leftovers from a previous turn that should be cleared.
    state["agent_outputs"] = {"discovery": AgentOutput(agent_name="discovery")}
    state["active_agent"] = "discovery"
    state["planner_rationale"] = "previous turn's reasoning"
    state["should_end"] = True
    state["hop_count"] = 2
    state["turn_count"] = 3
    # Cross-turn state that must survive.
    state["why_probe_state"] = {"wants_to_be_doctor": 1}
    state["confidence_score"] = 0.4

    result = turn_start_node(state)

    assert result["agent_outputs"] == {}
    assert result["active_agent"] is None
    assert result["planner_rationale"] is None
    assert result["should_end"] is False
    assert result["hop_count"] == 0
    assert result["turn_count"] == 4
    assert result["why_probe_state"] == {"wants_to_be_doctor": 1}
    assert result["confidence_score"] == 0.4
