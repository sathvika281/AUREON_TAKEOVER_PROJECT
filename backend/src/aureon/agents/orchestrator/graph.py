from functools import partial

from langgraph.graph import END, StateGraph

import aureon.agents.specialized  # noqa: F401  (registers every specialized agent)
from aureon.agents.confidence_gate import apply_confidence_gate
from aureon.agents.orchestrator.checkpointer import get_checkpointer
from aureon.agents.orchestrator.planner_node import planner_node, route_from_planner
from aureon.agents.registry import AgentRegistry
from aureon.agents.state import AureonState
from aureon.core.config import get_settings
from aureon.services.llm.base import LLMClient
from aureon.services.llm.factory import get_llm_client

TURN_START_NODE = "turn_start"
PLANNER_NODE = "planner"
GATE_NODE = "confidence_gate"


def turn_start_node(state: AureonState) -> AureonState:
    """Real entry point of the graph. Resets fields that are scoped to a
    single user turn — even when the checkpointer resumes a conversation
    thread across turns (see domain/services/conversation_service.py),
    these must not leak from the previous turn. Fields that should
    persist across the whole conversation (student_profile,
    confidence_score, mode, why_probe_state) are deliberately left alone.
    """
    state["turn_count"] = state.get("turn_count", 0) + 1
    state["agent_outputs"] = {}
    state["active_agent"] = None
    state["planner_rationale"] = None
    state["should_end"] = False
    state["hop_count"] = 0
    return state


def _gate_node(state: AureonState) -> AureonState:
    return apply_confidence_gate(state, settings=get_settings())


def build_graph(llm: LLMClient | None = None) -> StateGraph:
    """Builds the orchestrator ``StateGraph`` entirely from
    ``AgentRegistry.describe_all()``. Adding agent #9 means creating one
    new module under ``agents/specialized/`` and importing it in
    ``agents/specialized/__init__.py`` — this function never changes.

    Flow: turn_start (per-turn hygiene) -> planner (LLM decides next
    agent) -> confidence_gate (hard deterministic override for
    recommendation-stage agents below the safety floor) -> conditional
    edge to the chosen agent node -> back to planner, looping until the
    planner (or gate, or the hop cap) routes to ``END``.

    ``llm`` defaults to the configured provider (``get_llm_client()``) but
    can be injected — e.g. a fake double in tests — without touching
    production wiring.
    """
    graph = StateGraph(AureonState)

    llm = llm or get_llm_client()
    graph.add_node(TURN_START_NODE, turn_start_node)
    graph.add_node(PLANNER_NODE, partial(planner_node, llm=llm))
    graph.add_node(GATE_NODE, _gate_node)

    route_map: dict[str, str] = {END: END}
    for descriptor in AgentRegistry.describe_all():
        agent = AgentRegistry.get(descriptor.name)
        graph.add_node(descriptor.name, partial(agent.run, llm=llm))
        graph.add_edge(descriptor.name, PLANNER_NODE)
        route_map[descriptor.name] = descriptor.name

    graph.set_entry_point(TURN_START_NODE)
    graph.add_edge(TURN_START_NODE, PLANNER_NODE)
    graph.add_edge(PLANNER_NODE, GATE_NODE)
    graph.add_conditional_edges(GATE_NODE, route_from_planner, route_map)

    return graph


def get_compiled_graph(llm: LLMClient | None = None):
    return build_graph(llm).compile(checkpointer=get_checkpointer())
