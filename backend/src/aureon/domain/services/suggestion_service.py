"""Responsibility: Suggestion business logic — submitting a contribution
and transitioning its review status. Owns: ``submit_suggestion``,
``update_status``. Does NOT own persistence (``suggestion_repository.py``)
or reviewer authorization (``api/deps.py::require_reviewer_secret``).
Consumed by: ``api/v1/suggestions.py``.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, get_args

from aureon.domain.models.suggestion import Suggestion, SuggestionCategory, SuggestionStatus

_VALID_STATUSES = set(get_args(SuggestionStatus))


def submit_suggestion(
    *,
    student_id: str,
    category: SuggestionCategory,
    title: str,
    description: str,
    source_url: str | None = None,
    context_type: str | None = None,
    context_id: str | None = None,
    context_metadata: dict[str, Any] | None = None,
) -> Suggestion:
    """Invalid ``category`` raises ``pydantic.ValidationError`` here (the
    ``Literal`` is enforced by ``Suggestion`` itself) — the route
    translates that into a 422."""
    return Suggestion(
        id=str(uuid.uuid4()),
        student_id=student_id,
        category=category,
        title=title.strip(),
        description=description.strip(),
        source_url=source_url,
        context_type=context_type,
        context_id=context_id,
        context_metadata=context_metadata or {},
    )


def update_status(
    suggestion: Suggestion, *, status: str, review_notes: str | None = None
) -> Suggestion:
    """A reviewer action — never called from student-facing code.

    ``model_copy(update={...})`` deliberately skips re-validation (that's
    what makes it cheap for the hardcoded-literal updates elsewhere, e.g.
    ``mentorship_service.py::accept``) — since ``status`` here comes from
    reviewer input rather than a hardcoded literal, it's checked
    explicitly against ``SuggestionStatus`` first, raising ``ValueError``
    (the route translates that into a 422) rather than silently writing
    an invalid value onto the model.
    """
    if status not in _VALID_STATUSES:
        raise ValueError(f"Invalid suggestion status: {status!r}")
    update: dict[str, Any] = {
        "status": status,
        "reviewed_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    if review_notes is not None:
        update["review_notes"] = review_notes
    return suggestion.model_copy(update=update)
