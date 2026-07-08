import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Literal

import httpx

#: Three real, keyless, trusted-source APIs — confirmed reachable without
#: any paid API key. No general web search (e.g. scraping DuckDuckGo's
#: HTML results) is included: it has no stable API/key and is a ToS/
#: fragility risk, whereas these three are genuine structured sources.
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
ARXIV_API = "http://export.arxiv.org/api/query"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

_TIMEOUT_SECONDS = 8.0
_USER_AGENT = "AureonBot/1.0 (+search-intelligence)"
_MAX_SNIPPET_CHARS = 1500
_MAX_RESULTS_PER_SOURCE = 3

SourceType = Literal["wikipedia", "arxiv", "semantic_scholar"]
SourceStatus = Literal["completed", "failed", "rate_limited", "no_results"]


@dataclass
class SourceResult:
    """One real, extracted result from a single trusted source — never a
    full page copy, always a short real snippet (abstract/intro extract)."""

    title: str
    url: str
    snippet: str
    source_type: SourceType
    metadata: dict = field(default_factory=dict)


@dataclass
class SourceSearchOutcome:
    """Every failure mode named plainly — a source that's down, rate-
    limited, or returns nothing real never gets fabricated content."""

    status: SourceStatus
    results: list[SourceResult] = field(default_factory=list)
    explanation: str | None = None


async def search_wikipedia(query: str) -> SourceSearchOutcome:
    """Real Wikipedia REST API — a search call to find matching pages,
    then one real page-extract call per top match (the genuine intro
    paragraph, not the full article)."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS, headers={"User-Agent": _USER_AGENT}) as client:
            search_resp = await client.get(
                WIKIPEDIA_API,
                params={
                    "action": "query", "list": "search", "srsearch": query,
                    "format": "json", "srlimit": _MAX_RESULTS_PER_SOURCE,
                },
            )
            search_resp.raise_for_status()
            hits = search_resp.json().get("query", {}).get("search", [])
            if not hits:
                return SourceSearchOutcome(status="no_results", explanation=f"No Wikipedia results for '{query}'.")

            results: list[SourceResult] = []
            for hit in hits[:2]:
                title = hit.get("title", "")
                if not title:
                    continue
                extract_resp = await client.get(
                    WIKIPEDIA_API,
                    params={
                        "action": "query", "prop": "extracts", "exintro": 1,
                        "explaintext": 1, "titles": title, "format": "json",
                    },
                )
                if extract_resp.status_code != 200:
                    continue
                pages = extract_resp.json().get("query", {}).get("pages", {})
                extract = next(iter(pages.values()), {}).get("extract", "")
                if not extract:
                    continue
                results.append(SourceResult(
                    title=title,
                    url=f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    snippet=extract[:_MAX_SNIPPET_CHARS],
                    source_type="wikipedia",
                ))

            if not results:
                return SourceSearchOutcome(
                    status="no_results",
                    explanation=f"Wikipedia had matches for '{query}' but none had readable content.",
                )
            return SourceSearchOutcome(status="completed", results=results)
    except httpx.TimeoutException:
        return SourceSearchOutcome(status="failed", explanation="Wikipedia request timed out.")
    except httpx.HTTPError as exc:
        return SourceSearchOutcome(status="failed", explanation=f"Could not reach Wikipedia: {exc}")


async def search_arxiv(query: str) -> SourceSearchOutcome:
    """Real arXiv API — genuine research paper titles/abstracts/links,
    parsed from the real Atom feed (stdlib XML, no new dependency)."""
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT_SECONDS, follow_redirects=True, headers={"User-Agent": _USER_AGENT}
        ) as client:
            resp = await client.get(
                ARXIV_API,
                params={"search_query": f"all:{query}", "start": 0, "max_results": _MAX_RESULTS_PER_SOURCE},
            )
            if resp.status_code == 429:
                return SourceSearchOutcome(status="rate_limited", explanation="arXiv's API rate limit was reached.")
            resp.raise_for_status()

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(resp.text)
            results: list[SourceResult] = []
            for entry in root.findall("atom:entry", ns):
                title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
                summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
                if not title or not summary:
                    continue
                link = ""
                for link_el in entry.findall("atom:link", ns):
                    if link_el.get("rel") == "alternate":
                        link = link_el.get("href", "")
                        break
                results.append(SourceResult(
                    title=title, url=link, snippet=summary[:_MAX_SNIPPET_CHARS], source_type="arxiv",
                ))

            if not results:
                return SourceSearchOutcome(status="no_results", explanation=f"No arXiv papers found for '{query}'.")
            return SourceSearchOutcome(status="completed", results=results)
    except httpx.TimeoutException:
        return SourceSearchOutcome(status="failed", explanation="arXiv request timed out.")
    except httpx.HTTPError as exc:
        return SourceSearchOutcome(status="failed", explanation=f"Could not reach arXiv: {exc}")
    except ET.ParseError as exc:
        return SourceSearchOutcome(status="failed", explanation=f"Could not parse arXiv's response: {exc}")


async def search_semantic_scholar(query: str) -> SourceSearchOutcome:
    """Real Semantic Scholar Graph API. Reachable without a key, but
    genuinely rate-limited on shared/unauthenticated traffic — that 429 is
    an honest, expected failure mode here, not a bug."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS, headers={"User-Agent": _USER_AGENT}) as client:
            resp = await client.get(
                SEMANTIC_SCHOLAR_API,
                params={"query": query, "limit": _MAX_RESULTS_PER_SOURCE, "fields": "title,abstract,url,year,authors"},
            )
            if resp.status_code == 429:
                return SourceSearchOutcome(
                    status="rate_limited",
                    explanation="Semantic Scholar's API rate limit was reached (no API key configured).",
                )
            resp.raise_for_status()

            results: list[SourceResult] = []
            for paper in resp.json().get("data", []):
                abstract = paper.get("abstract")
                if not abstract:
                    continue
                authors = [a.get("name", "") for a in (paper.get("authors") or []) if a.get("name")]
                results.append(SourceResult(
                    title=paper.get("title") or "Untitled",
                    url=paper.get("url") or "",
                    snippet=abstract[:_MAX_SNIPPET_CHARS],
                    source_type="semantic_scholar",
                    metadata={"year": paper.get("year"), "authors": authors},
                ))

            if not results:
                return SourceSearchOutcome(
                    status="no_results",
                    explanation=f"No Semantic Scholar papers with abstracts found for '{query}'.",
                )
            return SourceSearchOutcome(status="completed", results=results)
    except httpx.TimeoutException:
        return SourceSearchOutcome(status="failed", explanation="Semantic Scholar request timed out.")
    except httpx.HTTPError as exc:
        return SourceSearchOutcome(status="failed", explanation=f"Could not reach Semantic Scholar: {exc}")


@dataclass
class SourceStatusEntry:
    name: str
    category: str
    reached: bool
    note: str | None = None


@dataclass
class SourceAvailability:
    """A deterministic, display-only summary of which real sources were
    actually reached — built directly from each source's own
    ``SourceSearchOutcome.status``. Never passed into
    ``investigation_planning.py`` or ``cross_verification.py``; a
    question answered from 1-of-3 sources reasons identically to one
    answered from 3-of-3, it only *displays* differently."""

    total_sources: int
    sources_retrieved: int
    sources_unavailable: int
    sources: list[SourceStatusEntry] = field(default_factory=list)


_SOURCE_DISPLAY: dict[str, tuple[str, str]] = {
    "wikipedia": ("Wikipedia", "Encyclopedia"),
    "arxiv": ("arXiv", "Research Papers"),
    "semantic_scholar": ("Semantic Scholar", "Academic Search"),
}

_STATUS_NOTE: dict[SourceStatus, str] = {
    "rate_limited": "Rate Limited",
    "failed": "Unavailable",
    "no_results": "No Results",
}


def build_source_availability(outcomes: dict[str, SourceSearchOutcome]) -> SourceAvailability:
    entries: list[SourceStatusEntry] = []
    retrieved = 0
    for key, (name, category) in _SOURCE_DISPLAY.items():
        outcome = outcomes.get(key)
        reached = outcome is not None and outcome.status == "completed" and bool(outcome.results)
        note = None if reached else _STATUS_NOTE.get(outcome.status if outcome else "failed", "Unavailable")
        if reached:
            retrieved += 1
        entries.append(SourceStatusEntry(name=name, category=category, reached=reached, note=note))
    total = len(entries)
    return SourceAvailability(
        total_sources=total, sources_retrieved=retrieved, sources_unavailable=total - retrieved, sources=entries,
    )
