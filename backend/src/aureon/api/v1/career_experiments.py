from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_experiment_repository,
    get_life_mission_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.models.experiment import Experiment, ExperimentEvidence
from aureon.domain.services.experience_lab_service import build_experience_lab_view
from aureon.domain.services.experiment_history import get_completed_experiment_ids
from aureon.domain.services.experiment_result import complete_experiment
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    EmergingMissionDTO,
    ExperienceLabViewResponse,
    ExperimentCompletionDTO,
    ExperimentDTO,
    ExperimentEvidenceDTO,
    ExperimentEvidenceRequest,
    ExperimentsResponse,
    LifeMissionDTO,
    MissionEvidenceItemDTO,
)

router = APIRouter(prefix="/students", tags=["career-experiments"], dependencies=[Depends(require_own_profile)])


def _build_experiment_dto(experiment: Experiment) -> ExperimentDTO:
    return ExperimentDTO(
        id=experiment.id,
        title=experiment.title,
        category=experiment.category,
        description=experiment.description,
        instructions=experiment.instructions,
        estimated_minutes=experiment.estimated_minutes,
        age_appropriate_note=experiment.age_appropriate_note,
        related_world=experiment.related_world,
        target_traits=experiment.target_traits,
        related_life_mission_ids=experiment.related_life_mission_ids,
        reflection_prompt=experiment.reflection_prompt,
        source_note=experiment.source_note,
    )


def _build_completion_dto(completion) -> ExperimentCompletionDTO:
    return ExperimentCompletionDTO(
        id=completion.id,
        experiment_id=completion.experiment_id,
        experiment_title=completion.experiment_title,
        related_world=completion.related_world,
        completed_at=completion.completed_at,
        evidence=ExperimentEvidenceDTO(
            enjoyment=completion.evidence.enjoyment,
            curiosity=completion.evidence.curiosity,
            frustration=completion.evidence.frustration,
            persistence=completion.evidence.persistence,
            confidence=completion.evidence.confidence,
            reflection=completion.evidence.reflection,
        ),
    )


@router.get("/{student_id}/experience-lab", response_model=ExperienceLabViewResponse)
async def get_experience_lab_view(
    student_id: str,
    experiments: ExperimentRepository = Depends(get_experiment_repository),
    missions_repo: LifeMissionRepository = Depends(get_life_mission_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ExperienceLabViewResponse:
    """The unified Experience Lab view — composes the real experiment
    catalog with real Life Mission resonance (domain/services/
    experience_lab_service.py::build_experience_lab_view). Purely
    additive: does not change how /experiments or
    /experiments/{id}/complete behave."""
    profile = await profiles.get_or_create(student_id)
    catalog = await experiments.list_experiments()
    missions = await missions_repo.list_missions()

    view = build_experience_lab_view(
        profile, experiments=catalog, missions=missions, now=datetime.now(timezone.utc)
    )

    return ExperienceLabViewResponse(
        recommended=[_build_experiment_dto(e) for e in view.recommended],
        mission_experiences=[_build_experiment_dto(e) for e in view.mission_experiences],
        career_experiences=[_build_experiment_dto(e) for e in view.career_experiences],
        completed=[_build_completion_dto(c) for c in view.completed],
        completed_experiment_ids=sorted(view.completed_experiment_ids),
        emerging_missions=[
            EmergingMissionDTO(
                mission=_mission_dto(em.resonance.mission),
                tier=em.resonance.tier,
                trend=em.resonance.trend,
                explanation=em.resonance.explanation,
                evidence=[
                    MissionEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
                    for e in em.resonance.evidence
                ],
                suggested_experience=(
                    _build_experiment_dto(em.suggested_experience) if em.suggested_experience else None
                ),
            )
            for em in view.emerging_missions
        ],
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


@router.get("/{student_id}/experiments", response_model=ExperimentsResponse)
async def list_experiments(
    student_id: str,
    experiments: ExperimentRepository = Depends(get_experiment_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ExperimentsResponse:
    """Real catalog + real completion status in one call — small
    achievable activities, never framed as an examination."""
    profile = await profiles.get_or_create(student_id)
    catalog = await experiments.list_experiments()
    return ExperimentsResponse(
        experiments=[_build_experiment_dto(e) for e in catalog],
        completed_experiment_ids=sorted(get_completed_experiment_ids(profile)),
    )


@router.post("/{student_id}/experiments/{experiment_id}/complete", response_model=ExperimentCompletionDTO)
async def complete_experiment_route(
    student_id: str,
    experiment_id: str,
    body: ExperimentEvidenceRequest,
    experiments: ExperimentRepository = Depends(get_experiment_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ExperimentCompletionDTO:
    """Records a real completion, reinforces the matching World Signal,
    and writes real Evidence Graph entries for each target trait — see
    domain/services/experiment_result.py."""
    experiment = await experiments.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    profile = await profiles.get_or_create(student_id)
    evidence = ExperimentEvidence(
        enjoyment=body.enjoyment,
        curiosity=body.curiosity,
        frustration=body.frustration,
        persistence=body.persistence,
        confidence=body.confidence,
        reflection=body.reflection,
    )
    completion = complete_experiment(profile, experiment, evidence=evidence, now=datetime.now(timezone.utc))
    await profiles.save(profile)

    return ExperimentCompletionDTO(
        id=completion.id,
        experiment_id=completion.experiment_id,
        experiment_title=completion.experiment_title,
        related_world=completion.related_world,
        completed_at=completion.completed_at,
        evidence=ExperimentEvidenceDTO(
            enjoyment=completion.evidence.enjoyment,
            curiosity=completion.evidence.curiosity,
            frustration=completion.evidence.frustration,
            persistence=completion.evidence.persistence,
            confidence=completion.evidence.confidence,
            reflection=completion.evidence.reflection,
        ),
    )
