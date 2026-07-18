"""Responsibility: the one bootstrap file wiring this foundation's two
default Event Bus subscribers. Owns: ``register_default_subscribers`` —
the only place depending on ``career_memory`` + ``universe_evolution`` +
the bus together, mirroring how ``agents/specialized/__init__.py`` is
the one place that wires new agents. Does NOT own: Career Memory's
storage or Universe Evolution's rule table — both are only called from
here. Consumed by: ``BuildOrchestrator``.

Extension point — a new subscriber does not require editing this file;
call ``get_event_bus().subscribe(event_type, your_handler)`` from
wherever your future feature lives. This file only holds this
foundation's own two subscribers.

Design note: the publishing ``Event.payload`` carries the already-
loaded, already-saved ``StudentProfile`` directly (``payload["profile"]``)
rather than each subscriber re-fetching it through its own repository
reference — this is in-process, same-request pub/sub, not a distributed
queue, so passing the live object is correct and avoids a stale-
repository bug if this function were called more than once (safe to
call repeatedly; see ``_already_registered``).
"""

from aureon.services.foundation.career_memory.service import get_career_memory_snapshot
from aureon.services.foundation.events.bus import EventBus
from aureon.services.foundation.events.types import Event, EventType
from aureon.services.foundation.universe_evolution import UniverseEvent, UniverseEvolutionEngine

_already_registered: set[int] = set()


def register_default_subscribers(bus: EventBus) -> None:
    if id(bus) in _already_registered:
        return
    _already_registered.add(id(bus))

    async def _record_memory_change(event: Event) -> list[str]:
        profile = event.payload["profile"]
        snapshot = get_career_memory_snapshot(profile)
        changes: list[str] = []
        if snapshot.connections.connections:
            changes.append(f"connections: {len(snapshot.connections.connections)} active")
        if snapshot.evidence.artifacts:
            changes.append(f"evidence: {len(snapshot.evidence.artifacts)} artifacts")
        if snapshot.opportunities.entries:
            changes.append(f"opportunities: {len(snapshot.opportunities.entries)} entries")
        if snapshot.growth.skills or snapshot.growth.missions or snapshot.growth.interview_practice:
            changes.append("growth: updated")
        return changes

    async def _evaluate_universe_change(event: Event) -> UniverseEvent | None:
        return UniverseEvolutionEngine().evaluate(event)

    # Both subscribers listen to every EventType — Career Memory recording
    # is always worth attempting, and UniverseEvolutionEngine.evaluate
    # already returns None gracefully for any EventType with no rule.
    for event_type in EventType:
        bus.subscribe(event_type, _record_memory_change)
        bus.subscribe(event_type, _evaluate_universe_change)
