"""Responsibility: Experiment Result Service — records a real completion,
reinforces the matching World Signal, and writes real Evidence Graph
entries for each of the experiment's target traits. Never reimplements
World Signal reinforcement math (domain/services/world_signal.py) or
Evidence Graph writing (domain/services/evidence_recording.py) — only
composes them, same discipline as domain/services/progressive_discovery.py."""

import uuid
from datetime import datetime

from aureon.domain.models.experiment import Experiment, ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence
from aureon.domain.services.experiment_evidence import generate_evidence_descriptions
from aureon.domain.services.world_signal import create_world_signal, reinforce_world_signal


def complete_experiment(
    profile: StudentProfile, experiment: Experiment, *, evidence: ExperimentEvidence, now: datetime
) -> ExperimentCompletion:
    completion = ExperimentCompletion(
        id=str(uuid.uuid4()),
        experiment_id=experiment.id,
        experiment_title=experiment.title,
        related_world=experiment.related_world,
        target_traits=experiment.target_traits,
        completed_at=now,
        evidence=evidence,
    )
    profile.career_experiments.append(completion)

    descriptions = generate_evidence_descriptions(experiment, evidence)
    reinforcement_items = descriptions or [f"Completed '{experiment.title}'"]

    onboarding = profile.discovery_onboarding
    existing_signal = next(
        (s for s in onboarding.world_signals if s.world == experiment.related_world), None
    )
    if existing_signal is not None:
        onboarding.world_signals = [
            reinforce_world_signal(s, reinforcement_items, now) if s.world == experiment.related_world else s
            for s in onboarding.world_signals
        ]
    else:
        new_signal = create_world_signal(experiment.related_world, now)
        onboarding.world_signals.append(reinforce_world_signal(new_signal, reinforcement_items, now))

    for trait in experiment.target_traits:
        record_new_evidence(
            profile,
            items=reinforcement_items,
            relation="supports",
            now=now,
            source="experiment",
            related_trait=trait,
        )

    return completion
