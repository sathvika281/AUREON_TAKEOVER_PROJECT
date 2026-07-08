from aureon.domain.models.career_hypothesis import HypothesisStatus

#: Investigating -> Growing -> Strong is a function of confidence alone;
#: Validated additionally requires the orchestrator's own recommendation
#: floor to have been crossed (mode == "recommendation") for the leading
#: hypothesis specifically. Status is never LLM-self-reported — asserting
#: your own confidence tier is exactly the kind of unearned certainty this
#: product refuses to allow, so it's always computed from the real number.
INVESTIGATING_CEILING = 0.3
GROWING_CEILING = 0.6


def compute_status(*, confidence: float, mode: str, is_top_hypothesis: bool) -> HypothesisStatus:
    if mode == "recommendation" and is_top_hypothesis:
        return "validated"
    if confidence >= GROWING_CEILING:
        return "strong"
    if confidence >= INVESTIGATING_CEILING:
        return "growing"
    return "investigating"
