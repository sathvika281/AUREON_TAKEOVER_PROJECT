import io
import re
from dataclasses import dataclass
from typing import Literal

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from aureon.agents.tools.base import Evidence, ToolResult, ToolStatus

#: Below this many real characters, a PDF is treated as having no usable
#: text layer (a scan, an image-only page, or genuinely empty) — the same
#: "not enough real signal" floor as career_intelligence's
#: _MIN_READABLE_CHARS for URLs.
MIN_READABLE_CHARS = 100

PdfExtractionStatus = Literal["completed", "encrypted", "no_readable_text", "invalid_document"]


@dataclass
class PdfExtractionResult:
    status: PdfExtractionStatus
    text: str = ""
    first_page_text: str = ""
    page_count: int = 0


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_pdf_text(content: bytes) -> PdfExtractionResult:
    """Real PDF text extraction (pypdf) — no OCR, no password guessing.
    This is the one place pypdf is imported; every document tool calls
    through this function rather than parsing PDFs itself.

    Never fabricates text: an encrypted, corrupt, or scan-only PDF
    returns an honest status naming exactly what happened, with no text
    attached.
    """
    try:
        reader = PdfReader(io.BytesIO(content))
    except PdfReadError:
        return PdfExtractionResult(status="invalid_document")
    except Exception:  # noqa: BLE001 — any other parse failure is still "not a valid PDF" to us
        return PdfExtractionResult(status="invalid_document")

    if reader.is_encrypted:
        # Never attempts a password — an encrypted document without one
        # supplied is simply unreadable, not a puzzle to guess at. Page
        # count isn't accessible without decrypting, so it's left at 0
        # rather than triggering pypdf's own decryption attempt.
        return PdfExtractionResult(status="encrypted")

    try:
        pages_text = [_clean(page.extract_text() or "") for page in reader.pages]
    except Exception:  # noqa: BLE001 — a corrupt page stream still means "invalid", not a crash
        return PdfExtractionResult(status="invalid_document")

    full_text = " ".join(t for t in pages_text if t)
    first_page_text = pages_text[0] if pages_text else ""

    if len(full_text) < MIN_READABLE_CHARS:
        return PdfExtractionResult(
            status="no_readable_text", page_count=len(reader.pages), first_page_text=first_page_text,
        )

    return PdfExtractionResult(
        status="completed", text=full_text, first_page_text=first_page_text, page_count=len(reader.pages),
    )


#: Standardized, self-explaining failure prefixes (per V8's naming) —
#: every document tool's ToolResult.explanation starts with one of these
#: when extraction doesn't complete, so the reason is never vague.
_STATUS_EXPLANATION: dict[PdfExtractionStatus, str] = {
    "encrypted": "ENCRYPTED: this document is password-protected and cannot be read without one.",
    "no_readable_text": (
        "NO_READABLE_TEXT: no readable text could be extracted — it may be a scanned image "
        "with no embedded text layer."
    ),
    "invalid_document": "INVALID_DOCUMENT: this file could not be parsed as a valid PDF.",
}


def pdf_result_to_tool_result(tool_name: str, filename: str, result: PdfExtractionResult) -> ToolResult:
    """Shared mapping from a PdfExtractionResult to the Tool
    architecture's existing ToolResult — reused by every document tool
    (Discovery/Institution/Mentor/Career Intelligence) instead of each
    duplicating this logic. ToolResult.status stays exactly the existing
    COMPLETED/FAILED/NOT_CONNECTED (not redesigned); the standardized
    encrypted/no_readable_text/invalid_document detail lives in
    ``explanation``."""
    if result.status == "completed":
        return ToolResult(
            tool_name=tool_name,
            status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=filename, source_type="document", summary=result.text)],
        )
    return ToolResult(
        tool_name=tool_name,
        status=ToolStatus.FAILED,
        explanation=_STATUS_EXPLANATION[result.status],
    )
