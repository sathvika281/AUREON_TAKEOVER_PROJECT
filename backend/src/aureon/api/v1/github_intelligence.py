from fastapi import APIRouter, Depends

from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.specialized.discovery.github_pipeline import investigate_repository
from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    GitHubInvestigationRequest,
    GitHubInvestigationResponse,
    GitHubInvestigationRecordDTO,
    GitHubInvestigationsResponse,
    GitHubRepoSummaryDTO,
    GitHubSkillDTO,
    GitHubSkillRecordDTO,
)

router = APIRouter(prefix="/students", tags=["github-intelligence"], dependencies=[Depends(require_own_profile)])


@router.post("/{student_id}/github/analyze", response_model=GitHubInvestigationResponse)
async def analyze_repository_route(
    student_id: str,
    request: GitHubInvestigationRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> GitHubInvestigationResponse:
    """GitHub Intelligence (V9) — Discovery Agent's flagship capability.
    Investigates a real public GitHub repository via the real GitHub REST
    API, extracts structural engineering evidence, and updates the
    student's Career DNA/Discovery Notebook. Never fabricates repository
    information, and never lets popularity (stars/forks) influence any
    conclusion."""
    profile = await profiles.get_or_create(student_id)
    llm = get_llm_client()

    result = await investigate_repository(request.url, student_id=student_id, profile=profile, llm=llm)

    if result.evidence_added:
        await profiles.save(profile)

    repo_dto = None
    if result.repo_facts is not None:
        r = result.repo_facts.reasoning
        d = result.repo_facts.display
        repo_dto = GitHubRepoSummaryDTO(
            name=r.name, description=r.description, owner=r.owner, primary_language=r.primary_language,
            languages=r.languages, topics=r.topics, license=r.license,
            stars=d.stars, forks=d.forks, last_activity=d.last_activity,
        )

    analysis = result.analysis
    return GitHubInvestigationResponse(
        url=result.url,
        status=result.status.value,
        explanation=result.explanation,
        repo=repo_dto,
        skills=[GitHubSkillDTO(skill=s.skill, category=s.category, evidence=s.evidence) for s in result.skills],
        overall_summary=analysis.overall_summary if analysis else None,
        project_purpose=analysis.project_purpose if analysis else None,
        technical_complexity=analysis.technical_complexity if analysis else None,
        problem_solving=analysis.problem_solving if analysis else None,
        code_organization=analysis.code_organization if analysis else None,
        technology_breadth=analysis.technology_breadth if analysis else None,
        documentation_quality=analysis.documentation_quality if analysis else None,
        learning_signals=analysis.learning_signals if analysis else None,
        engineering_maturity=analysis.engineering_maturity if analysis else None,
        research_orientation=analysis.research_orientation if analysis else None,
        ai_ml_signals=analysis.ai_ml_signals if analysis else None,
        stages=result.stages,
        evidence_added=result.evidence_added,
        mission=mission_snapshot_to_dto(build_mission_snapshot(result.mission)),
        artifacts_updated=result.artifacts_updated,
    )


@router.get("/{student_id}/github-investigations", response_model=GitHubInvestigationsResponse)
async def get_github_investigations(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> GitHubInvestigationsResponse:
    """Investigation History (V12) reopens one of these by id — a pure
    read of the already-persisted record, never a re-investigation."""
    profile = await profiles.get_or_create(student_id)
    return GitHubInvestigationsResponse(investigations=[
        GitHubInvestigationRecordDTO(
            id=r.id, url=r.url, owner=r.owner, repo=r.repo, name=r.name, description=r.description,
            primary_language=r.primary_language, languages=r.languages, topics=r.topics, license=r.license,
            stars=r.stars, forks=r.forks, last_activity=r.last_activity,
            skills=[GitHubSkillRecordDTO(skill=s.skill, category=s.category, evidence=s.evidence) for s in r.skills],
            overall_summary=r.overall_summary, project_purpose=r.project_purpose,
            technical_complexity=r.technical_complexity, problem_solving=r.problem_solving,
            code_organization=r.code_organization, technology_breadth=r.technology_breadth,
            documentation_quality=r.documentation_quality, learning_signals=r.learning_signals,
            engineering_maturity=r.engineering_maturity, research_orientation=r.research_orientation,
            ai_ml_signals=r.ai_ml_signals, created_at=r.created_at,
        )
        for r in profile.github_investigations
    ])
