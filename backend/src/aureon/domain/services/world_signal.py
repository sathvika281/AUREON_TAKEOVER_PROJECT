"""Responsibility: World Signal Service — the real, evolving record of
which worlds a student is curious about. Owns: creating/reinforcing
``WorldSignal``s and the pending-follow-up queue. Does NOT own: the
follow-up question *content* (``domain/services/progressive_discovery.py``'s
``WORLD_FOLLOWUPS``) or Orbit Status's guidance copy
(``domain/services/orbit_status.py``). Consumed by:
``domain/services/discovery_onboarding.py`` (initial creation),
``domain/services/progressive_discovery.py`` (queue reads),
``api/v1/discovery_onboarding.py`` (the Curiosity Check-in answer route).

Signal evolution: ``confidence`` is monotonically non-decreasing — a
decrease with no real evidence behind it would be fabrication, the same
failure mode this system refuses everywhere else. See the approved
migration plan's "Signal evolution strategy" section for the intended
future (read-time, recency-aware ranking layered on top of this honest
historical record — not implemented here).
"""

from datetime import datetime

from aureon.domain.models.discovery_onboarding import DiscoveryOnboarding, UncertaintySignal, WorldSignal
from aureon.domain.models.student_profile import StudentProfile

INITIAL_CONFIDENCE = 0.3  # mere curiosity at onboarding is real but weak evidence
REINFORCE_STEP = 0.2  # one real follow-up answer strengthens it — same small-step,
# capped philosophy as agents/specialized/career_intelligence/confidence.py


def create_world_signal(world: str, now: datetime) -> WorldSignal:
    return WorldSignal(
        world=world, confidence=INITIAL_CONFIDENCE, evidence=["selected_at_onboarding"],
        status="curious", first_observed=now, last_reinforced=now,
    )


def reinforce_world_signal(signal: WorldSignal, evidence_items: list[str], now: datetime) -> WorldSignal:
    """Source-agnostic: ``evidence_items`` are plain strings, not a
    "check-in answer" type — any future real evidence source (a
    completed Life Mission, a reflection, an Expert Connect session)
    can call this unchanged later. Never resets ``first_observed``;
    confidence only ever moves up from genuine new evidence."""
    real_items = [item for item in evidence_items if item != "None Yet"]
    new_confidence = min(1.0, signal.confidence + (REINFORCE_STEP if real_items else 0.0))
    return signal.model_copy(
        update={
            "confidence": new_confidence,
            "evidence": [*signal.evidence, *evidence_items],
            "status": "reinforced" if real_items else signal.status,
            "last_reinforced": now,
        }
    )


def next_pending_world_followup(onboarding: DiscoveryOnboarding) -> str | None:
    pending = onboarding.worlds_pending_followup
    return pending[0] if pending else None


def answer_world_followup(profile: StudentProfile, *, world: str, chosen_options: list[str], now: datetime) -> None:
    """Finds the matching WorldSignal, reinforces it, removes ``world``
    from the pending queue, and records an UncertaintySignal if only
    "None Yet" was chosen. Mutates ``profile`` in place; the caller
    persists it."""
    onboarding = profile.discovery_onboarding
    onboarding.world_signals = [
        reinforce_world_signal(signal, chosen_options, now) if signal.world == world else signal
        for signal in onboarding.world_signals
    ]
    onboarding.worlds_pending_followup = [w for w in onboarding.worlds_pending_followup if w != world]

    only_none_yet = len(chosen_options) > 0 and all(o == "None Yet" for o in chosen_options)
    if only_none_yet:
        onboarding.uncertainty_signals.append(
            UncertaintySignal(context=f"none_yet:{world}", observed_at=now)
        )


def queue_world_for_followup(profile: StudentProfile, world: str, now: datetime) -> None:
    """Extension point for a future "explore a new world" surface —
    creates a fresh WorldSignal and queues it even if the world was
    never selected at onboarding, so a genuinely new curiosity is asked
    about instead of permanently skipped. Not wired to any concrete
    trigger yet in this batch; documented honestly rather than faked."""
    onboarding = profile.discovery_onboarding
    if any(signal.world == world for signal in onboarding.world_signals):
        return
    onboarding.world_signals.append(create_world_signal(world, now))
    if world not in onboarding.worlds_pending_followup:
        onboarding.worlds_pending_followup.append(world)
