from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

SuggestionCategory = Literal[
    "career",
    "opportunity",
    "resource",
    "feature_request",
    "correction",
    "general_feedback",
    #: Reserved for a future "Share My Journey" submission flow (Journey
    #: Stories' student-discovery purpose split) — the category exists so
    #: the architecture stays extensible now; no submission UI, moderation
    #: workflow, or auto-publishing is built in this batch.
    "student_story",
]
SuggestionStatus = Literal[
    "pending",
    "under_review",
    "approved",
    "rejected",
    "implemented",
    "needs_information",
]


class Suggestion(BaseModel):
    """A student-submitted contribution — a missing career, an outdated
    scholarship deadline, a feature idea, general feedback. Always starts
    ``pending`` and is never used as trusted career evidence or
    auto-published into the knowledge base; only a holder of the
    reviewer secret (``api/deps.py::require_reviewer_secret`` — there is
    no admin/staff role anywhere in this system to gate on instead) can
    move it to ``approved``/``rejected``/``implemented``. Approval itself
    never creates a ``Career``/``Opportunity``/``Resource`` row — that
    stays a deliberate, separate, manual integration step.

    ``context_type``/``context_id``/``context_metadata`` is one flexible
    attachment point (e.g. a student reporting an outdated scholarship
    deadline from its detail screen) instead of a column per possible
    origin — most submissions won't have one at all.
    """

    id: str
    student_id: str
    category: SuggestionCategory
    title: str
    description: str
    source_url: str | None = None
    context_type: str | None = None
    context_id: str | None = None
    context_metadata: dict[str, Any] = Field(default_factory=dict)
    status: SuggestionStatus = "pending"
    review_notes: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
