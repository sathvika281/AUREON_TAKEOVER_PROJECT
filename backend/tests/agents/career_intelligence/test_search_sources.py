import httpx
import pytest

from aureon.agents.specialized.career_intelligence import search_sources
from aureon.agents.specialized.career_intelligence.search_sources import (
    build_source_availability,
    search_arxiv,
    search_semantic_scholar,
    search_wikipedia,
)

ARXIV_ATOM = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Deep Learning for Computer Vision</title>
    <summary>A real abstract about computer vision research.</summary>
    <link href="https://arxiv.org/abs/1234.5678" rel="alternate" type="text/html"/>
  </entry>
</feed>
"""

ARXIV_EMPTY_ATOM = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>
"""


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None, text: str = "", headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)  # type: ignore[arg-type]


class _FakeAsyncClient:
    def __init__(self, responder, **kwargs):
        self._responder = responder

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url: str, params: dict | None = None):
        return self._responder(url, params or {})


def _install(monkeypatch, responder):
    monkeypatch.setattr(search_sources.httpx, "AsyncClient", lambda **kwargs: _FakeAsyncClient(responder, **kwargs))


# --- Wikipedia -------------------------------------------------------


async def test_search_wikipedia_success(monkeypatch):
    def responder(url, params):
        if params.get("list") == "search":
            return _FakeResponse(200, {"query": {"search": [{"title": "Cybersecurity"}]}})
        if params.get("prop") == "extracts":
            return _FakeResponse(200, {"query": {"pages": {"1": {"extract": "Cybersecurity is a real field."}}}})
        return _FakeResponse(404, {})

    _install(monkeypatch, responder)

    outcome = await search_wikipedia("cybersecurity")

    assert outcome.status == "completed"
    assert outcome.results[0].source_type == "wikipedia"
    assert "real field" in outcome.results[0].snippet


async def test_search_wikipedia_no_results(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(200, {"query": {"search": []}}))

    outcome = await search_wikipedia("asdkjaslkdjaslkd")

    assert outcome.status == "no_results"
    assert outcome.explanation


async def test_search_wikipedia_network_error(monkeypatch):
    def raise_timeout(**kwargs):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(search_sources.httpx, "AsyncClient", raise_timeout)

    outcome = await search_wikipedia("cybersecurity")

    assert outcome.status == "failed"


# --- arXiv -------------------------------------------------------------


async def test_search_arxiv_success(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(200, text=ARXIV_ATOM))

    outcome = await search_arxiv("computer vision")

    assert outcome.status == "completed"
    assert outcome.results[0].source_type == "arxiv"
    assert "computer vision" in outcome.results[0].snippet.lower()


async def test_search_arxiv_no_results(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(200, text=ARXIV_EMPTY_ATOM))

    outcome = await search_arxiv("zzzznonexistent")

    assert outcome.status == "no_results"


async def test_search_arxiv_rate_limited(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(429, text=""))

    outcome = await search_arxiv("computer vision")

    assert outcome.status == "rate_limited"


# --- Semantic Scholar ----------------------------------------------------


async def test_search_semantic_scholar_success(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(200, {
        "data": [{"title": "AI Research Trends", "abstract": "A real abstract.", "url": "https://x", "year": 2025, "authors": [{"name": "A. Researcher"}]}]
    }))

    outcome = await search_semantic_scholar("ai research trends")

    assert outcome.status == "completed"
    assert outcome.results[0].source_type == "semantic_scholar"
    assert outcome.results[0].metadata["year"] == 2025


async def test_search_semantic_scholar_rate_limited(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(429, {}))

    outcome = await search_semantic_scholar("ai research trends")

    assert outcome.status == "rate_limited"
    assert "rate limit" in outcome.explanation.lower()


async def test_search_semantic_scholar_no_results_when_missing_abstracts(monkeypatch):
    _install(monkeypatch, lambda url, params: _FakeResponse(200, {"data": [{"title": "No Abstract Paper"}]}))

    outcome = await search_semantic_scholar("ai research trends")

    assert outcome.status == "no_results"


# --- build_source_availability -------------------------------------------


def test_build_source_availability_mixed_outcomes():
    outcomes = {
        "wikipedia": search_sources.SourceSearchOutcome(status="completed", results=[
            search_sources.SourceResult(title="x", url="u", snippet="s", source_type="wikipedia"),
        ]),
        "arxiv": search_sources.SourceSearchOutcome(status="completed", results=[
            search_sources.SourceResult(title="y", url="u2", snippet="s2", source_type="arxiv"),
        ]),
        "semantic_scholar": search_sources.SourceSearchOutcome(status="rate_limited", explanation="rate limited"),
    }

    availability = build_source_availability(outcomes)

    assert availability.total_sources == 3
    assert availability.sources_retrieved == 2
    assert availability.sources_unavailable == 1
    semantic_entry = next(s for s in availability.sources if s.name == "Semantic Scholar")
    assert semantic_entry.reached is False
    assert semantic_entry.note == "Rate Limited"
    wiki_entry = next(s for s in availability.sources if s.name == "Wikipedia")
    assert wiki_entry.reached is True
    assert wiki_entry.note is None
