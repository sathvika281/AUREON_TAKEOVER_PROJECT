import uuid
from datetime import datetime
from typing import Any

from aureon.domain.models.career_exploration import CareerExplorationEvent, CareerInteractionType
from aureon.domain.models.student_profile import StudentProfile

#: Guards against near-instant duplicate fires (e.g. a double-invoked UI
#: effect or a rapid double-click) — genuine repeat visits over time are
#: still recorded, since "returned to repeatedly" is meaningful signal
#: for Phase 3, not noise to suppress.
DEDUP_WINDOW_SECONDS = 5.0

#: "opened" and "revisited" are the same underlying action (a visit),
#: just labeled differently depending on history — for dedup purposes
#: they must be treated as one bucket. Checking dedup only against the
#: post-upgrade label would miss a rapid double-fire that happens to
#: cross the opened->revisited boundary mid-flight.
_VISIT_TYPES = {"opened", "revisited"}


def record_exploration_event(
    profile: StudentProfile,
    *,
    career_id: str,
    interaction_type: CareerInteractionType,
    metadata: dict[str, Any],
    now: datetime,
) -> CareerExplorationEvent | None:
    """Appends one observational exploration event, or returns ``None`` if
    this is a near-instant duplicate of the last event for the same career
    + interaction (checked *before* the opened->revisited upgrade below, so
    a rapid double-fire is caught regardless of which label it would land
    on). An ``"opened"`` event is then auto-upgraded to ``"revisited"``
    when the student has already visited this career before — a single,
    authoritative place for that classification rather than depending on
    frontend-held state.
    """
    dedup_types = _VISIT_TYPES if interaction_type in _VISIT_TYPES else {interaction_type}
    matching = [
        e
        for e in profile.career_exploration_history
        if e.career_id == career_id and e.interaction_type in dedup_types
    ]
    if matching:
        last = max(matching, key=lambda e: e.created_at)
        if (now - last.created_at).total_seconds() < DEDUP_WINDOW_SECONDS:
            return None

    if interaction_type == "opened" and any(
        e.career_id == career_id and e.interaction_type in _VISIT_TYPES
        for e in profile.career_exploration_history
    ):
        interaction_type = "revisited"

    event = CareerExplorationEvent(
        id=str(uuid.uuid4()),
        career_id=career_id,
        interaction_type=interaction_type,
        metadata=metadata,
        created_at=now,
    )
    profile.career_exploration_history.append(event)
    return event
