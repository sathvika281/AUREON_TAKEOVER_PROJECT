from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.mentor_handoff import MentorHandoff
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import Mode


class AureonState(TypedDict):
    """Shared graph state threaded through the orchestrator and every
    specialized agent node.

    Two categories of field live here:

    - Session-scoped (reset per conversation): conversation_id, messages,
      turn_count, should_end.
    - Person-scoped snapshot: student_profile, confidence_score, mode. These
      are loaded from the student's long-term ``StudentProfile`` at session
      start and written back to that same long-term record after each turn
      (see domain/services/conversation_service.py) — understanding of the
      student accumulates across sessions rather than resetting.

    ``agent_outputs`` is keyed by agent name so each specialized agent only
    ever reads/writes its own entry, preventing cross-agent coupling.
    """

    conversation_id: str
    student_id: str
    messages: Annotated[list[AnyMessage], add_messages]

    student_profile: StudentProfile | None
    confidence_score: float
    mode: Literal["exploration", "recommendation"]

    active_agent: str | None
    agent_history: list[str]
    planner_rationale: str | None
    agent_outputs: dict[str, AgentOutput]

    mentor_handoff: MentorHandoff | None

    #: Why Engine depth tracking: topic label -> number of times probed.
    #: Capped deterministically (see agents/specialized/discovery/agent.py)
    #: so the student is never interrogated past a couple of "why"s on the
    #: same topic.
    why_probe_state: dict[str, int]

    #: Set by Discovery when it asks a reflection question; read back next
    #: turn so evidence sources know the student's message is answering it
    #: rather than starting a new topic.
    pending_reflection_prompt: str | None

    #: Counts agent->planner->agent hops within a single user turn (reset
    #: each turn by turn_start_node). Capped to prevent a runaway loop
    #: within one graph invocation now that planner routing is real.
    hop_count: int

    turn_count: int
    should_end: bool


def new_state(
    *,
    conversation_id: str,
    student_id: str,
    student_profile: StudentProfile | None = None,
) -> AureonState:
    """Factory for a fresh per-session state, seeded from the student's
    long-term profile when one already exists."""
    return AureonState(
        conversation_id=conversation_id,
        student_id=student_id,
        messages=[],
        student_profile=student_profile,
        confidence_score=student_profile.confidence_score if student_profile else 0.0,
        mode=Mode.EXPLORATION.value,
        active_agent=None,
        agent_history=[],
        planner_rationale=None,
        agent_outputs={},
        mentor_handoff=None,
        why_probe_state={},
        pending_reflection_prompt=None,
        hop_count=0,
        turn_count=0,
        should_end=False,
    )
