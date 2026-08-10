"""Responsibility: Project Result Service — records a real attempt and
writes real Evidence Graph entries for each of the project's target
skills. Mirrors domain/services/experiment_result.py's composition
discipline (never reimplements Evidence Graph writing, only composes
it), but does NOT reinforce a World Signal — that mechanism is
Experiment-specific (tied to related_world, which Project doesn't have;
see docs/SPRINT_3.md's Explicit Out-of-Scope Items).

Genuine-engagement gate: completion alone is not evidence. Evidence is
only written when the student reported something real (an artifact URL
or a reflection) — see project_evidence.py."""

import uuid
from datetime import datetime

from aureon.domain.models.project import Project, ProjectAttempt, ProjectAttemptEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence
from aureon.domain.services.project_evidence import generate_project_evidence_descriptions


def complete_project_attempt(
    profile: StudentProfile, project: Project, *, evidence: ProjectAttemptEvidence, now: datetime
) -> ProjectAttempt:
    attempt = ProjectAttempt(
        id=str(uuid.uuid4()),
        project_id=project.id,
        project_title=project.title,
        target_skill_ids=project.target_skill_ids,
        attempted_at=now,
        evidence=evidence,
    )
    profile.project_attempts.append(attempt)

    descriptions = generate_project_evidence_descriptions(project, evidence)
    if descriptions:
        for skill_id in project.target_skill_ids:
            record_new_evidence(
                profile,
                items=descriptions,
                relation="supports",
                now=now,
                source="project",
                related_skill=skill_id,
            )

    return attempt
