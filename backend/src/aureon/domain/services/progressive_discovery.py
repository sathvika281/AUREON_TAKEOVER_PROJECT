"""Responsibility: Progressive Discovery Service — "what should the
student see right now." Owns: ``WORLD_FOLLOWUPS`` (the real, backend-
owned follow-up question content — the frontend no longer hardcodes
this) and ``get_progressive_discovery_state``, which composes World
Signal Service + Orbit Service (+, since Discover Batch 2, the
Experiment catalog) into one response. Does NOT own:
confidence/reinforcement math (``domain/services/world_signal.py``) or
stage-derived guidance (``domain/services/orbit_status.py``) — this
module never reimplements either, only composes them. Consumed by:
``api/v1/discovery_onboarding.py``, all three routes.
"""

from dataclasses import dataclass

from aureon.domain.models.experiment import Experiment
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_history import get_completed_experiment_ids
from aureon.domain.services.orbit_status import get_orbit_status
from aureon.domain.services.world_signal import next_pending_world_followup
from aureon.shared.schemas import (
    ExperimentSummaryDTO,
    PendingCheckInDTO,
    ProgressiveDiscoveryStateResponse,
    WorldSignalDTO,
)


@dataclass(frozen=True)
class WorldFollowUp:
    prompt: str
    options: list[str]


#: One follow-up question per world — always ends with "None Yet," the
#: explicit honest opt-out required for every world, not just the
#: top-level "I'm not sure." Ported from the reviewed frontend
#: onboardingConfig.ts — this is now the single real copy; the frontend
#: stops hardcoding it and renders whatever this returns.
WORLD_FOLLOWUPS: dict[str, WorldFollowUp] = {
    "AI": WorldFollowUp("Have you ever tried any of these?", ["Python", "Robotics", "Hackathons", "Research Papers", "Science Fairs", "None Yet"]),
    "Arts": WorldFollowUp("Have you ever tried any of these?", ["Drawing", "Design", "Illustration", "Photography", "Competitions", "None Yet"]),
    "Healthcare": WorldFollowUp("Have you ever tried any of these?", ["Biology", "Medical Camps", "Hospital Visits", "Science Projects", "None Yet"]),
    "Space": WorldFollowUp("Have you ever tried any of these?", ["Astronomy Club", "Science Fairs", "Documentaries", "Stargazing", "None Yet"]),
    "Business": WorldFollowUp("Have you ever tried any of these?", ["Startup Meetups", "School Clubs", "Case Competitions", "Reading", "None Yet"]),
    "Design": WorldFollowUp("Have you ever tried any of these?", ["Sketching", "Digital Tools", "School Projects", "Competitions", "None Yet"]),
    "Psychology": WorldFollowUp("Have you ever tried any of these?", ["Reading", "Journaling", "Peer Counseling", "School Projects", "None Yet"]),
}


def get_progressive_discovery_state(
    profile: StudentProfile, *, mode: str, experiments: list[Experiment] | None = None
) -> ProgressiveDiscoveryStateResponse:
    onboarding = profile.discovery_onboarding
    orbit = get_orbit_status(profile, mode=mode)

    pending_world = next_pending_world_followup(onboarding)
    pending = None
    if pending_world is not None and pending_world in WORLD_FOLLOWUPS:
        follow_up = WORLD_FOLLOWUPS[pending_world]
        pending = PendingCheckInDTO(world=pending_world, prompt=follow_up.prompt, options=follow_up.options)

    #: Discover Batch 2 — the one real experiments-catalog-shaped fact
    #: this service can't derive from ``profile`` alone. Omitting
    #: ``experiments`` (every pre-Batch-2 call site) preserves the exact
    #: prior response shape — honestly ``None`` once nothing's left.
    suggested_experiment = None
    if experiments:
        completed_ids = get_completed_experiment_ids(profile)
        next_experiment = next((e for e in experiments if e.id not in completed_ids), None)
        if next_experiment is not None:
            suggested_experiment = ExperimentSummaryDTO(
                id=next_experiment.id,
                title=next_experiment.title,
                related_world=next_experiment.related_world,
                estimated_minutes=next_experiment.estimated_minutes,
            )

    return ProgressiveDiscoveryStateResponse(
        onboarding_completed=onboarding.completed,
        orbit_status=orbit,
        pending_curiosity_checkin=pending,
        world_signals=[
            WorldSignalDTO(
                world=signal.world, confidence=signal.confidence, evidence=signal.evidence,
                status=signal.status, first_observed=signal.first_observed, last_reinforced=signal.last_reinforced,
            )
            for signal in onboarding.world_signals
        ],
        suggested_experiment=suggested_experiment,
    )
