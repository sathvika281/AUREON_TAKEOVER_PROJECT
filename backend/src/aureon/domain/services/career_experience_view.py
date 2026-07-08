from datetime import datetime, timedelta, timezone

"""Deterministic slot generation for Expert Connect (V13) — a genuine
architectural simplification, not a fake "real" scheduling system: slots
are computed the same way for every request, with no persisted global-
availability table and no cross-student conflict resolution (see the
V13 plan's explicit design decision on this). Real video calling / real
calendar integration are both explicitly out of scope."""

#: Fixed daily times a mentor is illustratively "available" — not read
#: from any real calendar, since none exists.
_SLOT_HOURS = (10, 15)
_WEEKDAYS_AHEAD = 5


def generate_available_slots(*, now: datetime | None = None) -> list[datetime]:
    """The next 5 weekdays (Mon-Fri), 2 fixed times each — identical for
    every mentor and every student, since no real calendar backs this."""
    now = now or datetime.now(timezone.utc)
    slots: list[datetime] = []
    day = now.date() + timedelta(days=1)
    while len(slots) < _WEEKDAYS_AHEAD * len(_SLOT_HOURS):
        if day.weekday() < 5:  # Monday-Friday
            for hour in _SLOT_HOURS:
                slots.append(datetime(day.year, day.month, day.day, hour, 0, tzinfo=timezone.utc))
        day += timedelta(days=1)
    return slots
