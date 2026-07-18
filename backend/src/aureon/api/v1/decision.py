from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.registry import AgentRegistry
from aureon.agents.specialized.career_intelligence.candidates import MIN_TRAITS_FOR_ANALYSIS
from aureon.agents.specialized.career_intelligence.confidence import evidence_strength_label
from aureon.agents.specialized.decision.reasoning import (
    analyze_comparison,
    analyze_parallel_universe,
    finalize_comparison,
    finalize_parallel_universe,
)
from aureon.agents.specialized.decision.simulation_pipeline import run_career_simulation
from aureon.agents.specialized.institution.matching import upsert_college_matches
from aureon.agents.specialized.mentor.matching import upsert_mentor_matches
from aureon.agents.specialized.opportunity.providers.registry import fetch_all_safely
from aureon.api.deps import (
    get_career_repository,
    get_career_world_repository,
    get_expert_repository,
    get_experiment_repository,
    get_institution_repository,
    get_journey_story_repository,
    get_knowledge_circle_repository,
    get_learning_style_repository,
    get_life_mission_repository,
    get_mentor_repository,
    get_mentorship_repository,
    get_student_profile_repository,
    get_topic_resource_repository,
    require_own_profile,
)
from aureon.domain.models.career import Career
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.career_exploration import record_exploration_event
from aureon.domain.services.decision_comparison_extra_dimensions import build_extra_comparison_dimensions
from aureon.domain.services.decision_memory import record_comparison_memory
from aureon.domain.services.decision_timeline import build_decision_timeline
from aureon.domain.services.decision_workspace_service import CareerDecisionCard, DecisionWorkspace, build_decision_workspace
from aureon.domain.services.journey_story_service import build_journey_story_view
from aureon.domain.services.learning_style_analysis_service import analyze_learning_styles
from aureon.domain.services.life_mission_engine import analyze_life_missions
from aureon.domain.services.match_recommendations import (
    top_active_institution_names,
    top_active_mentor_names,
)
from aureon.domain.services.missing_worlds_engine import analyze_missing_worlds
from aureon.domain.services.decision_view import (
    build_career_comparison_dtos,
    build_career_simulation_dtos,
    build_college_match_dtos,
    build_decision_memory_dtos,
    build_mentor_match_dtos,
    build_parallel_universe_dtos,
)
from aureon.domain.services.interest_signal_engine import analyze_relevant_interests
from aureon.domain.services.opportunity_equality import find_equality_opportunities
from aureon.domain.services.talent_pattern_engine import analyze_talents
from aureon.services.foundation.career_memory.service import get_career_memory_snapshot
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.career_world_repository import CareerWorldRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.journey_story_repository import JourneyStoryRepository
from aureon.services.supabase.repositories.knowledge_circle_repository import KnowledgeCircleRepository
from aureon.services.supabase.repositories.learning_style_repository import LearningStyleRepository
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.services.supabase.repositories.mentorship_repository import MentorshipRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CardRecommendationDTO,
    CareerComparisonRequest,
    CareerComparisonsResponse,
    CareerDecisionCardDTO,
    CareerSimulationRequest,
    CareerSimulationsResponse,
    CareerWorldDTO,
    CollegeMatchesResponse,
    DecisionExplanationDTO,
    DecisionMemoryResponse,
    DecisionTimelineResponse,
    DecisionWorkspaceResponse,
    ExperimentDTO,
    ExpertSummaryDTO,
    JourneyStoryDTO,
    KnowledgeCircleSummaryDTO,
    LearningStylePatternDTO,
    LearningStyleEvidenceItemDTO,
    LearningStyleDTO,
    LifeMissionDTO,
    LinkedExpertRefDTO,
    MentorMatchesResponse,
    MissionEvidenceItemDTO,
    MissionResonanceDTO,
    NextActionItemDTO,
    OpportunityEqualityRecommendationDTO,
    OpportunitySummaryDTO,
    ParallelUniverseRequest,
    ParallelUniverseResponse,
    InterestEvidenceItemDTO,
    RelevantInterestDTO,
    ExperimentSummaryDTO,
    ReadinessCheckpointsDTO,
    RealityCheckDTO,
    SalaryRangeDTO,
    StageProgressDTO,
    TalentEvidenceItemDTO,
    TalentPatternDTO,
    CareerJourneyMilestoneDTO,
)
from aureon.shared.types import AgentName

router = APIRouter(prefix="/students", tags=["decision"], dependencies=[Depends(require_own_profile)])

#: Comparing/simulating careers the student hasn't even been matched to
#: yet would be exactly the generic comparison this product refuses to
#: produce — both routes below require the given career_ids to already
#: be among the student's own active Career Candidates.
MIN_CAREERS_FOR_COMPARISON = 2
MAX_CAREERS_FOR_COMPARISON = 4
PARALLEL_UNIVERSE_CAREER_COUNT = 2


def _active_candidate_ids(profile) -> set[str]:
    return {c.career_id for c in profile.career_candidates if c.status != "discarded"}


async def _partner_institution_ids(institutions: InstitutionRepository) -> set[str]:
    partners = await institutions.list_institutions(is_partner=True)
    return {i.id for i in partners}


# ---------------------------------------------------------------------------
# Decide Batch 1 — Decision Workspace DTO mappers. Each one is a small,
# private, 1:1 field mapping — the same "each view module maps its own
# domain object" convention already used identically in missing_worlds.py,
# life_missions.py, learning_styles.py, hidden_potential.py,
# opportunity_equality.py, and expert_connect.py.
# Nothing here recomputes a value; every field is read straight off an
# already-computed domain object.
# ---------------------------------------------------------------------------


def _expert_summary_dto(expert: Mentor) -> ExpertSummaryDTO:
    return ExpertSummaryDTO(
        id=expert.id, name=expert.name, profession=expert.profession,
        specialization=expert.specialization, country=expert.country, city=expert.city,
        years_experience=expert.years_experience, industries=expert.industries,
        organization=expert.organization, trait_tags=expert.trait_tags,
        who_should_talk_to_me=expert.who_should_talk_to_me, photo_url=expert.photo_url,
        updated_at=expert.updated_at,
    )


def _circle_summary_dto(circle) -> KnowledgeCircleSummaryDTO:
    return KnowledgeCircleSummaryDTO(id=circle.id, name=circle.name, overview=circle.overview)


def _world_dto(world) -> CareerWorldDTO:
    return CareerWorldDTO(
        id=world.id, name=world.name, description=world.description, why_it_matters=world.why_it_matters,
        global_importance=world.global_importance, future_growth=world.future_growth,
        famous_careers=world.famous_careers, beginner_roadmap=world.beginner_roadmap,
        required_skills=world.required_skills, misconceptions=world.misconceptions,
        related_industries=world.related_industries, videos=world.videos, books=world.books,
        communities=world.communities, beginner_projects=world.beginner_projects,
        internships=world.internships, colleges=world.colleges, companies=world.companies,
        source_note=world.source_note,
    )


def _mission_dto(mission) -> LifeMissionDTO:
    return LifeMissionDTO(
        id=mission.id, name=mission.name, description=mission.description,
        famous_people=mission.famous_people, organizations=mission.organizations,
        companies=mission.companies, nonprofits=mission.nonprofits, books=mission.books,
        documentaries=mission.documentaries, podcasts=mission.podcasts, communities=mission.communities,
        real_world_examples=mission.real_world_examples, suggested_careers=mission.suggested_careers,
        projects=mission.projects, volunteering_opportunities=mission.volunteering_opportunities,
        research_areas=mission.research_areas, startup_ideas=mission.startup_ideas,
        source_note=mission.source_note,
    )


def _mission_resonance_dto(resonance) -> MissionResonanceDTO:
    return MissionResonanceDTO(
        mission=_mission_dto(resonance.mission), tier=resonance.tier, trend=resonance.trend,
        explanation=resonance.explanation,
        evidence=[
            MissionEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
            for e in resonance.evidence
        ],
    )


def _talent_pattern_dto(pattern) -> TalentPatternDTO:
    return TalentPatternDTO(
        talent=pattern.talent, tier=pattern.tier, explanation=pattern.explanation,
        evidence=[
            TalentEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
            for e in pattern.evidence
        ],
    )


def _style_dto(style) -> LearningStyleDTO:
    return LearningStyleDTO(
        id=style.id, name=style.name, description=style.description, strengths=style.strengths,
        excels_in=style.excels_in, common_struggles=style.common_struggles, study_strategies=style.study_strategies,
        note_taking_techniques=style.note_taking_techniques, memory_strategies=style.memory_strategies,
        active_learning_methods=style.active_learning_methods, project_ideas=style.project_ideas,
        practice_routines=style.practice_routines, collaboration_techniques=style.collaboration_techniques,
        learning_environments=style.learning_environments, productivity_systems=style.productivity_systems,
        recommended_books=style.recommended_books, research_backed_resources=style.research_backed_resources,
        online_courses=style.online_courses, communities=style.communities,
        ways_to_strengthen=style.ways_to_strengthen, source_note=style.source_note,
    )


def _experiment_summary_dto(experiment) -> ExperimentSummaryDTO:
    return ExperimentSummaryDTO(
        id=experiment.id, title=experiment.title, related_world=experiment.related_world,
        estimated_minutes=experiment.estimated_minutes,
    )


def _experiment_dto(experiment) -> ExperimentDTO:
    return ExperimentDTO(
        id=experiment.id, title=experiment.title, category=experiment.category,
        description=experiment.description, instructions=experiment.instructions,
        estimated_minutes=experiment.estimated_minutes, age_appropriate_note=experiment.age_appropriate_note,
        related_world=experiment.related_world, target_traits=experiment.target_traits,
        reflection_prompt=experiment.reflection_prompt, source_note=experiment.source_note,
    )


def _learning_style_pattern_dto(pattern) -> LearningStylePatternDTO:
    return LearningStylePatternDTO(
        style=_style_dto(pattern.style), tier=pattern.tier, explanation=pattern.explanation,
        evidence=[
            LearningStyleEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
            for e in pattern.evidence
        ],
        recommended_experiments=[_experiment_dto(e) for e in pattern.recommended_experiments],
    )


def _relevant_interest_dto(interest) -> RelevantInterestDTO:
    return RelevantInterestDTO(
        topic=interest.topic, explanation=interest.explanation,
        evidence=[
            InterestEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
            for e in interest.evidence
        ],
    )


def _opportunity_summary_dto(opportunity) -> OpportunitySummaryDTO:
    return OpportunitySummaryDTO(
        id=opportunity.id, title=opportunity.title, category=opportunity.category,
        organization=opportunity.organization, description=opportunity.description,
        location=opportunity.location, is_remote=opportunity.is_remote,
        application_deadline=opportunity.application_deadline, official_link=opportunity.official_link,
    )


def _opportunity_recommendation_dto(recommendation) -> OpportunityEqualityRecommendationDTO:
    return OpportunityEqualityRecommendationDTO(
        opportunity=_opportunity_summary_dto(recommendation.opportunity),
        readiness_label=recommendation.fit.readiness_label,
        likelihood_of_self_discovery=recommendation.exposure_gap.likelihood_of_self_discovery,
        why_shown=recommendation.exposure_gap.why_shown,
        contributing_factors=recommendation.exposure_gap.contributing_factors,
    )


def _journey_story_dto(story, *, career: Career, experts_by_id: dict[str, Mentor], missions_by_id: dict) -> JourneyStoryDTO:
    linked_expert = experts_by_id.get(story.linked_expert_id) if story.linked_expert_id else None
    linked_mission = missions_by_id.get(story.linked_life_mission_id) if story.linked_life_mission_id else None
    view = build_journey_story_view(story, career=career, linked_expert=linked_expert, linked_mission=linked_mission)
    return JourneyStoryDTO(
        id=view.id, career_id=view.career_id, career_name=view.career_name,
        person_label=view.person_label, background=view.background, journey=view.journey,
        challenges=view.challenges, turning_points=view.turning_points, advice=view.advice,
        lessons_learned=view.lessons_learned, trait_tags=view.trait_tags,
        timeline=[
            CareerJourneyMilestoneDTO(stage=m.stage, label=m.label, description=m.description, year_label=m.year_label)
            for m in view.timeline
        ],
        career_switch=view.career_switch, gap_year=view.gap_year,
        uncertainty_period=view.uncertainty_period, current_outcome=view.current_outcome,
        industry=view.industry, story_type=view.story_type, source_reference=view.source_reference,
        linked_expert=(
            LinkedExpertRefDTO(id=view.linked_expert.id, name=view.linked_expert.name, profession=view.linked_expert.profession)
            if view.linked_expert else None
        ),
        linked_life_mission_name=view.linked_life_mission_name,
    )


def _card_dto(card: CareerDecisionCard, *, career: Career, experts_by_id: dict[str, Mentor], missions_by_id: dict) -> CareerDecisionCardDTO:
    return CareerDecisionCardDTO(
        career_id=card.career_id, career_name=card.career_name, one_liner=card.one_liner,
        why_it_matters=card.why_it_matters, confidence_label=card.confidence_label,
        confidence_band=card.confidence_band, demand_2030=card.demand_2030, demand_2035=card.demand_2035,
        demand_2040=card.demand_2040,
        readiness=ReadinessCheckpointsDTO(
            has_reflection=card.readiness.has_reflection, has_experiment=card.readiness.has_experiment,
            has_expert_contact=card.readiness.has_expert_contact, has_explored_world=card.readiness.has_explored_world,
            has_explored_opportunity=card.readiness.has_explored_opportunity, has_simulation=card.readiness.has_simulation,
            has_knowledge_circle_engagement=card.readiness.has_knowledge_circle_engagement,
            percent=card.readiness.percent,
        ),
        reality_check=RealityCheckDTO(
            daily_work=card.reality_check.daily_work, work_life_balance=card.reality_check.work_life_balance,
            stress=card.reality_check.stress, automation_risk=card.reality_check.automation_risk,
            remote_possibility=card.reality_check.remote_possibility, travel=card.reality_check.travel,
            industry_outlook=card.reality_check.industry_outlook,
            salary_ranges=[
                SalaryRangeDTO(region=s.region, range=s.range, note=s.note) for s in card.reality_check.salary_ranges
            ],
        ),
        reasons_for=card.reasons_for, reasons_against=card.reasons_against, missing_evidence=card.missing_evidence,
        explanation=DecisionExplanationDTO(
            supporting_by_source=card.explanation.supporting_by_source,
            contradicting_by_source=card.explanation.contradicting_by_source,
            missing_evidence=card.explanation.missing_evidence, strength_traits=card.explanation.strength_traits,
        ),
        hidden_strengths=[_talent_pattern_dto(p) for p in card.hidden_strengths],
        relevant_interests=[_relevant_interest_dto(p) for p in card.relevant_interests],
        learning_style_pattern=(
            _learning_style_pattern_dto(card.learning_style_pattern) if card.learning_style_pattern else None
        ),
        unexplored_worlds=[_world_dto(w) for w in card.unexplored_worlds],
        related_life_missions=[_mission_resonance_dto(m) for m in card.related_life_missions],
        top_journey_stories=[
            _journey_story_dto(s, career=career, experts_by_id=experts_by_id, missions_by_id=missions_by_id)
            for s in card.top_journey_stories
        ],
        top_knowledge_circles=[_circle_summary_dto(c) for c in card.top_knowledge_circles],
        top_opportunities=[_opportunity_recommendation_dto(r) for r in card.top_opportunities],
        top_experts=[_expert_summary_dto(e) for e in card.top_experts],
        decision_gaps=card.decision_gaps,
        next_actions=[NextActionItemDTO(label=a.label, href=a.href) for a in card.next_actions],
        recommendation=CardRecommendationDTO(verdict=card.recommendation.verdict, reason=card.recommendation.reason),
    )


async def _build_workspace(
    profile: StudentProfile,
    candidates: list[CareerCandidate],
    *,
    careers_repo: CareerRepository,
    career_world_repo: CareerWorldRepository,
    life_mission_repo: LifeMissionRepository,
    learning_style_repo: LearningStyleRepository,
    experiment_repo: ExperimentRepository,
    expert_repo: ExpertRepository,
    journey_story_repo: JourneyStoryRepository,
    knowledge_circle_repo: KnowledgeCircleRepository,
    mentorship_repo: MentorshipRepository,
    institutions_repo: InstitutionRepository,
) -> tuple[DecisionWorkspace, dict[str, Career], dict[str, Mentor], dict]:
    """Fetches every whole catalog exactly once and calls every pure
    analysis engine exactly once, then composes `CareerDecisionCard`s for
    the given candidates. Shared by `GET /decision-workspace` and
    `POST /career-comparisons` (for the latter, `candidates` is narrowed
    to just the careers being compared) so the "fetch everything, compose
    once" logic lives in exactly one place."""
    all_careers = await careers_repo.list_careers()
    careers_by_id = {c.id: c for c in all_careers}
    career_worlds = await career_world_repo.list_worlds()
    life_missions = await life_mission_repo.list_missions()
    missions_by_id = {m.id: m for m in life_missions}
    learning_styles = await learning_style_repo.list_styles()
    experiments = await experiment_repo.list_experiments()
    experts, _total = await expert_repo.search_experts(limit=500)
    experts_by_id = {e.id: e for e in experts}
    knowledge_circles = await knowledge_circle_repo.list_circles()
    mentorships = await mentorship_repo.list_for_student(profile.student_id)

    candidate_career_ids = [c.career_id for c in candidates if c.career_id in careers_by_id]
    journey_stories_by_career: dict[str, list] = {}
    for career_id in candidate_career_ids:
        # Expert Connect / Journey Stories purpose split — explicitly scoped
        # to professional-narrative stories, matching what the readiness
        # checkpoint below actually measures (a real professional's account,
        # viewed via the career detail page's Human Stories section). Without
        # this, the new composite_student_discovery rows would silently mix
        # in here once they exist, even though nothing about this checkpoint
        # changed. "publicly_documented" exists in the Literal but has zero
        # real rows today — not filtered for here since search_stories only
        # supports one exact story_type match at a time.
        stories, _ = await journey_story_repo.search_stories(career_id=career_id, story_type="composite", limit=3)
        journey_stories_by_career[career_id] = stories

    now = datetime.now(timezone.utc)
    missing_worlds_analysis = analyze_missing_worlds(profile, career_worlds, all_careers)
    mission_resonances = analyze_life_missions(profile, life_missions, now=now)
    learning_style_patterns = analyze_learning_styles(profile, learning_styles, experiments)
    talent_patterns = analyze_talents(profile)
    relevant_interests = analyze_relevant_interests(
        profile, missing_worlds_analysis.explorations, mission_resonances, talent_patterns,
    )

    memory = get_career_memory_snapshot(profile)
    opportunities = await fetch_all_safely()
    opportunity_recommendations = find_equality_opportunities(profile, memory, opportunities, now=now)

    partner_ids = await _partner_institution_ids(institutions_repo)
    institution_names = top_active_institution_names(profile, partner_ids=partner_ids)

    workspace = build_decision_workspace(
        profile, candidates, careers_by_id,
        missing_worlds_analysis=missing_worlds_analysis, mission_resonances=mission_resonances,
        learning_style_patterns=learning_style_patterns, relevant_interests=relevant_interests,
        talent_patterns=talent_patterns, opportunity_recommendations=opportunity_recommendations,
        experts=experts, journey_stories_by_career=journey_stories_by_career,
        knowledge_circles=knowledge_circles, experiment_catalog=experiments, mentorships=mentorships,
        institution_names=institution_names, now=now,
    )
    return workspace, careers_by_id, experts_by_id, missions_by_id


@router.post("/{student_id}/career-comparisons", response_model=CareerComparisonsResponse)
async def create_career_comparison(
    student_id: str,
    request: CareerComparisonRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
    institutions_repo: InstitutionRepository = Depends(get_institution_repository),
    career_world_repo: CareerWorldRepository = Depends(get_career_world_repository),
    life_mission_repo: LifeMissionRepository = Depends(get_life_mission_repository),
    learning_style_repo: LearningStyleRepository = Depends(get_learning_style_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
    expert_repo: ExpertRepository = Depends(get_expert_repository),
    journey_story_repo: JourneyStoryRepository = Depends(get_journey_story_repository),
    knowledge_circle_repo: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
    mentorship_repo: MentorshipRepository = Depends(get_mentorship_repository),
) -> CareerComparisonsResponse:
    """Decision Lab's primary trigger — "conversation optional." Bypasses
    the LangGraph planner entirely, calling the same analyze_comparison()
    reasoning the conversational DecisionAgent uses. Decide Batch 1 adds
    6 more deterministic dimensions on top of the 15 LLM-reasoned ones
    below — see `decision_comparison_extra_dimensions.py`; the LLM call,
    `finalize_comparison`, and every dimension it produces are untouched."""
    profile = await profiles.get_or_create(student_id)
    valid_ids = [cid for cid in request.career_ids if cid in _active_candidate_ids(profile)]

    if len(valid_ids) < MIN_CAREERS_FOR_COMPARISON:
        return CareerComparisonsResponse(comparisons=build_career_comparison_dtos(profile))

    career_ids = valid_ids[:MAX_CAREERS_FOR_COMPARISON]
    all_careers = await careers_repo.list_careers()
    careers = [c for c in all_careers if c.id in career_ids]

    llm = get_llm_client()
    output = await analyze_comparison(profile, careers, llm=llm)
    now = datetime.now(timezone.utc)

    comparison = finalize_comparison(career_ids, careers, output, now)

    compared_candidates = [c for c in profile.career_candidates if c.career_id in career_ids]
    workspace, careers_by_id, _experts_by_id, _missions_by_id = await _build_workspace(
        profile, compared_candidates,
        careers_repo=careers_repo, career_world_repo=career_world_repo, life_mission_repo=life_mission_repo,
        learning_style_repo=learning_style_repo,
        experiment_repo=experiment_repo, expert_repo=expert_repo, journey_story_repo=journey_story_repo,
        knowledge_circle_repo=knowledge_circle_repo, mentorship_repo=mentorship_repo,
        institutions_repo=institutions_repo,
    )
    cards_by_career_id = {c.career_id: c for c in workspace.cards}
    comparison.dimensions.extend(build_extra_comparison_dimensions(careers, cards_by_career_id))

    profile.career_comparisons.append(comparison)
    record_comparison_memory(profile, comparison, now)
    for career_id in career_ids:
        record_exploration_event(
            profile, career_id=career_id, interaction_type="compared",
            metadata={"compared_with": [cid for cid in career_ids if cid != career_id]}, now=now,
        )
    profile.updated_at = now
    await profiles.save(profile)

    partner_ids = await _partner_institution_ids(institutions_repo)
    return CareerComparisonsResponse(
        comparisons=build_career_comparison_dtos(profile),
        recommended_colleges=top_active_institution_names(profile, partner_ids=partner_ids),
        recommended_experts=top_active_mentor_names(profile),
    )


@router.get("/{student_id}/career-comparisons", response_model=CareerComparisonsResponse)
async def get_career_comparisons(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    institutions_repo: InstitutionRepository = Depends(get_institution_repository),
) -> CareerComparisonsResponse:
    profile = await profiles.get_or_create(student_id)
    partner_ids = await _partner_institution_ids(institutions_repo)
    return CareerComparisonsResponse(
        comparisons=build_career_comparison_dtos(profile),
        recommended_colleges=top_active_institution_names(profile, partner_ids=partner_ids),
        recommended_experts=top_active_mentor_names(profile),
    )


@router.post("/{student_id}/parallel-universe", response_model=ParallelUniverseResponse)
async def create_parallel_universe_scenario(
    student_id: str,
    request: ParallelUniverseRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
) -> ParallelUniverseResponse:
    profile = await profiles.get_or_create(student_id)
    valid_ids = [cid for cid in request.career_ids if cid in _active_candidate_ids(profile)]

    if len(valid_ids) != PARALLEL_UNIVERSE_CAREER_COUNT:
        return ParallelUniverseResponse(scenarios=build_parallel_universe_dtos(profile))

    all_careers = await careers_repo.list_careers()
    careers = [c for c in all_careers if c.id in valid_ids]
    career_names = {c.id: c.name for c in careers}

    llm = get_llm_client()
    output = await analyze_parallel_universe(profile, careers, llm=llm)
    now = datetime.now(timezone.utc)

    scenario = finalize_parallel_universe(output, career_names, now)
    profile.parallel_universe_scenarios.append(scenario)
    profile.updated_at = now
    await profiles.save(profile)

    return ParallelUniverseResponse(scenarios=build_parallel_universe_dtos(profile))


@router.get("/{student_id}/parallel-universe", response_model=ParallelUniverseResponse)
async def get_parallel_universe_scenarios(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ParallelUniverseResponse:
    profile = await profiles.get_or_create(student_id)
    return ParallelUniverseResponse(scenarios=build_parallel_universe_dtos(profile))


@router.post("/{student_id}/career-simulations/analyze", response_model=CareerSimulationsResponse)
async def analyze_career_simulation_route(
    student_id: str,
    request: CareerSimulationRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
) -> CareerSimulationsResponse:
    """Career Simulator & Decision Laboratory (V11) — Decision Agent's own
    capability, no delegation. Requires 2-4 of the student's own active
    Career Candidates, same bounds as Career Comparison."""
    profile = await profiles.get_or_create(student_id)
    valid_ids = [cid for cid in request.career_ids if cid in _active_candidate_ids(profile)]

    if not (MIN_CAREERS_FOR_COMPARISON <= len(valid_ids) <= MAX_CAREERS_FOR_COMPARISON):
        return CareerSimulationsResponse(
            simulations=build_career_simulation_dtos(profile),
            insufficient_evidence=True,
            insufficient_evidence_reason=(
                f"The Career Simulator needs {MIN_CAREERS_FOR_COMPARISON}-{MAX_CAREERS_FOR_COMPARISON} "
                "of your own active career candidates — analyze more careers in Career Intelligence first."
            ),
        )

    all_careers = await careers_repo.list_careers()
    careers = [c for c in all_careers if c.id in valid_ids]
    llm = get_llm_client()

    result = await run_career_simulation(
        valid_ids, student_id=student_id, profile=profile, careers=careers, llm=llm,
    )

    if result.evidence_added:
        profile.updated_at = datetime.now(timezone.utc)
        await profiles.save(profile)

    return CareerSimulationsResponse(
        simulations=build_career_simulation_dtos(profile),
        insufficient_evidence=result.status != "completed",
        insufficient_evidence_reason=result.explanation,
        mission=mission_snapshot_to_dto(build_mission_snapshot(result.mission)),
        artifacts_updated=result.artifacts_updated,
    )


@router.get("/{student_id}/career-simulations", response_model=CareerSimulationsResponse)
async def get_career_simulations(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerSimulationsResponse:
    profile = await profiles.get_or_create(student_id)
    return CareerSimulationsResponse(simulations=build_career_simulation_dtos(profile))


@router.post("/{student_id}/mentor-matches/analyze", response_model=MentorMatchesResponse)
async def analyze_mentor_matches_route(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    mentors_repo: MentorRepository = Depends(get_mentor_repository),
) -> MentorMatchesResponse:
    profile = await profiles.get_or_create(student_id)

    if len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS:
        return MentorMatchesResponse(
            matches=build_mentor_match_dtos(profile),
            insufficient_evidence=True,
            insufficient_evidence_reason=(
                "Not enough evidence yet — keep exploring in Identity Discovery first."
            ),
        )

    mentors = await mentors_repo.list_mentors()
    llm = get_llm_client()

    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="mentor_match_analysis", primary_agent=AgentName.DECISION.value,
    )
    mentor_agent = AgentRegistry.get(AgentName.MENTOR.value)
    output = await MissionOrchestrator.delegate(
        mission,
        from_agent=AgentName.DECISION.value,
        to_agent=AgentName.MENTOR.value,
        capability=Capability.INVESTIGATION,
        reason="Decision Lab needs mentor-fit analysis, which Mentor Agent owns.",
        call=lambda: mentor_agent.find_matches(profile, mentors, llm=llm, mission=mission),
    )

    artifacts_updated: list[str] = []
    if not output.insufficient_evidence:
        mentors_by_id = {m.id: m.name for m in mentors}
        now = datetime.now(timezone.utc)
        upsert_mentor_matches(profile, output.matches, mentors_by_id, now)
        profile.updated_at = now
        await profiles.save(profile)
        artifacts_updated = ["Mentor Matches Updated"]
    MissionOrchestrator.complete(mission)

    return MentorMatchesResponse(
        matches=build_mentor_match_dtos(profile),
        insufficient_evidence=output.insufficient_evidence,
        insufficient_evidence_reason=output.insufficient_evidence_reason,
        mission=mission_snapshot_to_dto(build_mission_snapshot(mission)),
        artifacts_updated=artifacts_updated,
    )


@router.get("/{student_id}/mentor-matches", response_model=MentorMatchesResponse)
async def get_mentor_matches(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> MentorMatchesResponse:
    profile = await profiles.get_or_create(student_id)
    return MentorMatchesResponse(
        matches=build_mentor_match_dtos(profile),
        insufficient_evidence=len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS,
        insufficient_evidence_reason=None,
    )


@router.post("/{student_id}/college-matches/analyze", response_model=CollegeMatchesResponse)
async def analyze_college_matches_route(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    institutions_repo: InstitutionRepository = Depends(get_institution_repository),
) -> CollegeMatchesResponse:
    profile = await profiles.get_or_create(student_id)

    if len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS:
        return CollegeMatchesResponse(
            matches=build_college_match_dtos(profile),
            insufficient_evidence=True,
            insufficient_evidence_reason=(
                "Not enough evidence yet — keep exploring in Identity Discovery first."
            ),
        )

    institutions = await institutions_repo.list_institutions()
    llm = get_llm_client()

    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="college_match_analysis", primary_agent=AgentName.DECISION.value,
    )
    institution_agent = AgentRegistry.get(AgentName.INSTITUTION.value)
    output = await MissionOrchestrator.delegate(
        mission,
        from_agent=AgentName.DECISION.value,
        to_agent=AgentName.INSTITUTION.value,
        capability=Capability.INVESTIGATION,
        reason="Decision Lab needs institution-fit analysis, which Institution Agent owns.",
        call=lambda: institution_agent.find_matches(profile, institutions, llm=llm, mission=mission),
    )

    artifacts_updated: list[str] = []
    if not output.insufficient_evidence:
        institutions_by_id = {i.id: i.name for i in institutions}
        now = datetime.now(timezone.utc)
        upsert_college_matches(profile, output.matches, institutions_by_id, now)
        profile.updated_at = now
        await profiles.save(profile)
        artifacts_updated = ["Institution Profile Updated"]
    MissionOrchestrator.complete(mission)

    return CollegeMatchesResponse(
        matches=build_college_match_dtos(profile),
        insufficient_evidence=output.insufficient_evidence,
        insufficient_evidence_reason=output.insufficient_evidence_reason,
        mission=mission_snapshot_to_dto(build_mission_snapshot(mission)),
        artifacts_updated=artifacts_updated,
    )


@router.get("/{student_id}/college-matches", response_model=CollegeMatchesResponse)
async def get_college_matches(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CollegeMatchesResponse:
    profile = await profiles.get_or_create(student_id)
    return CollegeMatchesResponse(
        matches=build_college_match_dtos(profile),
        insufficient_evidence=len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS,
        insufficient_evidence_reason=None,
    )


@router.get("/{student_id}/decision-timeline", response_model=DecisionTimelineResponse)
async def get_decision_timeline(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> DecisionTimelineResponse:
    """Pure read, no LLM call — every milestone traces to already-stored
    data (see domain/services/decision_timeline.py)."""
    profile = await profiles.get_or_create(student_id)
    return build_decision_timeline(profile)


@router.get("/{student_id}/decision-memory", response_model=DecisionMemoryResponse)
async def get_decision_memory(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> DecisionMemoryResponse:
    profile = await profiles.get_or_create(student_id)
    return DecisionMemoryResponse(entries=build_decision_memory_dtos(profile))


@router.get("/{student_id}/decision-workspace", response_model=DecisionWorkspaceResponse)
async def get_decision_workspace(
    student_id: str,
    career_ids: str | None = None,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
    institutions_repo: InstitutionRepository = Depends(get_institution_repository),
    career_world_repo: CareerWorldRepository = Depends(get_career_world_repository),
    life_mission_repo: LifeMissionRepository = Depends(get_life_mission_repository),
    learning_style_repo: LearningStyleRepository = Depends(get_learning_style_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
    expert_repo: ExpertRepository = Depends(get_expert_repository),
    journey_story_repo: JourneyStoryRepository = Depends(get_journey_story_repository),
    knowledge_circle_repo: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
    mentorship_repo: MentorshipRepository = Depends(get_mentorship_repository),
) -> DecisionWorkspaceResponse:
    """The Decision Workspace — one real, traceable, composed card per
    active Career Candidate (or a `career_ids`-filtered subset). Pure
    composition: every score/tier/label already exists elsewhere (Career
    DNA, Hidden Potential, Missing Worlds, Life Missions, Learning
    Styles, Interest Signals, Opportunity Equality, Expert Connect,
    Journey Stories, Knowledge Circles) and is only ever filtered,
    grouped, or aggregated here — no LLM call, no writes."""
    profile = await profiles.get_or_create(student_id)
    active = [c for c in profile.career_candidates if c.status != "discarded"]

    if career_ids:
        requested = set(career_ids.split(","))
        candidates = [c for c in active if c.career_id in requested]
    else:
        candidates = active

    workspace, careers_by_id, experts_by_id, missions_by_id = await _build_workspace(
        profile, candidates,
        careers_repo=careers_repo, career_world_repo=career_world_repo, life_mission_repo=life_mission_repo,
        learning_style_repo=learning_style_repo,
        experiment_repo=experiment_repo, expert_repo=expert_repo, journey_story_repo=journey_story_repo,
        knowledge_circle_repo=knowledge_circle_repo, mentorship_repo=mentorship_repo,
        institutions_repo=institutions_repo,
    )

    return DecisionWorkspaceResponse(
        cards=[
            _card_dto(
                card, career=careers_by_id[card.career_id], experts_by_id=experts_by_id,
                missions_by_id=missions_by_id,
            )
            for card in workspace.cards
        ],
        workspace_gaps=workspace.workspace_gaps,
        overall_readiness_percent=workspace.overall_readiness_percent,
        stage_progress=StageProgressDTO(
            discover=workspace.stage_progress.discover, explore=workspace.stage_progress.explore,
            connect=workspace.stage_progress.connect,
        ),
    )
