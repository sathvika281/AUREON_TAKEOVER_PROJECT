from typing import Literal
from urllib.parse import urlparse

from aureon.shared.types import AgentName

UrlCategory = Literal[
    "github_repository",
    "linkedin_profile",
    "youtube_video",
    "medium_article",
    "university_page",
    "research_paper",
    "portfolio_website",
    "career_article",
]

#: Deterministic — every category is decided from the URL's domain/path
#: alone, never from fetched content. Career Intelligence owns URL
#: Intelligence overall; categories that genuinely belong to another
#: specialist's expertise are delegated (see url_investigation_pipeline.py).
URL_CATEGORY_OWNER: dict[UrlCategory, str] = {
    "github_repository": AgentName.DISCOVERY.value,
    "linkedin_profile": AgentName.MENTOR.value,
    "youtube_video": AgentName.CAREER_INTELLIGENCE.value,
    "medium_article": AgentName.CAREER_INTELLIGENCE.value,
    "university_page": AgentName.INSTITUTION.value,
    "research_paper": AgentName.CAREER_INTELLIGENCE.value,
    "portfolio_website": AgentName.DISCOVERY.value,
    "career_article": AgentName.CAREER_INTELLIGENCE.value,
}

_RESEARCH_PAPER_DOMAINS = ("arxiv.org", "doi.org", "scholar.google", "researchgate.net")


def classify_url(url: str) -> UrlCategory:
    """Pattern-based, deterministic — no LLM call, no content fetch.
    Order matters: the most specific real signals (a well-known domain)
    are checked before the generic fallback."""
    parsed = urlparse(url.lower())
    domain = parsed.netloc
    full = url.lower()

    if "github.com" in domain:
        return "github_repository"
    if "linkedin.com" in domain:
        return "linkedin_profile"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube_video"
    if "medium.com" in domain:
        return "medium_article"
    if domain.endswith(".edu") or "university" in full or "college" in full:
        return "university_page"
    if any(d in domain for d in _RESEARCH_PAPER_DOMAINS):
        return "research_paper"
    if "portfolio" in full:
        return "portfolio_website"
    return "career_article"
