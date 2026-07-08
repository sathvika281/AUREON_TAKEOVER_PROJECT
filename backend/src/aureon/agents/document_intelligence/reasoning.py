from datetime import datetime, timezone

from aureon.agents.document_intelligence.classifier import DocumentCategory
from aureon.agents.document_intelligence.prompts import build_document_investigation_messages
from aureon.agents.document_intelligence.schemas import (
    DOCUMENT_INVESTIGATION_TOOL,
    DocumentInvestigationTurnOutput,
)
from aureon.agents.tools.base import Evidence
from aureon.services.llm.base import LLMClient

#: Same deterministic-ceiling discipline as url_investigation.py's
#: _extraction_confidence — never trust the LLM's own confidence claim,
#: only how much real extracted text actually backed it.
_CONFIDENCE_FLOOR_CHARS = 200
_CONFIDENCE_CEILING_CHARS = 3000


def _extraction_confidence(raw_text_length: int) -> float:
    if raw_text_length < _CONFIDENCE_FLOOR_CHARS:
        return 0.1
    if raw_text_length >= _CONFIDENCE_CEILING_CHARS:
        return 0.9
    span = _CONFIDENCE_CEILING_CHARS - _CONFIDENCE_FLOOR_CHARS
    return round(0.1 + 0.8 * (raw_text_length - _CONFIDENCE_FLOOR_CHARS) / span, 2)


async def analyze_document_content(
    *, category: DocumentCategory, filename: str, raw_text: str, llm: LLMClient
) -> DocumentInvestigationTurnOutput:
    """The single reasoning entry point for Document Intelligence — raw
    extracted text (already real, from pdf_extraction.py) is working data
    only; this call turns it into the structured findings that become
    Evidence. Never called with the raw text kept afterward — the caller
    discards it once this returns."""
    messages = build_document_investigation_messages(category=category, filename=filename, raw_text=raw_text)
    response = await llm.complete(messages, tools=[DOCUMENT_INVESTIGATION_TOOL], tool_choice="required")
    if not response.tool_calls:
        return DocumentInvestigationTurnOutput(
            title=filename,
            summary=response.content or "Could not extract structured findings from this document.",
            insufficient_content=True,
            insufficient_content_reason="Investigation could not be completed this time.",
        )
    return DocumentInvestigationTurnOutput.model_validate(response.tool_calls[0].arguments)


def finalize_document_evidence(
    *, category: DocumentCategory, filename: str, raw_text_length: int, output: DocumentInvestigationTurnOutput
) -> Evidence:
    """Merges the deterministic confidence ceiling with the LLM's
    structured narrative into one Evidence record. Evidence.summary holds
    only this concise, reasoned summary — never the raw multi-page
    extracted text, which is discarded once this is built."""
    return Evidence(
        source=filename,
        source_type=f"document:{category}",
        title=output.title,
        summary=output.summary,
        confidence=_extraction_confidence(raw_text_length),
        metadata={
            "category": category,
            "key_findings": output.key_findings,
            "structured_fields": output.structured_fields,
            "insufficient_content": output.insufficient_content,
            "insufficient_content_reason": output.insufficient_content_reason,
        },
        timestamp=datetime.now(timezone.utc),
    )
