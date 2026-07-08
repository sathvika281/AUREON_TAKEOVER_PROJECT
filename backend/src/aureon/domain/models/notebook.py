from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class NotebookEntry(BaseModel):
    """One entry in the student's long-term Discovery Notebook — persisted
    server-side (on ``StudentProfile.notebook_entries``) so it survives a
    refresh or a new device, unlike the client-side reconstruction this
    replaces.

    Two shapes share one model rather than two parallel systems:
    - ``"observation"``: a Career DNA reading changed — uses `text`,
      `source`, `confidence_label`, `related_trait`.
    - ``"belief_revision"``: a hypothesis's lifecycle state changed — uses
      `previous_state`, `new_evidence`, `updated_belief`, `reason`,
      `related_hypothesis`. `text` is still set to a one-line summary for
      any caller that just wants a flat sentence.
    """

    id: str
    kind: Literal["observation", "belief_revision"]
    text: str
    source: str
    related_trait: str | None = None
    related_hypothesis: str | None = None
    related_career: str | None = None
    confidence_label: str | None = None
    previous_state: str | None = None
    new_evidence: str | None = None
    updated_belief: str | None = None
    reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
