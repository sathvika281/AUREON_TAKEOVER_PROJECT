from datetime import datetime, timezone

import pytest

from aureon.services.foundation.events.types import Event, EventType
from aureon.services.foundation.universe_evolution import UniverseEvolutionEngine, UniverseEventType


def _event(event_type: EventType) -> Event:
    return Event(
        event_id="e1", event_type=event_type, student_id="s1", payload={}, occurred_at=datetime.now(timezone.utc)
    )


@pytest.mark.parametrize(
    "event_type,expected",
    [
        (EventType.PROJECT_COMPLETED, UniverseEventType.SATELLITE_ADDED),
        (EventType.RESEARCH_PAPER_ADDED, UniverseEventType.STAR_APPEARED),
        (EventType.INTERNSHIP_ADDED, UniverseEventType.CONSTELLATION_EXPANDED),
        (EventType.MENTOR_CONNECTED, UniverseEventType.GUIDING_STAR_BRIGHTENED),
        (EventType.SKILL_VERIFIED, UniverseEventType.DARK_MATTER_BECAME_STAR),
        (EventType.CAREER_READINESS_INCREASED, UniverseEventType.SUN_ROSE),
        (EventType.PORTFOLIO_UPDATED, UniverseEventType.MOON_BRIGHTENED),
        (EventType.OPPORTUNITY_APPLIED, UniverseEventType.CONSTELLATION_EXPANDED),
        (EventType.OPPORTUNITY_COMPLETED, UniverseEventType.SATELLITE_ADDED),
    ],
)
def test_evaluate_maps_every_spec_example(event_type, expected):
    result = UniverseEvolutionEngine().evaluate(_event(event_type))
    assert result is not None
    assert result.event_type == expected
    assert result.student_id == "s1"


@pytest.mark.parametrize(
    "event_type",
    [
        EventType.SUGGESTED_ACTIVITY_COMPLETED,
        EventType.NEW_CERTIFICATE,
        EventType.INTERVIEW_FINISHED,
        EventType.OPPORTUNITY_VIEWED,
        EventType.OPPORTUNITY_SAVED,
        EventType.APPLICATION_WITHDRAWN,
    ],
)
def test_evaluate_returns_none_for_unmapped_event_types(event_type):
    assert UniverseEvolutionEngine().evaluate(_event(event_type)) is None
