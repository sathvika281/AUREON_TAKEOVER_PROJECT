"""Responsibility: Exposure Gap Detection — "how likely is this student
to discover this opportunity on their own." Owns:
``compute_exposure_gap``. Does NOT own: fit/eligibility scoring (reuses
Opportunity Hub's existing ``score_opportunity`` unmodified) or ranking
(``domain/services/opportunity_equality.py``). Consumed by:
``domain/services/opportunity_equality.py``.

Deterministic, no LLM. Every factor considered is real: whether the
student has ever engaged with this opportunity's category before
(``OpportunitiesMemory.entries``), whether they've told Aureon they're
still uncertain about the aligned World (``uncertainty_signals``), and
whether the opportunity has narrow eligibility that's easy to miss in a
general search. ``why_shown`` always hedges ("could be," "believes"),
matching Opportunity Hub's own ``timing_rationale``/
``consequence_if_ignored`` phrasing discipline — never asserts certainty
about a specific student.
"""

from aureon.domain.models.career_memory import CareerMemory
from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.models.exposure_gap import ExposureGapInsight
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.student_profile import StudentProfile


def _aligned_world(opportunity: Opportunity, world_signals: list[WorldSignal]) -> str | None:
    tags_lower = {t.lower() for t in [*opportunity.domain_tags, opportunity.category]}
    for signal in world_signals:
        world_lower = signal.world.lower()
        if any(world_lower in tag or tag in world_lower for tag in tags_lower):
            return signal.world
    return None


def compute_exposure_gap(
    opportunity: Opportunity, profile: StudentProfile, memory: CareerMemory, *, world_signal_alignment: float
) -> ExposureGapInsight:
    #: Full sentences for standalone display in `contributing_factors`,
    #: paired 1:1 with a noun-phrase fragment for splicing into the
    #: `why_shown` sentence — kept separate so that sentence reads
    #: grammatically clean instead of joining a clause onto "Based on X and...".
    factors: list[str] = []
    reason_fragments: list[str] = []

    engaged_categories = {e.category for e in memory.opportunities.entries}
    category_is_novel = opportunity.category not in engaged_categories
    if category_is_novel:
        category_label = opportunity.category.replace("_", " ")
        factors.append(f"You haven't explored a {category_label} opportunity before.")
        reason_fragments.append(f"how few {category_label} opportunities you've explored so far")

    aligned_world = _aligned_world(opportunity, profile.discovery_onboarding.world_signals)
    is_uncertain_world = False
    if aligned_world:
        uncertain_contexts = {u.context.lower() for u in profile.discovery_onboarding.uncertainty_signals}
        is_uncertain_world = any(aligned_world.lower() in context for context in uncertain_contexts)
        if is_uncertain_world:
            factors.append(
                f"You've told Aureon you're still exploring {aligned_world}, so you're less likely to "
                "have gone looking for this on your own."
            )
            reason_fragments.append(f"your own uncertainty about {aligned_world} so far")

    is_niche = opportunity.min_academic_level != "any" or bool(opportunity.countries)
    if is_niche:
        factors.append(
            "This opportunity has specific eligibility requirements that make it easy to miss in a general search."
        )
        reason_fragments.append("this opportunity's specific eligibility requirements")

    novel_signal_count = sum([category_is_novel, is_uncertain_world, is_niche])
    if novel_signal_count >= 2:
        likelihood = "low"
    elif novel_signal_count == 1:
        likelihood = "medium"
    else:
        likelihood = "high"

    if reason_fragments:
        world_phrase = f"your interest in {aligned_world}" if aligned_world else "your real activity so far"
        reason_phrase = reason_fragments[0]
        why_shown = f"Based on {world_phrase} and {reason_phrase}, Aureon believes this could be worth a look."
    else:
        why_shown = "This is a well-known opportunity that students in your area of interest often find easily."

    return ExposureGapInsight(
        likelihood_of_self_discovery=likelihood, why_shown=why_shown, contributing_factors=factors
    )
