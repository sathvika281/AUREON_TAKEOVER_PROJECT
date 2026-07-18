"""Responsibility: Decide Batch 1's Decision Workspace — composes every
active `CareerCandidate`'s fit signal from the systems that already
compute it (Career DNA, Hidden Potential, Reflection Journal, Experience
Lab, Missing Worlds, Life Missions, Learning Styles, Interest Signals,
Career Explorer, Opportunity Equality, Expert Connect, Journey Stories,
Knowledge Circles) into one real, traceable, per-career
`CareerDecisionCard`. Owns: `CareerDecisionCard`, `DecisionWorkspace`,
and `build_decision_workspace`. Calls zero LLMs and computes zero new
confidence/fit/tier scores — every score already exists elsewhere
(`evidence_strength_label`, `analyze_talents`, `analyze_missing_worlds`,
`analyze_life_missions`, `analyze_learning_styles`, `analyze_relevant_interests`,
`find_equality_opportunities`) and is only ever filtered, grouped, or
aggregated here. Does NOT own persistence — every card is computed
fresh on read, same "pattern engine" convention as every system it
composes. Consumed by: `api/v1/decision.py`.
"""

from dataclasses import dataclass, field
from datetime import datetime

from aureon.agents.specialized.career_intelligence.confidence import evidence_strength_label
from aureon.agents.specialized.decision.comparison_facts import extract_comparison_facts
from aureon.domain.models.career import Career, CareerStory, SalaryRange
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.experiment import Experiment, ExperimentCompletion
from aureon.domain.models.interest_signal import RelevantInterest
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.domain.models.learning_style import LearningStylePattern
from aureon.domain.models.life_mission import MissionResonance
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.mentorship import Mentorship
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentPattern
from aureon.domain.services.experiment_history import get_completed_experiment_ids
from aureon.domain.services.missing_worlds_engine import MissingWorldsAnalysis
from aureon.domain.services.opportunity_equality import OpportunityEqualityRecommendation

TOP_N = 3

#: The real, honest mapping from `EvidenceRecord.source` to a friendly
#: product-surface label — every value here is a source that actually
#: exists on the model; nothing is fabricated to match a nicer story.
_SOURCE_LABELS: dict[str, str] = {
    "conversation": "Conversations",
    "reflection": "Reflection Journal",
    "experiment": "Experience Lab",
    "url": "URL Intelligence",
    "document": "Document Intelligence",
    "github": "GitHub Intelligence",
    "search": "Search Intelligence",
}

_CONFIDENCE_BAND_LABELS: dict[str, str] = {
    "Strong": "High Confidence",
    "Growing": "Medium Confidence",
    "Needs More Evidence": "Early Exploration",
}


def _career_terms(career: Career) -> set[str]:
    return {career.name.lower(), career.industry.lower(), *(t.lower() for t in career.trait_tags)}


def _tag_overlap(tags: list[str], terms: set[str]) -> bool:
    lowered = [t.lower() for t in tags if t]
    return any(t in term or term in t for t in lowered for term in terms)


@dataclass(frozen=True)
class NextActionItem:
    label: str
    href: str | None = None


@dataclass(frozen=True)
class DecisionExplanation:
    supporting_by_source: dict[str, list[str]] = field(default_factory=dict)
    contradicting_by_source: dict[str, list[str]] = field(default_factory=dict)
    missing_evidence: list[str] = field(default_factory=list)
    strength_traits: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReadinessCheckpoints:
    """The 7 real, itemized readiness signals — deliberately not the
    same set as `decision_gaps` below (gaps also tracks journey-story
    viewing, which isn't one of these 7; readiness also tracks
    opportunity/simulation/circle engagement, which aren't gap items).
    Both lists are honest about which real facts they check, rather
    than being forced into a false mirror-image of each other."""

    has_reflection: bool
    has_experiment: bool
    has_expert_contact: bool
    has_explored_world: bool
    has_explored_opportunity: bool
    has_simulation: bool
    has_knowledge_circle_engagement: bool

    @property
    def percent(self) -> int:
        values = [
            self.has_reflection, self.has_experiment, self.has_expert_contact, self.has_explored_world,
            self.has_explored_opportunity, self.has_simulation, self.has_knowledge_circle_engagement,
        ]
        return round(100 * sum(values) / len(values))


@dataclass(frozen=True)
class RealityCheck:
    daily_work: str
    work_life_balance: str
    stress: str
    automation_risk: str
    remote_possibility: str
    travel: str
    industry_outlook: str
    salary_ranges: list[SalaryRange] = field(default_factory=list)


@dataclass(frozen=True)
class CardRecommendation:
    verdict: str  # "continue_exploring" | "ready_to_shortlist" | "hold_for_now"
    reason: str


@dataclass(frozen=True)
class CareerDecisionCard:
    # Overview
    career_id: str
    career_name: str
    one_liner: str
    why_it_matters: str
    confidence_label: str
    confidence_band: str
    demand_2030: str
    demand_2035: str
    demand_2040: str
    readiness: ReadinessCheckpoints
    # Reality Check
    reality_check: RealityCheck
    # Evidence
    reasons_for: list[str]
    reasons_against: list[str]
    missing_evidence: list[str]
    explanation: DecisionExplanation
    # Strengths
    hidden_strengths: list[TalentPattern]
    relevant_interests: list[RelevantInterest]
    learning_style_pattern: LearningStylePattern | None
    # Explore
    unexplored_worlds: list[CareerWorld]
    related_life_missions: list[MissionResonance]
    top_journey_stories: list[CareerStory]
    top_knowledge_circles: list[KnowledgeCircle]
    top_opportunities: list[OpportunityEqualityRecommendation]
    # People
    top_experts: list[Mentor]
    # Your Next Step
    decision_gaps: list[str]
    next_actions: list[NextActionItem]
    recommendation: CardRecommendation


@dataclass(frozen=True)
class StageProgress:
    discover: bool
    explore: bool
    connect: bool


@dataclass(frozen=True)
class DecisionWorkspace:
    cards: list[CareerDecisionCard]
    workspace_gaps: list[str]
    overall_readiness_percent: int
    stage_progress: StageProgress


def _relevant_experiments(career: Career, profile: StudentProfile) -> list[ExperimentCompletion]:
    trait_tags = {t.lower() for t in career.trait_tags}
    return [c for c in profile.career_experiments if trait_tags & {t.lower() for t in c.target_traits}]


def _relevant_interests(career: Career, relevant_interests: list[RelevantInterest]) -> list[RelevantInterest]:
    terms = _career_terms(career)
    return [p for p in relevant_interests if _tag_overlap([p.topic], terms)]


def _hidden_strengths(career: Career, talent_patterns: list[TalentPattern]) -> list[TalentPattern]:
    trait_tags = {t.lower() for t in career.trait_tags}
    return [p for p in talent_patterns if p.talent.lower() in trait_tags]


def _unexplored_worlds(career: Career, missing_worlds_analysis: MissingWorldsAnalysis) -> list[CareerWorld]:
    terms = _career_terms(career)
    return [
        e.world
        for e in missing_worlds_analysis.explorations
        if e.level == "unexplored" and _tag_overlap([*e.world.related_industries, e.world.name], terms)
    ]


def _explored_world_for_career(career: Career, missing_worlds_analysis: MissingWorldsAnalysis) -> bool:
    terms = _career_terms(career)
    return any(
        e.level != "unexplored" and _tag_overlap([*e.world.related_industries, e.world.name], terms)
        for e in missing_worlds_analysis.explorations
    )


def _relevant_missions(career: Career, mission_resonances: list[MissionResonance]) -> list[MissionResonance]:
    terms = _career_terms(career)
    return [
        m
        for m in mission_resonances
        if _tag_overlap(m.mission.related_tags, terms) or _tag_overlap(m.mission.suggested_careers, terms)
    ]


def _relevant_opportunities(
    career: Career, opportunity_recommendations: list[OpportunityEqualityRecommendation]
) -> list[OpportunityEqualityRecommendation]:
    terms = _career_terms(career)
    matched = [
        r
        for r in opportunity_recommendations
        if _tag_overlap([*r.opportunity.domain_tags, r.opportunity.category], terms)
    ]
    return matched[:TOP_N]


def _relevant_experts(career: Career, experts: list[Mentor]) -> list[Mentor]:
    matched = [e for e in experts if career.id in e.career_ids]
    matched.sort(key=lambda e: e.years_experience, reverse=True)
    return matched[:TOP_N]


def _relevant_circles(career: Career, knowledge_circles: list[KnowledgeCircle]) -> list[KnowledgeCircle]:
    industry = career.industry.lower()
    matched = [c for c in knowledge_circles if industry in {i.lower() for i in c.related_career_industries}]
    return matched[:TOP_N]


def _learning_style_pattern_for(career: Career, learning_style_patterns: list[LearningStylePattern]) -> LearningStylePattern | None:
    terms = {t.lower() for t in career.trait_tags} | {s.lower() for s in career.reality.required_skills}
    for pattern in learning_style_patterns:
        if _tag_overlap(pattern.style.keywords, terms):
            return pattern
    return None


def _reality_check_for(career: Career) -> RealityCheck:
    facts = extract_comparison_facts(career)
    return RealityCheck(
        daily_work=facts["work_style"],
        work_life_balance=facts["work_life_balance"],
        stress=facts["stress"],
        automation_risk=career.future_lens.automation_risk,
        remote_possibility=career.reality.remote_possibility,
        travel=facts["travel"],
        industry_outlook=facts["future_demand"],
        salary_ranges=career.reality.salary_ranges,
    )


def _has_expert_contact(profile: StudentProfile, expert_ids: set[str], mentorships: list[Mentorship]) -> bool:
    if expert_ids & set(profile.saved_experts):
        return True
    if any(r.mentor_id in expert_ids for r in profile.guidance_requests):
        return True
    if any(b.mentor_id in expert_ids for b in profile.expert_session_bookings):
        return True
    if any(m.expert_id in expert_ids for m in mentorships):
        return True
    return False


def _has_relevant_reflection(career: Career, profile: StudentProfile) -> bool:
    terms = {career.name.lower(), career.industry.lower()}
    for entry in profile.reflection_journal:
        if not entry.response:
            continue
        lowered = entry.response.lower()
        if any(term in lowered for term in terms):
            return True
    return False


def _has_viewed_journey_story(career: Career, profile: StudentProfile) -> bool:
    return any(
        e.career_id == career.id and e.interaction_type == "story_viewed"
        for e in profile.career_exploration_history
    )


def _has_explored_opportunity(profile: StudentProfile, opportunity_ids: set[str]) -> bool:
    return any(e.ref_id in opportunity_ids for e in profile.foundation_memory.opportunities.entries)


def _has_simulation(career_id: str, profile: StudentProfile) -> bool:
    return any(career_id in sim.career_ids for sim in profile.career_simulations)


def _has_circle_engagement(profile: StudentProfile, circle_ids: set[str]) -> bool:
    return any(p.circle_id in circle_ids for p in profile.circle_resource_progress)


def _build_explanation_and_reasons(
    profile: StudentProfile, career: CareerCandidate
) -> tuple[list[str], list[str], DecisionExplanation]:
    supporting = [e for e in profile.evidence_graph if e.related_career == career.career_id and e.relation == "supports"]
    contradicting = [e for e in profile.evidence_graph if e.related_career == career.career_id and e.relation == "contradicts"]

    supporting_by_source: dict[str, list[str]] = {}
    for e in supporting:
        label = _SOURCE_LABELS.get(e.source, e.source)
        supporting_by_source.setdefault(label, []).append(e.text)

    contradicting_by_source: dict[str, list[str]] = {}
    for e in contradicting:
        label = _SOURCE_LABELS.get(e.source, e.source)
        contradicting_by_source.setdefault(label, []).append(e.text)

    strength_traits = sorted({e.related_trait for e in supporting if e.related_trait})

    reasons_for = [e.text for e in supporting]
    reasons_against = [e.text for e in contradicting]
    if career.uncertainty_reason:
        reasons_against.append(career.uncertainty_reason)

    explanation = DecisionExplanation(
        supporting_by_source=supporting_by_source,
        contradicting_by_source=contradicting_by_source,
        missing_evidence=career.missing_evidence,
        strength_traits=strength_traits,
    )
    return reasons_for, reasons_against, explanation


_GAP_MESSAGES: dict[str, str] = {
    "experiment": "You haven't completed an experience relevant to this career yet.",
    "world": "You haven't explored a world related to this career yet.",
    "expert": "You haven't talked to an expert about this career yet.",
    "journey_story": "You haven't read a journey story for this career yet.",
    "reflection": "You haven't written a reflection connected to this career yet.",
}


def _build_recommendation(confidence_label: str, readiness_percent: int, gaps: list[str]) -> CardRecommendation:
    if readiness_percent >= 60 and confidence_label == "Strong":
        return CardRecommendation(
            verdict="ready_to_shortlist",
            reason=(
                f"Your evidence confidence is {confidence_label} and you've covered {readiness_percent}% of "
                "what's useful to know before deciding — this looks ready to shortlist."
            ),
        )
    if readiness_percent < 30 or confidence_label == "Needs More Evidence":
        top_gap = gaps[0] if gaps else "gathering more real evidence"
        return CardRecommendation(
            verdict="continue_exploring",
            reason=(
                f"Your evidence confidence is {confidence_label} and you've only covered {readiness_percent}% of "
                f"what's useful to know — {top_gap.rstrip('.').lower()} is a good next step."
            ),
        )
    return CardRecommendation(
        verdict="hold_for_now",
        reason=(
            f"Your evidence confidence is {confidence_label} with {readiness_percent}% covered — worth holding "
            "here a while longer before deciding either way."
        ),
    )


def build_decision_workspace(
    profile: StudentProfile,
    candidates: list[CareerCandidate],
    careers_by_id: dict[str, Career],
    *,
    missing_worlds_analysis: MissingWorldsAnalysis,
    mission_resonances: list[MissionResonance],
    learning_style_patterns: list[LearningStylePattern],
    relevant_interests: list[RelevantInterest],
    talent_patterns: list[TalentPattern],
    opportunity_recommendations: list[OpportunityEqualityRecommendation],
    experts: list[Mentor],
    journey_stories_by_career: dict[str, list[CareerStory]],
    knowledge_circles: list[KnowledgeCircle],
    experiment_catalog: list[Experiment],
    mentorships: list[Mentorship],
    institution_names: list[str],
    now: datetime,
) -> DecisionWorkspace:
    completed_experiment_ids = get_completed_experiment_ids(profile)
    cards: list[CareerDecisionCard] = []

    for candidate in candidates:
        career = careers_by_id.get(candidate.career_id)
        if career is None:
            continue

        confidence_label = evidence_strength_label(candidate.confidence)
        confidence_band = _CONFIDENCE_BAND_LABELS[confidence_label]

        top_experts = _relevant_experts(career, experts)
        expert_ids = {e.id for e in top_experts} | {e.id for e in experts if career.id in e.career_ids}
        top_opportunities = _relevant_opportunities(career, opportunity_recommendations)
        opportunity_ids = {r.opportunity.id for r in top_opportunities}
        top_circles = _relevant_circles(career, knowledge_circles)
        circle_ids = {c.id for c in top_circles}
        top_stories = journey_stories_by_career.get(career.id, [])[:TOP_N]

        readiness = ReadinessCheckpoints(
            has_reflection=_has_relevant_reflection(career, profile),
            has_experiment=bool(_relevant_experiments(career, profile)),
            has_expert_contact=_has_expert_contact(profile, expert_ids, mentorships),
            has_explored_world=_explored_world_for_career(career, missing_worlds_analysis),
            has_explored_opportunity=_has_explored_opportunity(profile, opportunity_ids),
            has_simulation=_has_simulation(career.id, profile),
            has_knowledge_circle_engagement=_has_circle_engagement(profile, circle_ids),
        )

        gaps: list[str] = []
        if not readiness.has_experiment:
            gaps.append(_GAP_MESSAGES["experiment"])
        if not readiness.has_explored_world:
            gaps.append(_GAP_MESSAGES["world"])
        if not readiness.has_expert_contact:
            gaps.append(_GAP_MESSAGES["expert"])
        if not _has_viewed_journey_story(career, profile):
            gaps.append(_GAP_MESSAGES["journey_story"])
        if not readiness.has_reflection:
            gaps.append(_GAP_MESSAGES["reflection"])

        reasons_for, reasons_against, explanation = _build_explanation_and_reasons(profile, candidate)

        not_yet_completed_relevant_experiments = [
            e
            for e in experiment_catalog
            if e.id not in completed_experiment_ids
            and {t.lower() for t in e.target_traits} & {t.lower() for t in career.trait_tags}
        ]

        next_actions = _build_next_actions(
            career=career, readiness=readiness, top_experts=top_experts,
            not_yet_completed_experiments=not_yet_completed_relevant_experiments,
            unexplored_worlds=_unexplored_worlds(career, missing_worlds_analysis),
            top_stories=top_stories, has_viewed_story=_has_viewed_journey_story(career, profile),
            top_circles=top_circles, institution_names=institution_names, top_opportunities=top_opportunities,
        )

        recommendation = _build_recommendation(confidence_label, readiness.percent, gaps)

        cards.append(
            CareerDecisionCard(
                career_id=career.id, career_name=career.name, one_liner=career.one_liner,
                why_it_matters=candidate.why_it_matches, confidence_label=confidence_label,
                confidence_band=confidence_band, demand_2030=career.future_lens.demand_2030,
                demand_2035=career.future_lens.demand_2035, demand_2040=career.future_lens.demand_2040,
                readiness=readiness, reality_check=_reality_check_for(career),
                reasons_for=reasons_for, reasons_against=reasons_against,
                missing_evidence=candidate.missing_evidence, explanation=explanation,
                hidden_strengths=_hidden_strengths(career, talent_patterns),
                relevant_interests=_relevant_interests(career, relevant_interests),
                learning_style_pattern=_learning_style_pattern_for(career, learning_style_patterns),
                unexplored_worlds=_unexplored_worlds(career, missing_worlds_analysis),
                related_life_missions=_relevant_missions(career, mission_resonances),
                top_journey_stories=top_stories, top_knowledge_circles=top_circles,
                top_opportunities=top_opportunities, top_experts=top_experts,
                decision_gaps=gaps, next_actions=next_actions, recommendation=recommendation,
            )
        )

    workspace_gaps = _aggregate_gaps(cards)
    overall_readiness_percent = (
        round(sum(c.readiness.percent for c in cards) / len(cards)) if cards else 0
    )
    stage_progress = _stage_progress(profile, mentorships)

    return DecisionWorkspace(
        cards=cards, workspace_gaps=workspace_gaps,
        overall_readiness_percent=overall_readiness_percent, stage_progress=stage_progress,
    )


def _aggregate_gaps(cards: list[CareerDecisionCard]) -> list[str]:
    """The most common gap message across every card, most-frequent
    first — a real aggregate of already-computed per-card gaps, not a
    new signal."""
    counts: dict[str, int] = {}
    for card in cards:
        for gap in card.decision_gaps:
            counts[gap] = counts.get(gap, 0) + 1
    return sorted(counts, key=lambda g: counts[g], reverse=True)[:5]


def _stage_progress(profile: StudentProfile, mentorships: list[Mentorship]) -> StageProgress:
    discover = profile.discovery_onboarding.completed or any(
        s.score is not None and s.score > 0 for s in profile.career_dna.traits.values()
    )
    explore = bool(profile.career_exploration_history) or bool(profile.career_candidates)
    connect = bool(
        profile.saved_experts or profile.guidance_requests or profile.expert_session_bookings or mentorships
    )
    return StageProgress(discover=discover, explore=explore, connect=connect)


def _build_next_actions(
    *,
    career: Career,
    readiness: ReadinessCheckpoints,
    top_experts: list[Mentor],
    not_yet_completed_experiments: list[Experiment],
    unexplored_worlds: list[CareerWorld],
    top_stories: list[CareerStory],
    has_viewed_story: bool,
    top_circles: list[KnowledgeCircle],
    institution_names: list[str],
    top_opportunities: list[OpportunityEqualityRecommendation],
) -> list[NextActionItem]:
    """Deterministic — every action traces to a real gap or real data,
    same discipline as `simulation_next_actions.py::build_next_actions`.
    Capped at 5, ordered by how central the gap is."""
    actions: list[NextActionItem] = []

    if not readiness.has_expert_contact:
        if top_experts:
            actions.append(NextActionItem(f"Talk to {top_experts[0].name}", "/experience/expert-connect"))
        else:
            actions.append(NextActionItem("Browse Expert Connect for someone in this field", "/experience/expert-connect"))

    if not readiness.has_experiment and not_yet_completed_experiments:
        actions.append(NextActionItem(f"Complete '{not_yet_completed_experiments[0].title}'", "/discover/experience-lab"))

    if unexplored_worlds:
        actions.append(NextActionItem(f"Explore the {unexplored_worlds[0].name} world", "/explore/exposure-universe"))

    if top_stories and not has_viewed_story:
        actions.append(NextActionItem(f"Read {top_stories[0].person_label}'s journey story", "/experience/journey-stories"))

    if top_circles:
        actions.append(NextActionItem(f"Join the {top_circles[0].name} Knowledge Circle", "/experience/knowledge-circles"))

    if institution_names:
        actions.append(NextActionItem(f"Visit {institution_names[0]}", "/experience/college-collaboration"))

    if top_opportunities:
        actions.append(NextActionItem(f"Apply for {top_opportunities[0].opportunity.title}", "/explore/opportunity-equality"))

    return actions[:5]
