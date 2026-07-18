"""Responsibility: Orbit Service — "where am I, what should I focus on,
what should I ignore, and why." Owns: ``ORBIT_GUIDANCE``,
``build_orbit_explanation``, ``get_orbit_status``. Does NOT own:
``understanding_stage`` computation itself — reuses
``domain/services/profile_view.py::build_understanding_level`` verbatim
rather than reimplementing the (already deterministic, already real)
stage derivation. Consumed by: ``domain/services/progressive_discovery.py``.

Design guardrails (ported verbatim from the reviewed frontend
``orbitCopy.ts`` this replaces): never compares the student to other
students — every message is anchored to "students at your stage."
Never names a career/college — Discover only ever answers "who am I?"
The explanation line only ever cites real counts
(``notebook_entries``/``career_hypotheses``); a genuine zero gets its
own honest sentence, never a vague platitude. No numeric score is ever
shown except the one real, already-capped ``confidence_score``.
"""

from dataclasses import dataclass

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.profile_view import build_understanding_level
from aureon.shared.schemas import OrbitStatusDTO


@dataclass(frozen=True)
class OrbitGuidance:
    focus: list[str]
    avoid: list[str]
    message: str


ORBIT_GUIDANCE: dict[str, OrbitGuidance] = {
    "Seed": OrbitGuidance(
        focus=["Explore Worlds", "Talk to Aureon about what interests you", "Build Curiosity"],
        avoid=["Research Papers", "Placements", "Internships"],
        message="You're exactly where students at your stage usually begin.",
    ),
    "Explorer": OrbitGuidance(
        focus=["Explore Worlds", "Complete Life Missions", "Build Curiosity"],
        avoid=["Research Papers", "Placements", "Internships"],
        message="You're exactly where students at your stage usually begin.",
    ),
    "Patterns Emerging": OrbitGuidance(
        focus=["Keep Reflecting", "Notice What Excites You", "Explore Worlds"],
        avoid=["Placements", "Choosing a Final Career", "Comparing Yourself to Others"],
        message="You're exactly where students at your stage usually are — patterns take time to reveal themselves.",
    ),
    "Identity Taking Shape": OrbitGuidance(
        focus=["Deepen Reflection", "Explore Adjacent Worlds", "Let Patterns Solidify"],
        avoid=["Rushing a Decision", "Placements", "Internships"],
        message="You're exactly where students at your stage usually are — a fuller picture is forming, and that's real progress.",
    ),
    "Career DNA Forming": OrbitGuidance(
        focus=["Reflect on What Resonates", "Explore Real Experiences", "Talk Through Your Emerging Direction"],
        avoid=["Locking In Too Early", "Placements"],
        message="You're exactly where students at your stage usually are — understanding takes time, and yours is deepening.",
    ),
    "Decision Ready": OrbitGuidance(
        focus=["Explore Direction With Decision Lab", "Validate Through Real Experiences", "Keep Reflecting"],
        avoid=["Rushing Without Reflection", "Ignoring New Curiosity"],
        message="You've reached real clarity — most students take time to get here, and you're exactly where you should be.",
    ),
}


def build_orbit_explanation(notebook_entry_count: int, hypothesis_count: int) -> str:
    """The one arithmetic line that makes the reassurance feel earned
    instead of generic — grounded only in real counts, never a
    fabricated observation."""
    if notebook_entry_count == 0:
        return "You're just getting started — there's nothing to base a direction on yet, and that's exactly right at this point."
    if hypothesis_count == 0:
        plural = "" if notebook_entry_count == 1 else "s"
        return (
            f"Aureon has noticed {notebook_entry_count} real observation{plural} so far, but nothing has "
            "taken clear shape yet — so exploration stays the priority."
        )
    entry_plural = "" if notebook_entry_count == 1 else "s"
    hypothesis_plural = "" if hypothesis_count == 1 else "s"
    return (
        f"Based on {notebook_entry_count} observation{entry_plural} and {hypothesis_count} early "
        f"direction{hypothesis_plural} Aureon has noticed, exploration still matters more than specialization right now."
    )


def get_orbit_status(profile: StudentProfile, *, mode: str) -> OrbitStatusDTO:
    stage, _narrative = build_understanding_level(profile, mode=mode)
    guidance = ORBIT_GUIDANCE.get(stage, ORBIT_GUIDANCE["Seed"])
    explanation = build_orbit_explanation(len(profile.notebook_entries), len(profile.career_hypotheses))
    return OrbitStatusDTO(
        current_orbit=stage,
        focus=guidance.focus,
        avoid=guidance.avoid,
        explanation=explanation,
        message=guidance.message,
        confidence=profile.confidence_score,
    )
