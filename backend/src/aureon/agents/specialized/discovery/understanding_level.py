from typing import Literal

from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.career_hypothesis import CareerHypothesis

UnderstandingStage = Literal[
    "Seed",
    "Explorer",
    "Patterns Emerging",
    "Identity Taking Shape",
    "Career DNA Forming",
    "Decision Ready",
]


def derive_understanding_level(
    *,
    career_dna: CareerDNA,
    hypotheses: list[CareerHypothesis],
    mode: str,
    has_hidden_potential: bool,
) -> tuple[UnderstandingStage, str]:
    """A single evolving narrative caption, not a progress bar or
    percentage — reads like a chapter title. Server-computed so Home and
    the Discovery Workspace always agree, and so it survives a new device
    like everything else in this pass.
    """
    trait_count = len(career_dna.traits)
    active_hypotheses = [h for h in hypotheses if h.status != "discarded"]

    if mode == "recommendation":
        return "Decision Ready", "There's enough evidence to talk about real directions."
    if active_hypotheses:
        return "Career DNA Forming", "A tentative direction is starting to take shape."
    if trait_count >= 3:
        return "Identity Taking Shape", "A fuller picture of you is coming together."
    if has_hidden_potential:
        return "Patterns Emerging", "Aureon is starting to notice how your traits connect."
    if trait_count >= 1:
        return "Explorer", "Aureon is gathering the first pieces of evidence about you."
    return "Seed", "Nothing yet — every conversation plants a seed."
