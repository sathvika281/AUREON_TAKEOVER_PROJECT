from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.conversation_service import ConversationService


def _service():
    conversations = AsyncMock()
    profiles = AsyncMock()
    profiles.get_or_create.return_value = StudentProfile(student_id="s1")
    service = ConversationService(conversations, profiles)
    return service, conversations, profiles


async def test_new_conversation_seeds_full_state_without_checking_checkpoint():
    service, conversations, profiles = _service()
    fake_graph = SimpleNamespace(
        aget_state=AsyncMock(),
        ainvoke=AsyncMock(return_value={"student_profile": StudentProfile(student_id="s1")}),
    )

    with patch(
        "aureon.domain.services.conversation_service.get_compiled_graph",
        return_value=fake_graph,
    ):
        await service.handle_turn(student_id="s1", conversation_id=None, message="hi")

    fake_graph.aget_state.assert_not_called()
    conversations.create_conversation.assert_called_once()
    sent_state = fake_graph.ainvoke.call_args.args[0]
    # A brand-new conversation gets the full state shape, not a partial update.
    assert "turn_count" in sent_state
    assert "why_probe_state" in sent_state


async def test_continuing_conversation_with_checkpoint_sends_incremental_update():
    service, conversations, profiles = _service()
    fake_graph = SimpleNamespace(
        aget_state=AsyncMock(return_value=SimpleNamespace(values={"turn_count": 1})),
        ainvoke=AsyncMock(return_value={"student_profile": StudentProfile(student_id="s1")}),
    )

    with patch(
        "aureon.domain.services.conversation_service.get_compiled_graph",
        return_value=fake_graph,
    ):
        await service.handle_turn(student_id="s1", conversation_id="existing", message="hi again")

    conversations.create_conversation.assert_not_called()
    fake_graph.aget_state.assert_called_once()
    sent_state = fake_graph.ainvoke.call_args.args[0]
    # Only the incremental update — not a full new_state() rebuild — so the
    # checkpointer's cross-turn fields (why_probe_state, turn_count, ...)
    # aren't clobbered back to defaults.
    assert set(sent_state.keys()) == {"messages", "student_profile"}


async def test_continuing_conversation_without_checkpoint_rebuilds_fresh():
    service, conversations, profiles = _service()
    fake_graph = SimpleNamespace(
        aget_state=AsyncMock(return_value=SimpleNamespace(values={})),
        ainvoke=AsyncMock(return_value={"student_profile": StudentProfile(student_id="s1")}),
    )

    with patch(
        "aureon.domain.services.conversation_service.get_compiled_graph",
        return_value=fake_graph,
    ):
        await service.handle_turn(
            student_id="s1", conversation_id="expired-thread", message="hi"
        )

    sent_state = fake_graph.ainvoke.call_args.args[0]
    assert "turn_count" in sent_state
    assert "why_probe_state" in sent_state
