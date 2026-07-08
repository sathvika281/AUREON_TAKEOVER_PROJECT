import aureon.agents.specialized  # noqa: F401  (registers every agent)
from aureon.agents.orchestrator.planner_node import HOP_CAP, planner_node
from aureon.agents.state import new_state
from aureon.shared.types import AgentName
from tests.fakes import FakeLLMClient, tool_call_response


async def test_planner_routes_to_a_valid_registered_agent():
    llm = FakeLLMClient(
        [
            tool_call_response(
                "route_turn",
                {"next_agent": AgentName.DISCOVERY.value, "rationale": "student just said hello"},
            )
        ]
    )
    state = new_state(conversation_id="c1", student_id="s1")

    result = await planner_node(state, llm=llm)

    assert result["active_agent"] == AgentName.DISCOVERY.value
    assert result["hop_count"] == 1
    assert len(llm.calls) == 1


async def test_planner_rejects_hallucinated_agent_name():
    llm = FakeLLMClient(
        [
            tool_call_response(
                "route_turn",
                {"next_agent": "not_a_real_agent", "rationale": "made up"},
            )
        ]
    )
    state = new_state(conversation_id="c1", student_id="s1")

    result = await planner_node(state, llm=llm)

    assert result["active_agent"] is None


async def test_planner_ends_turn_when_next_agent_is_null():
    llm = FakeLLMClient(
        [tool_call_response("route_turn", {"next_agent": None, "rationale": "reply is ready"})]
    )
    state = new_state(conversation_id="c1", student_id="s1")

    result = await planner_node(state, llm=llm)

    assert result["active_agent"] is None


async def test_hop_cap_stops_llm_calls_without_crashing():
    llm = FakeLLMClient([])  # no responses queued — must not be called
    state = new_state(conversation_id="c1", student_id="s1")
    state["hop_count"] = HOP_CAP

    result = await planner_node(state, llm=llm)

    assert result["active_agent"] is None
    assert len(llm.calls) == 0
