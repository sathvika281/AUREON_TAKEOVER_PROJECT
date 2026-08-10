"""Responsibility: Evidence Generation — turns a student's raw
ProjectAttemptEvidence self-report (an artifact URL and/or a free-text
reflection) into real, human-readable evidence strings for the Evidence
Graph. Never fabricates a signal that wasn't actually reported — mirrors
domain/services/experiment_evidence.py's honesty discipline, but for a
structurally different evidence shape (a demonstrated artifact, not a
reported feeling)."""

from aureon.domain.models.project import Project, ProjectAttemptEvidence


def generate_project_evidence_descriptions(project: Project, evidence: ProjectAttemptEvidence) -> list[str]:
    """Honest, possibly-empty list. An empty result means the genuine-
    engagement gate in complete_project_attempt() withholds evidence
    entirely — unlike Experiment, Project has no boolean-flag fallback to
    fall back on, since completion alone was never meant to count."""
    descriptions: list[str] = []
    if evidence.artifact_url:
        descriptions.append(f"Submitted a real artifact for '{project.title}': {evidence.artifact_url}")
    if evidence.reflection.strip():
        descriptions.append(f"Reflected on completing '{project.title}': {evidence.reflection.strip()}")
    return descriptions
