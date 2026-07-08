import base64
import json

import httpx
import pytest

from aureon.agents.specialized.discovery import github_reader
from aureon.agents.specialized.discovery.github_reader import fetch_repository, parse_repo_url

VALID_CASES = [
    ("https://github.com/torvalds/linux", "torvalds", "linux"),
    ("https://github.com/octocat/Hello-World.git", "octocat", "Hello-World"),
    ("https://www.github.com/pytorch/pytorch/", "pytorch", "pytorch"),
]

INVALID_CASES = [
    "https://github.com/torvalds",  # organization page, no repo segment
    "https://gist.github.com/someone/abc123",  # gist
    "https://github.com/facebook/react/pulls",  # pull requests
    "https://github.com/facebook/react/issues",  # issues
    "https://github.com/facebook/react/discussions",  # discussions
    "https://example.com/owner/repo",  # not github.com at all
]


@pytest.mark.parametrize("url,expected_owner,expected_repo", VALID_CASES)
def test_parse_repo_url_accepts_real_repo_shapes(url, expected_owner, expected_repo):
    result = parse_repo_url(url)

    assert result is not None
    assert result.owner == expected_owner
    assert result.repo == expected_repo


@pytest.mark.parametrize("url", INVALID_CASES)
def test_parse_repo_url_rejects_unsupported_shapes(url):
    assert parse_repo_url(url) is None


class _FakeResponse:
    def __init__(self, status_code: int, json_data=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)  # type: ignore[arg-type]


class _FakeAsyncClient:
    def __init__(self, responses: dict[str, _FakeResponse], **kwargs):
        self._responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url: str):
        for suffix, response in self._responses.items():
            if url.endswith(suffix):
                return response
        return _FakeResponse(404, {})


def _install_fake_client(monkeypatch, responses: dict[str, _FakeResponse]):
    monkeypatch.setattr(github_reader.httpx, "AsyncClient", lambda **kwargs: _FakeAsyncClient(responses, **kwargs))


async def test_fetch_repository_not_found(monkeypatch):
    _install_fake_client(monkeypatch, {"/repos/someone/doesnotexist": _FakeResponse(404, {})})

    result = await fetch_repository("someone", "doesnotexist")

    assert result.status == "not_found_or_private"
    assert "not found" in result.explanation.lower()


async def test_fetch_repository_rate_limited(monkeypatch):
    _install_fake_client(
        monkeypatch,
        {"/repos/someone/repo": _FakeResponse(403, {}, headers={"x-ratelimit-remaining": "0"})},
    )

    result = await fetch_repository("someone", "repo")

    assert result.status == "rate_limited"
    assert "rate limit" in result.explanation.lower()


async def test_fetch_repository_successful_real_shape(monkeypatch):
    repo_data = {
        "name": "myproject", "description": "A test project", "owner": {"login": "someone"},
        "language": "Python", "topics": ["ai", "agents"], "license": {"name": "MIT"},
        "stargazers_count": 42, "forks_count": 7, "pushed_at": "2026-01-01T00:00:00Z",
    }
    readme_b64 = base64.b64encode(b"# My Project\nThis does real things.").decode()
    package_json = json.dumps({"dependencies": {"react": "^18.0.0"}, "devDependencies": {}})

    _install_fake_client(monkeypatch, {
        "/repos/someone/myproject": _FakeResponse(200, repo_data),
        "/repos/someone/myproject/languages": _FakeResponse(200, {"Python": 1000, "JavaScript": 200}),
        "/repos/someone/myproject/readme": _FakeResponse(200, {"content": readme_b64}),
        "/repos/someone/myproject/contents": _FakeResponse(200, [{"name": "package.json"}, {"name": "README.md"}]),
        "/repos/someone/myproject/contents/package.json": _FakeResponse(200, {"content": base64.b64encode(package_json.encode()).decode()}),
    })

    result = await fetch_repository("someone", "myproject")

    assert result.status == "completed"
    assert result.repo_data["name"] == "myproject"
    assert result.languages == {"Python": 1000, "JavaScript": 200}
    assert "real things" in result.readme_text
    assert "package.json" in result.root_files
    assert "react" in result.dependency_names
