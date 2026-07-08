import asyncio

import httpx

from aureon.agents.specialized.career_intelligence.html_extraction import extract_readable_text
from aureon.agents.specialized.career_intelligence.search_sources import (
    SourceSearchOutcome,
    search_arxiv,
    search_semantic_scholar,
    search_wikipedia,
)
from aureon.agents.tools.base import Evidence, Tool, ToolResult, ToolStatus
from aureon.agents.tools.pdf_extraction import extract_pdf_text, pdf_result_to_tool_result

#: Career Intelligence owns these because they're about investigating
#: careers and comparing trustworthy sources — never analyzing
#: universities (that's Institution's job) or mentors (Mentor's job).

_FETCH_TIMEOUT_SECONDS = 10.0
_MIN_READABLE_CHARS = 100
_USER_AGENT = "AureonBot/1.0 (+career-intelligence-url-investigation)"


class BrowserInvestigationTool(Tool):
    name = "browser_investigation"
    description = "Browses the open web to investigate a career's real-world context."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No browser/network-fetch backend is configured yet — this tool is wired into "
            "Career Intelligence's toolset and ready for one.",
        )


class URLReaderTool(Tool):
    """Career Intelligence's real, first external capability (V6) — a
    genuine HTTP fetch + stdlib text extraction, not a stub. Every
    failure mode is handled gracefully and explained; it never fabricates
    page content it couldn't actually retrieve."""

    name = "url_reader"
    description = "Fetches a real URL and extracts its readable text content."

    async def execute(self, *, url: str, **kwargs) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=_FETCH_TIMEOUT_SECONDS, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": _USER_AGENT})
        except httpx.TimeoutException:
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation=f"Request to {url} timed out after {_FETCH_TIMEOUT_SECONDS:.0f}s.",
            )
        except httpx.ConnectError as exc:
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation=f"Could not connect to {url}: {exc}",
            )
        except httpx.HTTPError as exc:
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation=f"Request to {url} failed: {exc}",
            )

        if response.status_code >= 400:
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation=f"{url} returned HTTP {response.status_code}.",
            )

        text = extract_readable_text(response.text)
        if len(text) < _MIN_READABLE_CHARS:
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation=(
                    f"Only {len(text)} characters of readable text were extracted from {url} — "
                    "the page may be paywalled, require JavaScript, or have no meaningful text content."
                ),
            )

        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=url, source_type="url", summary=text)],
        )


class ResearchPaperReaderTool(Tool):
    """New in V8 (Document Intelligence) — Career Intelligence owns
    research papers/whitepapers/industry reports but had no
    document-shaped tool from V5; this attaches one to the specialist
    that owns the capability, mirroring how URLReaderTool became real in
    V6. Genuine PDF text extraction via pypdf, no OCR."""

    name = "research_paper_reader"
    description = "Extracts text from a research paper, whitepaper, or industry report PDF."

    async def execute(self, *, content: bytes, filename: str = "research_paper.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))


class SearchTool(Tool):
    """Kept as the honest ``NOT_CONNECTED`` stub the conversational
    ``CareerIntelligenceAgent.run()`` already calls every turn — V10's
    real search capability is deliberately a separate ``MultiSourceSearchTool``
    (below), used only by the dedicated Search Investigation pipeline, so
    the existing conversational path's behavior (and latency) stays
    exactly as it was rather than gaining new real network calls on every
    turn without being asked to."""

    name = "search"
    description = "Searches for information about a career across multiple sources."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No search API key is configured yet — this tool is wired into Career "
            "Intelligence's toolset and ready for one.",
        )


#: Deterministic confidence ceiling from a real snippet's length — same
#: "never trust the model's own confidence number" discipline as
#: career_intelligence/confidence.py and url_investigation.py, but a lower
#: floor/ceiling since these are already-curated abstracts/extracts, not
#: raw scraped HTML.
_CONFIDENCE_FLOOR_CHARS = 100
_CONFIDENCE_CEILING_CHARS = 1000


def _snippet_confidence(length: int) -> float:
    if length < _CONFIDENCE_FLOOR_CHARS:
        return 0.2
    if length >= _CONFIDENCE_CEILING_CHARS:
        return 0.85
    span = _CONFIDENCE_CEILING_CHARS - _CONFIDENCE_FLOOR_CHARS
    return round(0.2 + 0.65 * (length - _CONFIDENCE_FLOOR_CHARS) / span, 2)


class MultiSourceSearchTool(Tool):
    """Career Intelligence's real Multi-Source Search Intelligence tool
    (V10) — genuine, parallel calls to Wikipedia, arXiv, and Semantic
    Scholar, replacing the previous ``NOT_CONNECTED`` stub. Never
    fabricates a result any source didn't actually return; Semantic
    Scholar's real, unauthenticated rate-limiting is an honest, expected
    outcome here, not a bug.

    ``last_outcomes`` is set after ``execute()`` runs so the pipeline can
    build a display-only Source Availability summary
    (``search_sources.py::build_source_availability``) from the same real
    per-source results without a second round of network calls or
    stretching the ``ToolResult``/``Evidence`` contracts to carry it."""

    name = "multi_source_search"
    description = "Searches Wikipedia, arXiv, and Semantic Scholar for real, trusted career-research evidence."

    def __init__(self) -> None:
        self.last_outcomes: dict[str, SourceSearchOutcome] | None = None

    async def execute(
        self, *, wikipedia_query: str, arxiv_query: str, semantic_scholar_query: str, **kwargs
    ) -> ToolResult:
        wikipedia, arxiv, semantic_scholar = await asyncio.gather(
            search_wikipedia(wikipedia_query),
            search_arxiv(arxiv_query),
            search_semantic_scholar(semantic_scholar_query),
        )
        self.last_outcomes = {"wikipedia": wikipedia, "arxiv": arxiv, "semantic_scholar": semantic_scholar}

        evidence: list[Evidence] = []
        for outcome in (wikipedia, arxiv, semantic_scholar):
            if outcome.status != "completed":
                continue
            for result in outcome.results:
                evidence.append(Evidence(
                    source=result.url or result.title,
                    source_type=result.source_type,
                    title=result.title,
                    summary=result.snippet,
                    confidence=_snippet_confidence(len(result.snippet)),
                    metadata=result.metadata,
                ))

        if not evidence:
            explanations = [o.explanation for o in (wikipedia, arxiv, semantic_scholar) if o.explanation]
            return ToolResult(
                tool_name=self.name, status=ToolStatus.FAILED,
                explanation="No real evidence could be retrieved from any source. " + " ".join(explanations),
            )

        return ToolResult(tool_name=self.name, status=ToolStatus.COMPLETED, evidence=evidence)


class TrendInvestigationTool(Tool):
    name = "trend_investigation"
    description = "Investigates market/demand trends for a career."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No trend-data source is configured yet — this tool is wired into Career "
            "Intelligence's toolset and ready for one.",
        )
