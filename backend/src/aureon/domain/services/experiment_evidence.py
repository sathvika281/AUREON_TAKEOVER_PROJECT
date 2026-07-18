"""Responsibility: Evidence Generation — turns a student's raw
ExperimentEvidence self-report (boolean flags + a free-text reflection)
into real, human-readable evidence strings for the Evidence Graph and
for World Signal reinforcement. Never fabricates a signal that wasn't
actually reported."""

from aureon.domain.models.experiment import Experiment, ExperimentEvidence

_FLAG_DESCRIPTIONS: dict[str, str] = {
    "enjoyment": "Reported enjoying '{title}'",
    "curiosity": "Reported curiosity while completing '{title}'",
    "frustration": "Reported frustration while completing '{title}'",
    "persistence": "Reported persisting through '{title}'",
    "confidence": "Reported feeling confident completing '{title}'",
}


def generate_evidence_descriptions(experiment: Experiment, evidence: ExperimentEvidence) -> list[str]:
    """Honest, possibly-empty list — absence of a flag is never treated
    as a negative signal, only as nothing reported for that dimension."""
    descriptions: list[str] = []
    for flag, template in _FLAG_DESCRIPTIONS.items():
        if getattr(evidence, flag):
            descriptions.append(template.format(title=experiment.title))
    if evidence.reflection.strip():
        descriptions.append(f"Reflected: {evidence.reflection.strip()}")
    return descriptions
