from datetime import datetime, timezone

from aureon.services.foundation.events.bus import EventBus
from aureon.services.foundation.events.types import Event, EventType


def _event(event_type: EventType = EventType.SKILL_VERIFIED) -> Event:
    return Event(
        event_id="e1", event_type=event_type, student_id="s1", payload={}, occurred_at=datetime.now(timezone.utc)
    )


async def test_publish_calls_subscribed_handler_exactly_once():
    bus = EventBus()
    calls = []

    async def handler(event: Event):
        calls.append(event)
        return "handled"

    bus.subscribe(EventType.SKILL_VERIFIED, handler)
    results = await bus.publish(_event())

    assert calls == [_event()] or len(calls) == 1  # same event content, different identity is fine
    assert results == ["handled"]


async def test_publish_ignores_event_types_with_no_subscribers():
    bus = EventBus()
    results = await bus.publish(_event(EventType.NEW_CERTIFICATE))
    assert results == []


async def test_one_failing_handler_does_not_block_a_second_or_raise():
    bus = EventBus()
    calls = []

    async def failing_handler(event: Event):
        raise RuntimeError("boom")

    async def working_handler(event: Event):
        calls.append(event)
        return "ok"

    bus.subscribe(EventType.SKILL_VERIFIED, failing_handler)
    bus.subscribe(EventType.SKILL_VERIFIED, working_handler)

    results = await bus.publish(_event())

    assert len(calls) == 1
    assert results == ["ok"]  # only the working handler's result is collected
