from dataclasses import dataclass, field

from aureon.agents.specialized.discovery.github_reader import GitHubFetchResult

#: Known build/package-manager files this phase recognizes by filename —
#: their mere presence is a real, honest signal even for the ones whose
#: ecosystem-specific format isn't deep-parsed (only package.json and
#: requirements.txt are parsed for actual dependency names).
BUILD_FILES = [
    "package.json", "requirements.txt", "pyproject.toml", "Pipfile",
    "Dockerfile", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
]

_TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs"}


@dataclass
class ReasoningFacts:
    """Everything any LLM call, Career DNA update, or Skill Evidence
    extraction is allowed to see — structural/technical signals only.
    Deliberately excludes stars/forks/last_activity (see DisplayMetadata)
    so popularity can never influence an engineering conclusion."""

    name: str
    description: str
    owner: str
    primary_language: str | None
    languages: list[str]
    readme_present: bool
    readme_length: int
    topics: list[str]
    license: str | None
    root_files: list[str]
    build_files_found: list[str]
    has_ci: bool
    has_tests: bool
    dependencies: list[str]


@dataclass
class DisplayMetadata:
    """Real numbers, honestly shown to the student — but never passed to
    any reasoning step or used as evidence of engineering ability."""

    stars: int
    forks: int
    last_activity: str | None


@dataclass
class RepoFacts:
    reasoning: ReasoningFacts
    display: DisplayMetadata


def build_repo_facts(fetch_result: GitHubFetchResult) -> RepoFacts:
    data = fetch_result.repo_data or {}
    root_files = fetch_result.root_files

    reasoning = ReasoningFacts(
        name=data.get("name", ""),
        description=data.get("description") or "",
        owner=(data.get("owner") or {}).get("login", ""),
        primary_language=data.get("language"),
        languages=sorted(fetch_result.languages, key=lambda lang: fetch_result.languages[lang], reverse=True),
        readme_present=fetch_result.readme_text is not None,
        readme_length=len(fetch_result.readme_text or ""),
        topics=data.get("topics") or [],
        license=(data.get("license") or {}).get("name"),
        root_files=root_files,
        build_files_found=[f for f in BUILD_FILES if f in root_files],
        has_ci=fetch_result.has_ci_workflows,
        has_tests=any(name.lower() in _TEST_DIR_NAMES for name in root_files),
        dependencies=fetch_result.dependency_names,
    )
    display = DisplayMetadata(
        stars=data.get("stargazers_count", 0),
        forks=data.get("forks_count", 0),
        last_activity=data.get("pushed_at"),
    )
    return RepoFacts(reasoning=reasoning, display=display)


#: Deterministic technology -> skill-category map. Matched against real
#: detected languages, topics, and parsed dependency names only — never
#: an LLM guess.
SKILL_KEYWORDS: dict[str, str] = {
    "react": "Frontend Engineering",
    "vue": "Frontend Engineering",
    "angular": "Frontend Engineering",
    "next.js": "Frontend Engineering",
    "nextjs": "Frontend Engineering",
    "svelte": "Frontend Engineering",
    "fastapi": "Backend Engineering",
    "django": "Backend Engineering",
    "flask": "Backend Engineering",
    "express": "Backend Engineering",
    "spring": "Backend Engineering",
    "rails": "Backend Engineering",
    "pytorch": "Machine Learning",
    "scikit-learn": "Machine Learning",
    "sklearn": "Machine Learning",
    "xgboost": "Machine Learning",
    "tensorflow": "Deep Learning",
    "keras": "Deep Learning",
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "terraform": "DevOps",
    "ansible": "DevOps",
    "langgraph": "AI Agent Engineering",
    "langchain": "AI Agent Engineering",
    "autogen": "AI Agent Engineering",
    "python": "Backend Engineering",
    "typescript": "Frontend Engineering",
    "javascript": "Frontend Engineering",
    "go": "Backend Engineering",
    "rust": "Systems Engineering",
    "c++": "Systems Engineering",
    "solidity": "Blockchain Engineering",
}


@dataclass
class SkillFinding:
    skill: str
    category: str
    evidence: str


def extract_skills(facts: ReasoningFacts) -> list[SkillFinding]:
    """Deterministic — every skill found names the exact real fact
    (a language, a topic, or a parsed dependency) that produced it,
    satisfying 'every extracted skill must reference repository
    evidence' literally. No LLM call happens here."""
    findings: list[SkillFinding] = []
    seen: set[str] = set()

    def _record(raw_term: str, source_label: str) -> None:
        key = raw_term.strip().lower()
        category = SKILL_KEYWORDS.get(key)
        if category is None or key in seen:
            return
        seen.add(key)
        findings.append(SkillFinding(skill=raw_term, category=category, evidence=source_label))

    for language in facts.languages:
        _record(language, f"'{language}' detected as a language used in this repository")
    for topic in facts.topics:
        _record(topic, f"'{topic}' listed as a repository topic")
    for dependency in facts.dependencies:
        _record(dependency, f"'{dependency}' found among the repository's declared dependencies")

    return findings
