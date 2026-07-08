import uuid
from typing import Any

from langchain_core.messages import HumanMessage

from aureon.agents.orchestrator.graph import get_compiled_graph
from aureon.agents.state import AureonState, new_state
from aureon.domain.models.conversation import Conversation, Turn
from aureon.services.supabase.repositories.conversation_repository import (
    ConversationRepository,
)
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)


class ConversationService:
    """Coordinates a single conversation turn end-to-end:

    1. Loads the student's long-term profile (cross-session memory).
    2. Loads or creates the session-scoped conversation.
    3. Invokes the orchestrator graph with both.
    4. Persists the new turn and the (possibly updated) long-term profile.

    This is the seam the API layer calls through — routes never touch the
    orchestrator graph or repositories directly, keeping business logic out
    of ``api/``.
    """

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        student_profile_repository: StudentProfileRepository,
    ) -> None:
        self._conversations = conversation_repository
        self._profiles = student_profile_repository

    async def handle_turn(
        self, *, student_id: str, conversation_id: str | None, message: str
    ) -> AureonState:
        profile = await self._profiles.get_or_create(student_id)

        is_new_conversation = conversation_id is None
        if is_new_conversation:
            conversation_id = str(uuid.uuid4())
            await self._conversations.create_conversation(
                Conversation(conversation_id=conversation_id, student_id=student_id)
            )

        await self._conversations.append_turn(
            conversation_id, Turn(role="student", content=message)
        )

        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": conversation_id}}

        # Only a brand-new thread gets the full new_state(...). A
        # continuing conversation sends just the incremental message —
        # everything else (turn_count, why_probe_state, agent_history,
        # student_profile) comes from the checkpointer. Sending a full
        # new_state() every turn would silently reset those non-reducer
        # fields each time, defeating multi-turn continuity (e.g. the Why
        # Engine's probe-depth tracking).
        input_state: dict[str, Any]
        if is_new_conversation:
            seeded = new_state(
                conversation_id=conversation_id,
                student_id=student_id,
                student_profile=profile,
            )
            seeded["messages"] = [HumanMessage(content=message)]
            input_state = seeded
        else:
            snapshot = await graph.aget_state(config)
            if snapshot.values:
                input_state = {
                    "messages": [HumanMessage(content=message)],
                    "student_profile": profile,
                }
            else:
                # thread_id was provided but no checkpoint exists (e.g.
                # server restarted with the in-memory checkpointer) —
                # rebuild fresh rather than invoking with a half-formed state.
                seeded = new_state(
                    conversation_id=conversation_id,
                    student_id=student_id,
                    student_profile=profile,
                )
                seeded["messages"] = [HumanMessage(content=message)]
                input_state = seeded

        result_state: AureonState = await graph.ainvoke(input_state, config=config)

        updated_profile = result_state.get("student_profile")
        if updated_profile is not None:
            await self._profiles.save(updated_profile)

        return result_state
