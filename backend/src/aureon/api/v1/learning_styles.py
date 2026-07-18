from fastapi import APIRouter, Depends

from aureon.api.deps import (
    get_experiment_repository,
    get_learning_style_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.learning_style_analysis_service import analyze_learning_styles
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.learning_style_repository import LearningStyleRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    ExperimentDTO,
    LearningStyleDTO,
    LearningStyleEvidenceItemDTO,
    LearningStylePatternDTO,
    LearningStylesResponse,
)

router = APIRouter(prefix="/students", tags=["learning-styles"], dependencies=[Depends(require_own_profile)])


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


def _experiment_dto(experiment) -> ExperimentDTO:
    return ExperimentDTO(
        id=experiment.id, title=experiment.title, category=experiment.category,
        description=experiment.description, instructions=experiment.instructions,
        estimated_minutes=experiment.estimated_minutes, age_appropriate_note=experiment.age_appropriate_note,
        related_world=experiment.related_world, target_traits=experiment.target_traits,
        reflection_prompt=experiment.reflection_prompt, source_note=experiment.source_note,
    )


@router.get("/{student_id}/learning-styles", response_model=LearningStylesResponse)
async def get_learning_styles(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    styles_repo: LearningStyleRepository = Depends(get_learning_style_repository),
    experiments_repo: ExperimentRepository = Depends(get_experiment_repository),
) -> LearningStylesResponse:
    """How a student naturally learns best — inferred from real
    accumulated evidence, never a quiz. See
    domain/services/learning_style_analysis_service.py."""
    profile = await profiles.get_or_create(student_id)
    styles = await styles_repo.list_styles()
    experiments = await experiments_repo.list_experiments()

    patterns = analyze_learning_styles(profile, styles, experiments)

    return LearningStylesResponse(
        patterns=[
            LearningStylePatternDTO(
                style=_style_dto(p.style), tier=p.tier, explanation=p.explanation,
                evidence=[
                    LearningStyleEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
                    for e in p.evidence
                ],
                recommended_experiments=[_experiment_dto(e) for e in p.recommended_experiments],
            )
            for p in patterns
        ]
    )
