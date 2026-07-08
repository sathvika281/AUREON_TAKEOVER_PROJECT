import pytest

from aureon.agents.specialized.career_intelligence.url_classifier import (
    URL_CATEGORY_OWNER,
    classify_url,
)
from aureon.shared.types import AgentName

CASES = [
    ("https://github.com/someone/project", "github_repository", AgentName.DISCOVERY.value),
    ("https://www.linkedin.com/in/someone", "linkedin_profile", AgentName.MENTOR.value),
    ("https://www.youtube.com/watch?v=abc", "youtube_video", AgentName.CAREER_INTELLIGENCE.value),
    ("https://youtu.be/abc", "youtube_video", AgentName.CAREER_INTELLIGENCE.value),
    ("https://medium.com/@someone/article", "medium_article", AgentName.CAREER_INTELLIGENCE.value),
    ("https://www.mit.edu/admissions", "university_page", AgentName.INSTITUTION.value),
    ("https://example.com/university-of-life", "university_page", AgentName.INSTITUTION.value),
    ("https://arxiv.org/abs/1234.5678", "research_paper", AgentName.CAREER_INTELLIGENCE.value),
    ("https://someone.dev/portfolio", "portfolio_website", AgentName.DISCOVERY.value),
    ("https://random-blog.example.com/ai-careers", "career_article", AgentName.CAREER_INTELLIGENCE.value),
]


@pytest.mark.parametrize("url,expected_category,expected_owner", CASES)
def test_classify_url_is_deterministic(url, expected_category, expected_owner):
    category = classify_url(url)

    assert category == expected_category
    assert URL_CATEGORY_OWNER[category] == expected_owner


def test_same_url_always_classifies_identically():
    url = "https://github.com/someone/project"
    assert classify_url(url) == classify_url(url)
