"""Responsibility: Experiment Service — read access to the Career
Experiments catalog. A thin wrapper over ExperimentRepository, kept as
its own module (rather than inlined into the route) to match this
codebase's convention of a named domain-service layer between routes
and repositories."""

from aureon.domain.models.experiment import Experiment
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository


async def list_active_experiments(experiments: ExperimentRepository) -> list[Experiment]:
    return await experiments.list_experiments()


async def get_experiment_or_none(experiments: ExperimentRepository, experiment_id: str) -> Experiment | None:
    return await experiments.get_experiment(experiment_id)
