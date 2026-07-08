from langchain_core.messages import AIMessage
from langgraph.graph import END

from aureon.agents.orchestrator.schemas import PLANNER_TOOL, PlannerDecision
from aureon.agents.registry import AgentRegistry
from aureon.agents.state import AureonState
from aureon.services.llm.base import LLMClient
from aureon.services.llm.schemas import LLMMessage

#: Caps agent -> planner -> agent hops within a single user turn. Genuinely
#: agentic multi-agent chaining in one turn is allowed (e.g. Discovery then
#: Mentor), but must stay bounded — a deterministic backstop rather than
#: relying on the LLM to know when to stop.
HOP_CAP = 3


def _build_planner_messages(state: AureonState) -> list[LLMMessage]:
    descriptors = AgentRegistry.describe_all()
    agent_lines = "\n".join(
        f"- {d.name}: {d.description}"
        + (" [recommendation-stage, gated by confidence]" if d.is_recommendation_stage else "")
        for d in descriptors
    )

    # Agents that have already produced output THIS turn — deliberately
    # read from agent_outputs (reset every turn by turn_start_node), not
    # the whole-session agent_history, which would make every past turn
    # look like it's still "in progress" and caused the planner to keep
    # re-routing to the same agent up to the hop cap on every single turn.
    agents_run_this_turn = list(state["agent_outputs"].keys())
    messages = state["messages"]
    already_has_reply = bool(messages) and isinstance(messages[-1], AIMessage)

    system = LLMMessage(
        role="system",
        content=(
            "You are Aureon's Career Orchestrator. You do not do any career "
            "reasoning yourself — you only decide which specialized agent "
            "should act next this turn, or whether the turn is complete. "
            "There is no fixed pipeline: choose based on the student's "
            "current message and state.\n\n"
            f"Registered agents:\n{agent_lines}\n\n"
            f"Current mode: {state['mode']}\n"
            f"Current confidence score: {state['confidence_score']:.2f}\n"
            f"Agents that have already acted THIS turn: {agents_run_this_turn or 'none'}\n"
            f"Hop {state['hop_count'] + 1} of at most {HOP_CAP} for this turn.\n"
            f"The most recent message is already a reply to the student: {already_has_reply}\n\n"
            "Default to ending the turn (next_agent=null) as soon as the "
            "student's message has a satisfying reply. Only route to another "
            "agent if a genuinely different capability is needed this same "
            "turn (e.g. handing off to a mentor). Never route back to an "
            "agent that already acted this turn unless something material "
            "changed since it ran."
        ),
    )
    return [system]


async def planner_node(state: AureonState, *, llm: LLMClient) -> AureonState:
    """The sole agentic routing point in the orchestrator: an LLM call
    decides which registered agent runs next (or ends the turn), reading
    live from ``AgentRegistry.describe_all()`` — never a hardcoded
    pipeline.
    """
    if state["hop_count"] >= HOP_CAP:
        # Deterministic backstop: whatever agent already ran this turn has
        # already produced a reply, so ending here is graceful, not a
        # failure — it just stops the same kind of unbounded chaining the
        # confidence gate stops for premature recommendations.
        state["active_agent"] = None
        state["planner_rationale"] = "hop cap reached; ending turn"
        return state

    messages = _build_planner_messages(state)
    response = await llm.complete(messages, tools=[PLANNER_TOOL], tool_choice="required")

    if response.tool_calls:
        decision = PlannerDecision.model_validate(response.tool_calls[0].arguments)
    else:
        decision = PlannerDecision(next_agent=None, rationale="planner returned no tool call")

    valid_names = set(AgentRegistry.names())
    next_agent = decision.next_agent if decision.next_agent in valid_names else None

    state["active_agent"] = next_agent
    state["planner_rationale"] = decision.rationale
    state["hop_count"] += 1
    return state


def route_from_planner(state: AureonState) -> str:
    """Mechanical router required by LangGraph's ``add_conditional_edges``.

    All the intelligence already happened upstream (planner_node's LLM
    call, then the deterministic confidence gate); this function only
    reads the already-decided route and returns it, or ``END``. No
    business rules live in this edge function.
    """
    return state.get("active_agent") or END
