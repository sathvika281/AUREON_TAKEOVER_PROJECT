from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_company_repository,
    get_project_repository,
    get_skill_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.models.project import ProjectAttemptEvidence
from aureon.domain.services.project_result import complete_project_attempt
from aureon.domain.services.project_view import build_project_detail_view, build_project_dto
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.company_repository import CompanyRepository
from aureon.services.supabase.repositories.project_repository import ProjectRepository
from aureon.services.supabase.repositories.skill_repository import SkillRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    ProjectAttemptDTO,
    ProjectAttemptEvidenceDTO,
    ProjectAttemptEvidenceRequest,
    ProjectDetailResponse,
    ProjectsResponse,
)

# Open — no gating, same catalog-browsing openness as /skills, /companies.
router = APIRouter(prefix="/projects", tags=["projects"])

# Student-scoped — a project attempt is genuinely per-student, mirrors
# career_experiments.router's own-profile gating.
student_router = APIRouter(
    prefix="/students", tags=["projects"], dependencies=[Depends(require_own_profile)]
)


@router.get("", response_model=ProjectsResponse)
async def list_projects(
    difficulty_level: str | None = None,
    projects: ProjectRepository = Depends(get_project_repository),
) -> ProjectsResponse:
    """Project catalog browse endpoint — always open, no gating, same as
    every other knowledge-base catalog (Skills, Companies, Trends)."""
    results = await projects.list_projects(difficulty_level=difficulty_level)
    return ProjectsResponse(projects=[build_project_dto(p) for p in results])


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    projects: ProjectRepository = Depends(get_project_repository),
    skills: SkillRepository = Depends(get_skill_repository),
    careers: CareerRepository = Depends(get_career_repository),
    companies: CompanyRepository = Depends(get_company_repository),
) -> ProjectDetailResponse:
    project = await projects.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    target_skills = await skills.list_by_ids(project.target_skill_ids)
    related_careers = await careers.list_by_ids(project.related_career_ids)
    related_companies = await companies.list_by_ids(project.related_company_ids)

    return build_project_detail_view(
        project,
        target_skills=target_skills,
        related_careers=related_careers,
        related_companies=related_companies,
    )


def _attempt_dto(attempt) -> ProjectAttemptDTO:
    return ProjectAttemptDTO(
        id=attempt.id,
        project_id=attempt.project_id,
        project_title=attempt.project_title,
        target_skill_ids=attempt.target_skill_ids,
        attempted_at=attempt.attempted_at,
        evidence=ProjectAttemptEvidenceDTO(
            artifact_url=attempt.evidence.artifact_url,
            reflection=attempt.evidence.reflection,
        ),
    )


@student_router.post("/{student_id}/projects/{project_id}/complete", response_model=ProjectAttemptDTO)
async def complete_project_attempt_route(
    student_id: str,
    project_id: str,
    body: ProjectAttemptEvidenceRequest,
    projects: ProjectRepository = Depends(get_project_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ProjectAttemptDTO:
    """Records a real attempt and writes real Evidence Graph entries for
    each target skill, gated on genuine engagement — see
    domain/services/project_result.py. Unlike experiment completion, does
    NOT reinforce a World Signal (Project has no related_world; see
    docs/SPRINT_3.md's Explicit Out-of-Scope Items)."""
    project = await projects.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    profile = await profiles.get_or_create(student_id)
    evidence = ProjectAttemptEvidence(artifact_url=body.artifact_url, reflection=body.reflection)
    attempt = complete_project_attempt(profile, project, evidence=evidence, now=datetime.now(timezone.utc))
    await profiles.save(profile)

    return _attempt_dto(attempt)
