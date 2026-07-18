"""Responsibility: the domain event vocabulary published through the
Event Bus. Owns: ``EventType`` and the ``Event`` envelope. Does NOT own:
what happens when an event is published (that's ``EventBus``/its
subscribers) or which objectives emit which event
(``objective_event_registry.py``). Consumed by: ``EventBus``,
``UniverseEvolutionEngine``, and every subscriber in ``handlers.py``.

Naming note — ``Event``/``EventType`` here are this foundation's new
pub/sub primitive, unrelated to the pre-existing ``CareerEvent``
(domain/models/career_event.py, a Knowledge Base entity: workshops/
hackathons), ``CareerExplorationEvent`` (behavioral tracking, never
evidence), or ``EventRegistration`` (a student's event sign-up) — none
of those are part of this system and none are renamed; they're simply
unrelated pre-existing domain data that happens to share the word
"event."
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    PROJECT_COMPLETED = "project_completed"
    #: The frontend's/Growth's daily "suggested activity" concept
    #: (domain/models/discovery evidence's SuggestedActivity) —
    #: deliberately NOT named MISSION_COMPLETED, which would collide with
    #: the pre-existing, unrelated Mission dataclass (agents/mission/mission.py).
    SUGGESTED_ACTIVITY_COMPLETED = "suggested_activity_completed"
    INTERNSHIP_ADDED = "internship_added"
    NEW_CERTIFICATE = "new_certificate"
    RESEARCH_PAPER_ADDED = "research_paper_added"
    MENTOR_CONNECTED = "mentor_connected"
    PORTFOLIO_UPDATED = "portfolio_updated"
    INTERVIEW_FINISHED = "interview_finished"
    SKILL_VERIFIED = "skill_verified"
    CAREER_READINESS_INCREASED = "career_readiness_increased"
    #: Phase 2 Stage 2 — Opportunity Hub. Real student interactions with
    #: an Opportunity, published from BuildOrchestrator's
    #: opportunity_{viewed,saved,applied,withdrawn,completed} objectives.
    OPPORTUNITY_VIEWED = "opportunity_viewed"
    OPPORTUNITY_SAVED = "opportunity_saved"
    OPPORTUNITY_APPLIED = "opportunity_applied"
    APPLICATION_WITHDRAWN = "application_withdrawn"
    OPPORTUNITY_COMPLETED = "opportunity_completed"


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: EventType
    student_id: str
    payload: dict[str, Any]
    occurred_at: datetime
