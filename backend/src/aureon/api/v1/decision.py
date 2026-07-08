from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.registry import AgentRegistry
from aureon.agents.specialized.career_intelligence.candidates import MIN_TRAITS_FOR_ANALYSIS
from aureon.agents.specialized.decision.reasoning import (
    analyze_comparison,
    analyze_parallel_universe,
    finalize_comparison,
    finalize_parallel_universe,
)
from aureon.agents.specialized.decision.simulation_pipeline import run_career_simulation
from aureon.agents.specialized.institution.matching import upsert_college_matches
from aureon.agents.specialized.mentor.matching import upsert_mentor_matches
from aureon.api.deps import (
    get_career_repository,
    get_institution_repository,
    get_mentor_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.career_exploration import record_exploration_event
from aureon.domain.services.decision_memory import record_comparison_memory
from aureon.domain.services.decision_timeline import build_decision_timeline
from aureon.domain.services.match_recommendations import (
    top_active_institution_names,
    top_active_mentor_names,
)
from aureon.domain.services.decision_view import (
    build_career_comparison_dtos,
    build_career_simulation_dtos,
    build_college_match_dtos,
    build_decision_memory_dtos,
    build_mentor_match_dtos,
    build_parallel_universe_dtos,
)
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CareerComparisonRequest,
    CareerComparisonsResponse,
    CareerSimulationRequest,
    CareerSimulationsResponse,
    CollegeMatchesResponse,
    DecisionMemoryResponse,
    DecisionTimelineResponse,
    MentorMatchesResponse,
    ParallelUniverseRequest,
    ParallelUniverseResponse,
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


@router.post("/{student_id}/career-comparisons", response_model=CareerComparisonsResponse)
async def create_career_comparison(
    student_id: str,
    request: CareerComparisonRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
    institutions_repo: InstitutionRepository = Depends(get_institution_repository),
) -> CareerComparisonsResponse:
    """Decision Lab's primary trigger — "conversation optional." Bypasses
    the LangGraph planner entirely, calling the same analyze_comparison()
    reasoning the conversational DecisionAgent uses."""
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
