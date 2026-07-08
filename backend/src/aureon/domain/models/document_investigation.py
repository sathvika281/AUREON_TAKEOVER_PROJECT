from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DocumentInvestigationRecord(BaseModel):
    """One Document Intelligence (V8) investigation, persisted so it can
    be genuinely reopened from Investigation History (V12) — never
    regenerated. Mirrors ``DocumentInvestigationResult``'s already-real
    data."""

    id: str
    filename: str
    category: str
    owning_specialist: str
    title: str | None = None
    summary: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    structured_fields: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
