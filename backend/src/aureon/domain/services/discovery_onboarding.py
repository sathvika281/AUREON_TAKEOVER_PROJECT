"""Responsibility: Discover Batch 1's Profile Service — writing a
student's real onboarding answers onto their persisted profile. Owns:
``complete_onboarding``. Does NOT own: World Signal reinforcement
mechanics (``domain/services/world_signal.py``, called here only to
seed initial signals) or Orbit Status computation
(``domain/services/orbit_status.py``). Consumed by:
``api/v1/discovery_onboarding.py``'s onboarding-submit route.

Nothing collected here is a permanent label — every field stays a
plain, always-overwritable record; a future re-onboarding (not built
yet) would simply call this again.
"""

from datetime import datetime
from typing import Literal

from aureon.domain.models.discovery_onboarding import DiscoveryOnboarding, UncertaintySignal
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.world_signal import create_world_signal
from aureon.services.foundation.career_memory.service import record_academic_level


def complete_onboarding(
    profile: StudentProfile,
    *,
    name: str | None,
    age: int | None,
    stage: Literal["School", "College", "Professional"] | None,
    location_state: str | None,
    location_city: str | None,
    preferred_language: str | None,
    current_situation: Literal["no_idea", "few_careers", "dream_career", "switch_careers"] | None,
    worlds: list[str],
    worlds_unsure: bool,
    now: datetime,
) -> None:
    uncertainty_signals: list[UncertaintySignal] = []
    if current_situation == "no_idea":
        uncertainty_signals.append(UncertaintySignal(context="no_idea", observed_at=now))
    if worlds_unsure:
        uncertainty_signals.append(UncertaintySignal(context="worlds_unsure", observed_at=now))

    profile.discovery_onboarding = DiscoveryOnboarding(
        completed=True,
        completed_at=now,
        name=name,
        age=age,
        stage=stage,
        location_state=location_state,
        location_city=location_city,
        preferred_language=preferred_language,
        current_situation=current_situation,
        world_signals=[create_world_signal(world, now) for world in worlds],
        worlds_pending_followup=list(worlds),
        uncertainty_signals=uncertainty_signals,
    )

    if stage is not None:
        record_academic_level(profile, stage=stage)
