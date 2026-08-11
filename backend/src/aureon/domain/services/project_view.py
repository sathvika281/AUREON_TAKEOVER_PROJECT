"""Responsibility: presentation mapping + composition for the Project
Knowledge Base. Owns: ``build_project_dto``, ``build_project_detail_view``.
Mirrors ``skill_view.py``/``company_view.py`` exactly — the pattern
proven twice already, reused here rather than reinvented. Consumed by:
``api/v1/projects.py``.
"""

from aureon.domain.models.career import Career
from aureon.domain.models.company import Company
from aureon.domain.models.project import Project, ProjectAttempt
from aureon.domain.models.skill import Skill
from aureon.domain.services.company_view import build_company_dto
from aureon.domain.services.skill_view import build_skill_dto
from aureon.shared.schemas import (
    CareerSummaryDTO,
    ProjectAttemptDTO,
    ProjectAttemptEvidenceDTO,
    ProjectDetailResponse,
    ProjectDTO,
)


def build_project_dto(project: Project) -> ProjectDTO:
    return ProjectDTO(
        id=project.id,
        title=project.title,
        brief=project.brief,
        difficulty_level=project.difficulty_level,
        estimated_hours=project.estimated_hours,
        target_skill_ids=project.target_skill_ids,
        related_career_ids=project.related_career_ids,
        related_company_ids=project.related_company_ids,
        submission_type=project.submission_type,
    )


def build_project_attempt_dto(attempt: ProjectAttempt) -> ProjectAttemptDTO:
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


def build_project_detail_view(
    project: Project,
    *,
    target_skills: list[Skill],
    related_careers: list[Career],
    related_companies: list[Company],
    attempts: list[ProjectAttempt] | None = None,
) -> ProjectDetailResponse:
    """Composes a Project with the real Skills/Careers/Companies it
    points at — never stored/duplicated lists, always resolved live from
    the project's own id fields (see ProjectRepository/CareerRepository/
    SkillRepository/CompanyRepository .list_by_ids). ``attempts`` is the
    requesting student's own real attempt history for this project
    specifically (Sprint 7) — ordered most-recent-first for display,
    never collapsed to a single attempt."""
    ordered_attempts = sorted(attempts or [], key=lambda a: a.attempted_at, reverse=True)
    return ProjectDetailResponse(
        project=build_project_dto(project),
        target_skills=[build_skill_dto(s) for s in target_skills],
        related_careers=[
            CareerSummaryDTO(
                id=c.id, name=c.name, category=c.category, industry=c.industry,
                countries=c.countries, one_liner=c.one_liner, trait_tags=c.trait_tags,
            )
            for c in related_careers
        ],
        related_companies=[build_company_dto(co) for co in related_companies],
        attempts=[build_project_attempt_dto(a) for a in ordered_attempts],
    )
