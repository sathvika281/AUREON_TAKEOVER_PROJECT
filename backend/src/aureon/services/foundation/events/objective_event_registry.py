"""Responsibility: the registration mechanism for "does this Build
Orchestrator objective emit a domain event, and which one." Owns: the
objective -> ``EventType`` mapping (module-private dict), mirroring
``agents/foundation/objective_registry.py``'s pattern exactly. Does NOT
own: what happens once an event is published (``EventBus``/its
subscribers). Consumed by: ``BuildOrchestrator`` (read).

Starts genuinely empty — no real objective today (mentor_match_analysis,
college_match_analysis, progress_intelligence_analysis) honestly maps to
one of EventType's events without fabricating meaning; every one of
those events belongs to a not-yet-built Phase 2 feature.

Extension point — a future feature registers its own mapping from its
own module by calling ``register_objective_event(...)``; this file and
``build_orchestrator.py`` never change.
"""

from aureon.services.foundation.events.types import EventType

_OBJECTIVE_EVENTS: dict[str, EventType] = {}


def register_objective_event(objective: str, event_type: EventType) -> None:
    _OBJECTIVE_EVENTS[objective] = event_type


def get_objective_event(objective: str) -> EventType | None:
    return _OBJECTIVE_EVENTS.get(objective)
