from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    """One piece of evidence, structured rather than a flat string — the
    Evidence Graph's single unit of storage. Cross-referenced by trait or
    hypothesis name (not a literal graph database) so future agents have
    somewhere real to add evidence into, without building a query/
    traversal API this phase has no consumer for yet.

    This is the *only* place evidence is stored — trait and hypothesis
    evidence lists shown in the API are computed by filtering this graph,
    not duplicated into separate fields that could drift out of sync.
    """

    id: str
    text: str
    #: "url" added in V6 (URL Intelligence); "document" added in V8
    #: (Document Intelligence); "github" added in V9 (GitHub Intelligence);
    #: "search" added in V10 (Multi-Source Search Intelligence); "experiment"
    #: added in Discover Batch 2 (Career Experiments) — real evidence
    #: extracted from an investigated webpage, uploaded document, GitHub
    #: repository, cross-verified search investigation, or a completed
    #: Career Experiment, additive alongside the existing sources.
    source: Literal["conversation", "reflection", "url", "document", "github", "search", "experiment"]
    related_trait: str | None = None
    related_hypothesis: str | None = None
    related_career: str | None = None
    related_mentor: str | None = None
    related_institution: str | None = None
    relation: Literal["supports", "contradicts"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
