"""Responsibility: in-process publish/subscribe dispatch. Owns:
subscriber registration and isolated dispatch per ``EventType``. Does
NOT own: what any subscriber actually does (Career Memory recording,
Universe Evolution — both live in ``handlers.py``, never here) — this
module never imports either. Consumed by: ``BuildOrchestrator``
(publishes) and ``handlers.py`` (subscribes).

In-process is the deliberate, documented scope for this phase — same
precedent as ``agents/orchestrator/checkpointer.py``'s ``MemorySaver``
(swappable later, e.g. to a real queue, without changing callers).
"""

import logging
from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import Any

from aureon.services.foundation.events.types import Event, EventType

logger = logging.getLogger(__name__)

EventHandler = Callable[[Event], Awaitable[Any]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[EventHandler]] = {}

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event) -> list[Any]:
        """Calls every subscriber for ``event.event_type`` in
        registration order. One subscriber raising is logged and
        skipped — it never blocks the remaining subscribers and never
        raises out of ``publish`` itself (graceful degradation, per the
        approved plan's error-handling section)."""
        results: list[Any] = []
        for handler in self._subscribers.get(event.event_type, []):
            try:
                results.append(await handler(event))
            except Exception:  # noqa: BLE001 — isolate one bad subscriber from the rest
                logger.exception(
                    "Event Bus subscriber failed for event_type=%s (event_id=%s)",
                    event.event_type, event.event_id,
                )
        return results


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()
