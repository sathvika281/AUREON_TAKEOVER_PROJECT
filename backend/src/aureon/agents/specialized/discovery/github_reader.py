import base64
import re
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlparse

import httpx

GITHUB_API_BASE = "https://api.github.com"
_TIMEOUT = 10.0
_USER_AGENT = "AureonBot/1.0 (+github-intelligence)"

#: Explicitly unsupported input shapes, per the spec — never guessed at,
#: never partially processed.
_UNSUPPORTED_SUBPATHS = {"pulls", "issues", "discussions"}
_UNSUPPORTED_HOSTS = {"gist.github.com"}


@dataclass
class RepoIdentifier:
    owner: str
    repo: str


def parse_repo_url(url: str) -> RepoIdentifier | None:
    """Deterministic Repository Validation — accepts only a real
    ``https://github.com/{owner}/{repo}`` shape. Explicitly rejects
    organization pages (no repo segment), gists, and pull request/issue/
    discussion sub-paths rather than guessing what the student meant."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()

    if host in _UNSUPPORTED_HOSTS:
        return None
    if host not in ("github.com", "www.github.com"):
        return None

    segments = [s for s in parsed.path.split("/") if s]
    if len(segments) < 2:
        return None  # bare github.com or an organization page
    if len(segments) > 2 and segments[2] in _UNSUPPORTED_SUBPATHS:
        return None

    owner, repo = segments[0], segments[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return RepoIdentifier(owner=owner, repo=repo)


GitHubFetchStatus = Literal["completed", "not_found_or_private", "rate_limited", "network_error"]


@dataclass
class GitHubFetchResult:
    status: GitHubFetchStatus
    repo_data: dict | None = None
    languages: dict[str, int] = field(default_factory=dict)
    readme_text: str | None = None
    root_files: list[str] = field(default_factory=list)
    dependency_names: list[str] = field(default_factory=list)
    has_ci_workflows: bool = False
    explanation: str | None = None


def _decode_base64_file(payload: dict) -> str | None:
    content = payload.get("content")
    if not content:
        return None
    try:
        return base64.b64decode(content).decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return None


def _parse_package_json_dependencies(text: str) -> list[str]:
    import json

    try:
        data = json.loads(text)
    except ValueError:
        return []
    names: list[str] = []
    for key in ("dependencies", "devDependencies"):
        names.extend((data.get(key) or {}).keys())
    return names


def _parse_requirements_txt_dependencies(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)", line)
        if match:
            names.append(match.group(1))
    return names


async def fetch_repository(owner: str, repo: str) -> GitHubFetchResult:
    """Real GitHub REST API calls — no OCR, no scraping, no fabrication.
    Every failure mode names exactly what happened; GitHub itself returns
    404 for both nonexistent and private repositories to anonymous
    requests, so that honest ambiguity is stated plainly rather than
    guessed at."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": _USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=headers, follow_redirects=True) as client:
            repo_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")

            if repo_resp.status_code == 404:
                return GitHubFetchResult(
                    status="not_found_or_private",
                    explanation=(
                        f"'{owner}/{repo}' was not found. It may not exist, or it may be private — "
                        "GitHub's public API can't distinguish the two for anonymous requests."
                    ),
                )
            if repo_resp.status_code == 403 and repo_resp.headers.get("x-ratelimit-remaining") == "0":
                return GitHubFetchResult(
                    status="rate_limited",
                    explanation="GitHub's public API rate limit was reached (60 requests/hour, unauthenticated). Please try again later.",
                )
            repo_resp.raise_for_status()
            repo_data = repo_resp.json()

            languages_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages")
            languages = languages_resp.json() if languages_resp.status_code == 200 else {}

            readme_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme")
            readme_text = _decode_base64_file(readme_resp.json()) if readme_resp.status_code == 200 else None

            contents_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents")
            root_files: list[str] = []
            if contents_resp.status_code == 200 and isinstance(contents_resp.json(), list):
                root_files = [item["name"] for item in contents_resp.json() if isinstance(item, dict) and "name" in item]

            has_ci_workflows = False
            if ".github" in root_files:
                workflows_resp = await client.get(
                    f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows"
                )
                has_ci_workflows = workflows_resp.status_code == 200 and bool(workflows_resp.json())

            dependency_names: list[str] = []
            if "package.json" in root_files:
                pkg_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/package.json")
                if pkg_resp.status_code == 200:
                    text = _decode_base64_file(pkg_resp.json())
                    if text:
                        dependency_names.extend(_parse_package_json_dependencies(text))
            if "requirements.txt" in root_files:
                req_resp = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/requirements.txt")
                if req_resp.status_code == 200:
                    text = _decode_base64_file(req_resp.json())
                    if text:
                        dependency_names.extend(_parse_requirements_txt_dependencies(text))

            return GitHubFetchResult(
                status="completed", repo_data=repo_data, languages=languages, readme_text=readme_text,
                root_files=root_files, dependency_names=dependency_names, has_ci_workflows=has_ci_workflows,
            )
    except httpx.TimeoutException:
        return GitHubFetchResult(
            status="network_error", explanation=f"Request to GitHub for {owner}/{repo} timed out.",
        )
    except httpx.HTTPError as exc:
        return GitHubFetchResult(status="network_error", explanation=f"Could not reach GitHub: {exc}")
