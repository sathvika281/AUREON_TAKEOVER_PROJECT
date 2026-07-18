"""Responsibility: Opportunity Fit's deterministic scoring algorithm —
the "why deterministic scoring" answer lives here: a student must be
able to see exactly why a number is what it is, so no factor is ever a
hidden black box. Owns: the 10 per-factor computations, overall-score
combination, smoothing, readiness classification, Highest Impact Gap,
timing/consequence explanations, and ranking comparison. Does NOT own:
weights/thresholds (scoring_config.py — never an inline literal here),
narrative generation (agent.py's LLM call, which only ever narrates
these already-computed facts, never raw profile data), or Opportunity
Cost (cost.py — informational, never fed back into scoring).

Evidence traceability — a hard contract, not just a convention: every
one of the 10 factor-computing functions below returns a `FitFactor`
with a non-empty `evidence` list of concrete real facts, even for
factors that aren't evidence-driven in the skill-match sense (e.g.
`deadline`'s evidence states the real deadline date, `location`'s
states the real constraint or its absence).

Fairness: every `data_available=False` factor's rationale explicitly
states that missing evidence does not count against the student —
absence is never treated as negative evidence.
"""

from datetime import datetime

from aureon.agents.specialized.opportunity.scoring_config import (
    CATEGORY_CYCLE_NOTES,
    DATA_AVAILABLE_BASE,
    DATA_AVAILABLE_STEP,
    FACTOR_WEIGHTS,
    IMPROVABLE_FACTORS,
    NOT_READY_THRESHOLD,
    READY_THRESHOLD,
    SMOOTHING_MINOR_DELTA_THRESHOLD,
    SMOOTHING_NEW_WEIGHT,
    SMOOTHING_PREVIOUS_WEIGHT,
)
from aureon.domain.models.career_memory import CareerMemory
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import FitFactor, HighestImpactGap, OpportunityFitResult
from aureon.domain.models.student_profile import StudentProfile

_ACADEMIC_LADDER = ["high_school", "undergraduate", "graduate"]
_COMPETITIVENESS_BASE = {"low": 1.0, "medium": 0.75, "high": 0.5, "very_high": 0.3}
_HIGH_TRUST_SOURCES = {"github", "document", "search"}
_ABSENCE_TEMPLATE = "Not enough evidence yet to assess {factor} — this does not count against you."


def _match_skills(
    profile: StudentProfile, memory: CareerMemory, required_skills: list[str]
) -> tuple[list[str], list[str], float]:
    """Shared by _skill_match's factor and score_opportunity's
    requirements tally, so both agree on the same real matches."""
    growth_skills = {s.skill.lower(): s.status for s in memory.growth.skills}
    evidence_texts_lower = [e.text.lower() for e in profile.evidence_graph]

    matched: list[str] = []
    unmet: list[str] = []
    matched_weight = 0.0
    for skill in required_skills:
        key = skill.lower()
        if key in growth_skills:
            matched.append(skill)
            matched_weight += 1.0 if growth_skills[key] == "mastered" else 0.5
        elif any(key in text for text in evidence_texts_lower):
            matched.append(skill)
            matched_weight += 0.3
        else:
            unmet.append(skill)
    return matched, unmet, matched_weight


def _career_alignment(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["career_alignment"]
    domain_tags_lower = {t.lower() for t in opportunity.domain_tags}
    category_lower = opportunity.category.lower()

    active_hypotheses = [h for h in profile.career_hypotheses if h.status != "discarded"]
    matching_hypotheses = [
        h for h in active_hypotheses
        if category_lower in h.career_name.lower()
        or any(tag in h.career_name.lower() for tag in domain_tags_lower)
    ]
    has_any_identity_signal = bool(profile.career_hypotheses) or bool(profile.career_dna.traits)

    if matching_hypotheses:
        score = min(1.0, sum(h.confidence for h in matching_hypotheses))
        names = ", ".join(f"{h.career_name} ({h.confidence:.0%} confidence)" for h in matching_hypotheses)
        return FitFactor(
            key="career_alignment", label="Career Alignment", score=score, weight=weight, data_available=True,
            rationale="Your Identity Discovery hypotheses point toward this domain.",
            evidence=[f"Identity Discovery hypotheses aligned with this opportunity: {names}"],
        )

    trait_matches = [
        name for name, signal in profile.career_dna.traits.items()
        if signal.summary and any(tag in signal.summary.lower() for tag in domain_tags_lower)
    ]
    if trait_matches:
        score = min(1.0, 0.3 + 0.2 * len(trait_matches))
        return FitFactor(
            key="career_alignment", label="Career Alignment", score=score, weight=weight, data_available=True,
            rationale="Your Career DNA traits show some connection to this domain.",
            evidence=[f"Career DNA traits touching this domain: {', '.join(trait_matches)}"],
        )

    if has_any_identity_signal:
        return FitFactor(
            key="career_alignment", label="Career Alignment", score=0.5, weight=weight, data_available=True,
            rationale="Your Identity Discovery data exists, but nothing yet points specifically toward this domain.",
            evidence=["No active career hypotheses or Career DNA traits currently overlap with this domain."],
        )
    return FitFactor(
        key="career_alignment", label="Career Alignment", score=0.5, weight=weight, data_available=False,
        rationale=_ABSENCE_TEMPLATE.format(factor="career alignment"),
        evidence=["No Identity Discovery hypotheses or Career DNA traits recorded yet."],
    )


def _skill_match(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["skill_match"]
    if not opportunity.required_skills:
        return FitFactor(
            key="skill_match", label="Skill Match", score=1.0, weight=weight, data_available=True,
            rationale="This opportunity lists no specific required skills.",
            evidence=["No required_skills listed for this opportunity."],
        )
    matched, unmet, matched_weight = _match_skills(profile, memory, opportunity.required_skills)
    score = min(1.0, matched_weight / len(opportunity.required_skills))
    data_available = bool(memory.growth.skills or profile.evidence_graph)
    if matched:
        return FitFactor(
            key="skill_match", label="Skill Match", score=score, weight=weight, data_available=data_available,
            rationale=f"Matched {len(matched)} of {len(opportunity.required_skills)} required skills against your real evidence.",
            evidence=[f"Skill matched: {s}" for s in matched],
        )
    rationale = (
        _ABSENCE_TEMPLATE.format(factor="skill match")
        if not data_available else
        "None of the required skills currently appear in your tracked skills or evidence."
    )
    return FitFactor(
        key="skill_match", label="Skill Match", score=score, weight=weight, data_available=data_available,
        rationale=rationale, evidence=[f"Required skills for this opportunity: {', '.join(opportunity.required_skills)}"],
    )


def _project_match(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["project_match"]
    keywords = {s.lower() for s in [*opportunity.required_skills, *opportunity.domain_tags]}
    relevant = [a for a in memory.evidence.artifacts if a.kind in ("project", "github_repo", "portfolio")]
    matches = [a for a in relevant if any(k in a.title.lower() for k in keywords)]
    score = min(1.0, 0.2 + 0.2 * len(matches))
    data_available = bool(relevant)
    if matches:
        return FitFactor(
            key="project_match", label="Project Match", score=score, weight=weight, data_available=True,
            rationale=f"{len(matches)} of your tracked projects relate to this opportunity's focus area.",
            evidence=[f"Project evidence: {a.title}" for a in matches],
        )
    if data_available:
        return FitFactor(
            key="project_match", label="Project Match", score=score, weight=weight, data_available=True,
            rationale="Your tracked projects don't currently overlap with this opportunity's focus area.",
            evidence=[f"Tracked project/portfolio evidence: {', '.join(a.title for a in relevant)}"],
        )
    return FitFactor(
        key="project_match", label="Project Match", score=0.5, weight=weight, data_available=False,
        rationale=_ABSENCE_TEMPLATE.format(factor="project match"),
        evidence=["No project/GitHub/portfolio evidence tracked yet in Career Memory."],
    )


def _portfolio_strength(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["portfolio_strength"]
    supports_count = len([e for e in profile.evidence_graph if e.relation == "supports"])
    total = len(memory.evidence.artifacts) + supports_count
    score = min(1.0, 0.1 + 0.05 * total)
    # Always data_available=True — zero evidence is itself a real fact,
    # not missing data, so this floors near 0.1 rather than going neutral.
    return FitFactor(
        key="portfolio_strength", label="Portfolio Strength", score=score, weight=weight, data_available=True,
        rationale=f"Your portfolio currently has {len(memory.evidence.artifacts)} tracked evidence artifacts "
        f"and {supports_count} supporting evidence entries.",
        evidence=[f"Portfolio evidence volume: {total} real entries tracked."],
    )


def _academic_eligibility(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["academic_eligibility"]
    if opportunity.min_academic_level == "any":
        return FitFactor(
            key="academic_eligibility", label="Academic Eligibility", score=1.0, weight=weight, data_available=True,
            rationale="This opportunity has no specific academic level requirement.",
            evidence=["min_academic_level: any"],
        )
    student_level = memory.identity.academic_level
    if student_level is None:
        return FitFactor(
            key="academic_eligibility", label="Academic Eligibility", score=0.5, weight=weight, data_available=False,
            rationale=_ABSENCE_TEMPLATE.format(factor="academic eligibility"),
            evidence=[f"Requires: {opportunity.min_academic_level}; your academic level hasn't been recorded yet."],
        )
    gap = abs(_ACADEMIC_LADDER.index(student_level) - _ACADEMIC_LADDER.index(opportunity.min_academic_level))
    score = 1.0 if gap == 0 else 0.5 if gap == 1 else 0.1
    return FitFactor(
        key="academic_eligibility", label="Academic Eligibility", score=score, weight=weight, data_available=True,
        rationale=f"Requires {opportunity.min_academic_level}; your recorded level is {student_level}.",
        evidence=[f"Required academic level: {opportunity.min_academic_level}", f"Your recorded academic level: {student_level}"],
    )


def _location(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["location"]
    if opportunity.is_remote or not opportunity.countries:
        note = "Opportunity is remote — no location constraint." if opportunity.is_remote else "Opportunity is open to all countries."
        return FitFactor(
            key="location", label="Location", score=1.0, weight=weight, data_available=True,
            rationale="This opportunity is remote or open to all countries — no location constraint.",
            evidence=[note],
        )
    student_country = memory.identity.location_country
    if student_country is None:
        return FitFactor(
            key="location", label="Location", score=0.5, weight=weight, data_available=False,
            rationale=_ABSENCE_TEMPLATE.format(factor="location"),
            evidence=[f"Opportunity is limited to: {', '.join(opportunity.countries)}; your country hasn't been recorded yet."],
        )
    matched = student_country in opportunity.countries
    score = 1.0 if matched else 0.1
    rationale = (
        f"Located in {', '.join(opportunity.countries)}; your profile lists {student_country} as your country."
        if matched else
        f"This opportunity is limited to {', '.join(opportunity.countries)}; your profile lists {student_country}."
    )
    return FitFactor(
        key="location", label="Location", score=score, weight=weight, data_available=True,
        rationale=rationale, evidence=[rationale],
    )


def _deadline(opportunity: Opportunity, now: datetime) -> FitFactor:
    weight = FACTOR_WEIGHTS["deadline"]
    if opportunity.application_deadline is None:
        return FitFactor(
            key="deadline", label="Deadline", score=0.9, weight=weight, data_available=True,
            rationale="This opportunity has rolling/ongoing admissions.",
            evidence=["No fixed application deadline."],
        )
    days_left = (opportunity.application_deadline - now).days
    if days_left >= 30:
        score = 1.0
    elif days_left >= 14:
        score = 0.75
    elif days_left >= 7:
        score = 0.5
    elif days_left >= 1:
        score = 0.25
    else:
        score = 0.0
    return FitFactor(
        key="deadline", label="Deadline", score=score, weight=weight, data_available=True,
        rationale=f"{days_left} days remain until the application deadline.",
        evidence=[f"Application deadline: {opportunity.application_deadline.date().isoformat()} ({days_left} days from now)"],
    )


def _competition_level(opportunity: Opportunity, portfolio_factor: FitFactor) -> FitFactor:
    weight = FACTOR_WEIGHTS["competition_level"]
    base = _COMPETITIVENESS_BASE[opportunity.estimated_competitiveness]
    nudge = 0.2 * (portfolio_factor.score - 0.5)
    score = max(0.0, min(1.0, base + nudge))
    return FitFactor(
        key="competition_level", label="Competition Level", score=score, weight=weight, data_available=True,
        rationale=f"Estimated competitiveness: {opportunity.estimated_competitiveness}.",
        evidence=[
            f"Estimated competitiveness: {opportunity.estimated_competitiveness}",
            f"Your portfolio strength score: {portfolio_factor.score:.2f}",
        ],
    )


def _evidence_quality(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["evidence_quality"]
    sources = {e.source for e in profile.evidence_graph}
    if not sources:
        return FitFactor(
            key="evidence_quality", label="Evidence Quality", score=0.4, weight=weight, data_available=False,
            rationale=_ABSENCE_TEMPLATE.format(factor="evidence quality"),
            evidence=["No evidence graph entries tracked yet."],
        )
    score = min(1.0, 0.2 * min(len(sources), 5))
    if sources & _HIGH_TRUST_SOURCES:
        score = min(1.0, score + 0.3)
    return FitFactor(
        key="evidence_quality", label="Evidence Quality", score=score, weight=weight, data_available=True,
        rationale=f"Evidence drawn from {len(sources)} distinct real source(s): {', '.join(sorted(sources))}.",
        evidence=[f"Evidence sources: {', '.join(sorted(sources))}"],
    )


def _career_goal_alignment(profile: StudentProfile, memory: CareerMemory, opportunity: Opportunity) -> FitFactor:
    weight = FACTOR_WEIGHTS["career_goal_alignment"]
    domain_terms = {t.lower() for t in [*opportunity.domain_tags, opportunity.category]}
    goal_terms = {g.lower() for g in profile.goals}
    active_candidates = [c for c in profile.career_candidates if c.status != "discarded"]
    candidate_terms = {c.career_name.lower() for c in active_candidates}
    matches = (goal_terms | candidate_terms) & domain_terms
    data_available = bool(profile.goals or active_candidates)

    if matches:
        score = min(1.0, 0.2 * len(matches))
        return FitFactor(
            key="career_goal_alignment", label="Career Goal Alignment", score=score, weight=weight, data_available=True,
            rationale=f"Aligns with your stated goals/career candidates: {', '.join(sorted(matches))}.",
            evidence=[f"Matching terms: {', '.join(sorted(matches))}"],
        )
    if data_available:
        return FitFactor(
            key="career_goal_alignment", label="Career Goal Alignment", score=0.5, weight=weight, data_available=True,
            rationale="Your stated goals/career candidates don't currently overlap with this opportunity's domain.",
            evidence=[
                f"Your goals: {', '.join(profile.goals) or 'none recorded'}",
                f"Active career candidates: {', '.join(c.career_name for c in active_candidates) or 'none'}",
            ],
        )
    return FitFactor(
        key="career_goal_alignment", label="Career Goal Alignment", score=0.5, weight=weight, data_available=False,
        rationale=_ABSENCE_TEMPLATE.format(factor="career goal alignment"),
        evidence=["No stated goals or active career candidates recorded yet."],
    )


def _highest_impact_gap(factors: list[FitFactor]) -> HighestImpactGap | None:
    candidates = [f for f in factors if f.key in IMPROVABLE_FACTORS and f.score < 1.0]
    if not candidates:
        return None
    best = max(candidates, key=lambda f: (1.0 - f.score) * f.weight)
    gain = round((1.0 - best.score) * best.weight, 4)
    return HighestImpactGap(factor_key=best.key, label=best.label, potential_score_gain=gain, recommended_action=best.rationale)


def _timing_rationale(opportunity: Opportunity, now: datetime) -> str:
    """Why now instead of later — grounded in the real deadline and a
    category-level norm, never asserted as a specific fact about this
    exact posting's history, which Aureon doesn't have."""
    if opportunity.application_deadline is None:
        return "Rolling admissions — no urgent deadline, but earlier applications are usually reviewed first."
    days_left = (opportunity.application_deadline - now).days
    cycle_note = CATEGORY_CYCLE_NOTES[opportunity.category]
    if days_left <= 14:
        return f"Only {days_left} days remain, and {cycle_note} — missing this window likely means waiting for the next cycle."
    if days_left <= 30:
        return f"{days_left} days remain — enough time to prepare deliberately, but {cycle_note}."
    return f"{days_left} days remain, giving real room to strengthen your fit before applying."


def _consequence_if_ignored(opportunity: Opportunity, highest_impact_gap: HighestImpactGap | None, now: datetime) -> str:
    """What will likely happen if this is skipped — grounded in the
    real deadline and the real highest-impact gap, never a fabricated
    warning."""
    if opportunity.application_deadline is not None and (opportunity.application_deadline - now).days <= 14:
        return "This application window closes soon and, per this opportunity's own timeline, won't reopen until its next cycle."
    if highest_impact_gap is not None:
        return f"The underlying gap ({highest_impact_gap.label}) will likely keep limiting fit for similar future opportunities until it's addressed."
    return "No immediate deadline is at risk, but this was a strong match worth revisiting."


def score_opportunity(
    profile: StudentProfile,
    memory: CareerMemory,
    opportunity: Opportunity,
    *,
    now: datetime,
    previous_score: float | None = None,
) -> OpportunityFitResult:
    portfolio_factor = _portfolio_strength(profile, memory, opportunity)
    factors = [
        _career_alignment(profile, memory, opportunity),
        _skill_match(profile, memory, opportunity),
        _project_match(profile, memory, opportunity),
        portfolio_factor,
        _academic_eligibility(profile, memory, opportunity),
        _location(profile, memory, opportunity),
        _deadline(opportunity, now),
        _competition_level(opportunity, portfolio_factor),
        _evidence_quality(profile, memory, opportunity),
        _career_goal_alignment(profile, memory, opportunity),
    ]
    raw_overall = sum(f.score * f.weight for f in factors)

    smoothed = False
    overall = raw_overall
    if previous_score is not None and abs(raw_overall - previous_score) <= SMOOTHING_MINOR_DELTA_THRESHOLD:
        overall = SMOOTHING_PREVIOUS_WEIGHT * previous_score + SMOOTHING_NEW_WEIGHT * raw_overall
        smoothed = True

    real_signal_count = sum(1 for f in factors if f.data_available)
    confidence = round(min(1.0, DATA_AVAILABLE_BASE + DATA_AVAILABLE_STEP * real_signal_count), 4)
    confidence_basis = {
        "factors_with_real_signal": real_signal_count, "factors_total": len(factors), "smoothed": smoothed,
    }

    if overall >= READY_THRESHOLD:
        readiness_label = "ready"
    elif overall < NOT_READY_THRESHOLD:
        readiness_label = "not_ready"
    else:
        readiness_label = "almost_ready"

    matched_skills, unmet_skills, _ = _match_skills(profile, memory, opportunity.required_skills)
    factor_by_key = {f.key: f for f in factors}
    requirements_total = len(opportunity.required_skills) + 2
    requirements_met = len(matched_skills)
    met_labels = [f"Required skill met: {s}" for s in matched_skills]
    unmet_labels = [f"Missing demonstrated evidence for required skill '{s}'." for s in unmet_skills]
    if factor_by_key["academic_eligibility"].score >= 0.75:
        requirements_met += 1
        met_labels.append("Academic eligibility requirement met.")
    else:
        unmet_labels.append("Academic level not yet confirmed as eligible for this opportunity.")
    if factor_by_key["location"].score >= 0.75:
        requirements_met += 1
        met_labels.append("Location/country requirement met.")
    else:
        unmet_labels.append("Location/country eligibility not yet confirmed for this opportunity.")

    strengths = [evidence for f in factors if f.score >= 0.75 for evidence in f.evidence]
    gaps = list(unmet_labels)
    for f in factors:
        if f.score < 0.5 and f.key not in ("academic_eligibility", "location"):
            gaps.append(f.rationale)

    highest_impact_gap = _highest_impact_gap(factors)

    return OpportunityFitResult(
        opportunity_id=opportunity.id,
        overall_score=round(overall, 4),
        confidence=confidence,
        confidence_basis=confidence_basis,
        readiness_label=readiness_label,
        factors=factors,
        highest_impact_gap=highest_impact_gap,
        timing_rationale=_timing_rationale(opportunity, now),
        consequence_if_ignored=_consequence_if_ignored(opportunity, highest_impact_gap, now),
        requirements_met=requirements_met,
        requirements_total=requirements_total,
        met_requirement_labels=met_labels,
        unmet_requirement_labels=unmet_labels,
        strengths=strengths,
        gaps=gaps,
    )


def explain_ranking(
    fit: OpportunityFitResult, same_category_fits: list[OpportunityFitResult], title_by_id: dict[str, str]
) -> str:
    """Compares `fit` only against other results in the same category —
    a more meaningful "similar opportunities" comparison than the whole
    mixed-category batch. Purely arithmetic (the single largest
    per-factor score gap), never a second LLM judgment."""
    sorted_group = sorted(same_category_fits, key=lambda f: f.overall_score, reverse=True)
    if len(sorted_group) <= 1:
        return "The only opportunity matching these filters/search in its category."

    idx = next(i for i, f in enumerate(sorted_group) if f.opportunity_id == fit.opportunity_id)
    comparator = sorted_group[1] if idx == 0 else sorted_group[idx - 1]
    verb = "Ranked above" if idx == 0 else "Ranked below"

    fit_scores = {f.key: f.score for f in fit.factors}
    comp_scores = {f.key: f.score for f in comparator.factors}
    biggest_key = max(fit_scores, key=lambda k: abs(fit_scores[k] - comp_scores.get(k, 0.0)))
    gap = fit_scores[biggest_key] - comp_scores.get(biggest_key, 0.0)
    comparator_title = title_by_id.get(comparator.opportunity_id, comparator.opportunity_id)

    return (
        f"{verb} '{comparator_title}' primarily because of a "
        f"{'stronger' if gap > 0 else 'weaker'} {biggest_key} "
        f"({fit_scores[biggest_key]:.2f} vs {comp_scores.get(biggest_key, 0.0):.2f})."
    )
