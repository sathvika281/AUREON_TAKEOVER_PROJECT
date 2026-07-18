"""Responsibility: Discover Batch 1's own data shapes — adaptive
onboarding, World Signals, and Uncertainty Signals. Owns:
``WorldSignal``, ``UncertaintySignal``, ``DiscoveryOnboarding``. Does
NOT own: Career Memory's ``IdentityMemory`` (a different, later-phase
model — ``academic_level`` is written here-adjacent via
``services/foundation/career_memory/service.py::record_academic_level``,
never duplicated into this model) or the existing Discovery conversation
flow's own fields (``career_dna``, ``career_hypotheses``,
``notebook_entries`` on ``StudentProfile`` — untouched, read-only
inputs to Orbit Status). Consumed by: ``domain/services/world_signal.py``,
``domain/services/discovery_onboarding.py``,
``domain/services/progressive_discovery.py``, and
``api/v1/discovery_onboarding.py``.

Signal evolution philosophy (see the approved plan's "Signal evolution
strategy" section): ``WorldSignal.confidence`` is monotonically
non-decreasing — a decrease with no real evidence behind it would be
fabrication, the same failure mode this system refuses everywhere else.
Nothing here is ever a permanent label: every field stays plainly
re-writable by later real evidence, never redisplayed as a fixed "type."
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorldSignal(BaseModel):
    """One world's real, evolving interest signal. ``status`` is a
    convenience field derived at write time (never independently set) —
    "reinforced" once any real (non-"None Yet") evidence beyond the
    initial onboarding selection exists, "curious" otherwise."""

    world: str
    confidence: float  # 0-1, deterministic — never LLM-guessed, never itself shown as a score
    evidence: list[str] = Field(default_factory=list)
    status: Literal["curious", "reinforced"] = "curious"
    first_observed: datetime
    last_reinforced: datetime


class UncertaintySignal(BaseModel):
    """Uncertainty as meaningful information, not missing data — see
    ``domain/services/world_signal.py``'s writers for where these are
    recorded."""

    context: str  # "no_idea" | "worlds_unsure" | "none_yet:{world}"
    observed_at: datetime = Field(default_factory=_utcnow)


class DiscoveryOnboarding(BaseModel):
    """Adaptive onboarding's real, persisted answers plus every World/
    Uncertainty Signal gathered since. ``completed`` genuinely gates
    nothing on its own here — it's read by
    ``domain/services/progressive_discovery.py`` and mirrored (not
    duplicated as the source of truth) into Supabase Auth
    ``user_metadata`` for the frontend's synchronous route gate."""

    completed: bool = False
    completed_at: datetime | None = None
    name: str | None = None
    age: int | None = None
    stage: Literal["School", "College", "Professional"] | None = None
    location_state: str | None = None
    location_city: str | None = None
    preferred_language: str | None = None
    current_situation: Literal["no_idea", "few_careers", "dream_career", "switch_careers"] | None = None
    world_signals: list[WorldSignal] = Field(default_factory=list)
    worlds_pending_followup: list[str] = Field(default_factory=list)
    uncertainty_signals: list[UncertaintySignal] = Field(default_factory=list)
