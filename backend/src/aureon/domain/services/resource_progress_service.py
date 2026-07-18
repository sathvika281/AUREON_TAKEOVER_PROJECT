"""Responsibility: Knowledge Circles' per-student bookmark/completion
state — pure, testable toggle actions over
``StudentProfile.circle_resource_progress``, same idempotent-toggle
discipline as ``career_experience_actions.py::save_expert``. Consumed
by: ``api/v1/knowledge_circles.py``.
"""

import uuid
from datetime import datetime, timezone

from aureon.domain.models.circle_resource_progress import CircleResourceProgress, CircleResourceStatus
from aureon.domain.models.student_profile import StudentProfile


def _find(
    profile: StudentProfile,
    *,
    circle_id: str,
    resource_type: str,
    resource_label: str,
    status: CircleResourceStatus,
) -> CircleResourceProgress | None:
    for entry in profile.circle_resource_progress:
        if (
            entry.circle_id == circle_id
            and entry.resource_type == resource_type
            and entry.resource_label == resource_label
            and entry.status == status
        ):
            return entry
    return None


def _toggle(
    profile: StudentProfile,
    *,
    circle_id: str,
    resource_type: str,
    resource_label: str,
    status: CircleResourceStatus,
) -> list[CircleResourceProgress]:
    existing = _find(
        profile, circle_id=circle_id, resource_type=resource_type, resource_label=resource_label, status=status
    )
    if existing is not None:
        profile.circle_resource_progress.remove(existing)
    else:
        profile.circle_resource_progress.append(
            CircleResourceProgress(
                id=str(uuid.uuid4()), circle_id=circle_id, resource_type=resource_type,
                resource_label=resource_label, status=status,
            )
        )
    profile.updated_at = datetime.now(timezone.utc)
    return profile.circle_resource_progress


def toggle_bookmark(
    profile: StudentProfile, *, circle_id: str, resource_type: str, resource_label: str
) -> list[CircleResourceProgress]:
    return _toggle(
        profile, circle_id=circle_id, resource_type=resource_type, resource_label=resource_label,
        status="bookmarked",
    )


def toggle_completed(
    profile: StudentProfile, *, circle_id: str, resource_type: str, resource_label: str
) -> list[CircleResourceProgress]:
    return _toggle(
        profile, circle_id=circle_id, resource_type=resource_type, resource_label=resource_label,
        status="completed",
    )


def list_progress_for_circle(profile: StudentProfile, circle_id: str) -> list[CircleResourceProgress]:
    return [entry for entry in profile.circle_resource_progress if entry.circle_id == circle_id]
