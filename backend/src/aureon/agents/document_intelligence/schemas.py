from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class DocumentInvestigationTurnOutput(BaseModel):
    """Structured contract for one document investigation. The raw
    extracted text is already real (pypdf, deterministic) — this call
    only organizes/summarizes what's actually present in it, never
    invents anything beyond it. Raw text itself is never stored as
    Evidence; only this structured output becomes Evidence."""

    title: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    structured_fields: dict[str, str] = Field(default_factory=dict)
    insufficient_content: bool = False
    insufficient_content_reason: str | None = None


DOCUMENT_INVESTIGATION_TOOL = LLMTool(
    name="record_document_investigation",
    description="Record structured findings extracted from a real document's content — never invent beyond what's given.",
    parameters=DocumentInvestigationTurnOutput.model_json_schema(),
)
