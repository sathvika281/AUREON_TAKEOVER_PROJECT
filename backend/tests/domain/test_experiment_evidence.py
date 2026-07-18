from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment, ExperimentEvidence
from aureon.domain.services.experiment_evidence import generate_evidence_descriptions

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1",
        title="Debug a Tiny Bug",
        category="debug_code",
        description="d",
        instructions="i",
        estimated_minutes=10,
        age_appropriate_note="note",
        related_world="AI",
        target_traits=["analytical_thinking"],
        reflection_prompt="p",
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def test_honest_empty_list_when_nothing_reported():
    experiment = _experiment()
    evidence = ExperimentEvidence()

    assert generate_evidence_descriptions(experiment, evidence) == []


def test_real_description_per_true_flag():
    experiment = _experiment()
    evidence = ExperimentEvidence(enjoyment=True, persistence=True)

    descriptions = generate_evidence_descriptions(experiment, evidence)

    assert "Reported enjoying 'Debug a Tiny Bug'" in descriptions
    assert "Reported persisting through 'Debug a Tiny Bug'" in descriptions
    assert len(descriptions) == 2


def test_reflection_text_included_verbatim():
    experiment = _experiment()
    evidence = ExperimentEvidence(reflection="  I liked tracing the bug.  ")

    descriptions = generate_evidence_descriptions(experiment, evidence)

    assert "Reflected: I liked tracing the bug." in descriptions


def test_blank_reflection_not_included():
    experiment = _experiment()
    evidence = ExperimentEvidence(reflection="   ")

    assert generate_evidence_descriptions(experiment, evidence) == []
