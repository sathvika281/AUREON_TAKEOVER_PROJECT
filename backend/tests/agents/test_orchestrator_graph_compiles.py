from aureon.agents.orchestrator.graph import GATE_NODE, PLANNER_NODE, get_compiled_graph
from aureon.agents.registry import AgentRegistry


def test_graph_compiles_with_every_registered_agent():
    compiled = get_compiled_graph()

    node_names = set(compiled.get_graph().nodes.keys())
    assert PLANNER_NODE in node_names
    assert GATE_NODE in node_names
    for descriptor in AgentRegistry.describe_all():
        assert descriptor.name in node_names
