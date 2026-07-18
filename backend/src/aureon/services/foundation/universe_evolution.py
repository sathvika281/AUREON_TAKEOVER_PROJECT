"""Responsibility: decide the semantic universe change a domain
``Event`` produces. Owns: ``UniverseEventType``, ``UniverseEvent``, and
the event-to-event rule table in ``evaluate``. Does NOT own: how any
``UniverseEventType`` actually renders — no coordinates, no colors, no
animation; a future, separate frontend phase decides that. Consumed by:
the Universe-Evolution subscriber registered in
``events/handlers.py``.

Genuinely event-to-event, never UI-shaped: a domain ``Event`` (e.g.
``PROJECT_COMPLETED``) goes in, a semantic ``UniverseEvent`` (e.g.
``SATELLITE_ADDED``) comes out — never an ``(element, action)`` pair
that implies a specific visual shape.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from aureon.services.foundation.events.types import Event, EventType


class UniverseEventType(StrEnum):
    SATELLITE_ADDED = "satellite_added"
    STAR_APPEARED = "star_appeared"
    CONSTELLATION_EXPANDED = "constellation_expanded"
    GUIDING_STAR_BRIGHTENED = "guiding_star_brightened"
    DARK_MATTER_BECAME_STAR = "dark_matter_became_star"
    SUN_ROSE = "sun_rose"
    MOON_BRIGHTENED = "moon_brightened"


@dataclass(frozen=True)
class UniverseEvent:
    event_type: UniverseEventType
    student_id: str
    reason: str
    metadata: dict[str, Any]
    occurred_at: datetime


#: One rule per worked example in the approved spec. Unmapped EventTypes
#: (e.g. SUGGESTED_ACTIVITY_COMPLETED, NEW_CERTIFICATE, INTERVIEW_FINISHED)
#: deliberately have no entry — evaluate() returns None for those, never
#: a fabricated universe change.
_EVENT_RULES: dict[EventType, UniverseEventType] = {
    EventType.PROJECT_COMPLETED: UniverseEventType.SATELLITE_ADDED,
    EventType.RESEARCH_PAPER_ADDED: UniverseEventType.STAR_APPEARED,
    EventType.INTERNSHIP_ADDED: UniverseEventType.CONSTELLATION_EXPANDED,
    EventType.MENTOR_CONNECTED: UniverseEventType.GUIDING_STAR_BRIGHTENED,
    EventType.SKILL_VERIFIED: UniverseEventType.DARK_MATTER_BECAME_STAR,
    EventType.CAREER_READINESS_INCREASED: UniverseEventType.SUN_ROSE,
    EventType.PORTFOLIO_UPDATED: UniverseEventType.MOON_BRIGHTENED,
    #: Phase 2 Stage 2 — Opportunity Hub. Restrained mapping: only the
    #: two high-signal opportunity events get a universe reaction.
    #: OPPORTUNITY_VIEWED/OPPORTUNITY_SAVED/APPLICATION_WITHDRAWN are
    #: deliberately unmapped — low-signal browsing/retraction, same
    #: honest-None treatment as SUGGESTED_ACTIVITY_COMPLETED.
    EventType.OPPORTUNITY_APPLIED: UniverseEventType.CONSTELLATION_EXPANDED,
    EventType.OPPORTUNITY_COMPLETED: UniverseEventType.SATELLITE_ADDED,
}


class UniverseEvolutionEngine:
    def evaluate(self, event: Event) -> UniverseEvent | None:
        universe_event_type = _EVENT_RULES.get(event.event_type)
        if universe_event_type is None:
            return None
        return UniverseEvent(
            event_type=universe_event_type,
            student_id=event.student_id,
            reason=f"Triggered by {event.event_type.value}.",
            metadata=dict(event.payload),
            occurred_at=event.occurred_at,
        )
