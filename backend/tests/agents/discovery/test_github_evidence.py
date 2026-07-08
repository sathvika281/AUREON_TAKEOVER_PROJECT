import dataclasses

from aureon.agents.specialized.discovery.github_evidence import build_repo_facts, extract_skills
from aureon.agents.specialized.discovery.github_reader import GitHubFetchResult


def _fetch_result(**overrides) -> GitHubFetchResult:
    defaults = dict(
        status="completed",
        repo_data={
            "name": "myproject", "description": "desc", "owner": {"login": "someone"},
            "language": "Python", "topics": ["ai"], "license": {"name": "MIT"},
            "stargazers_count": 999, "forks_count": 111, "pushed_at": "2026-01-01T00:00:00Z",
        },
        languages={"Python": 1000, "TypeScript": 200},
        readme_text="x" * 500,
        root_files=["package.json", "requirements.txt", "tests", ".github"],
        dependency_names=["react", "pytorch"],
        has_ci_workflows=True,
    )
    defaults.update(overrides)
    return GitHubFetchResult(**defaults)


def test_reasoning_facts_never_contain_popularity_metrics():
    facts = build_repo_facts(_fetch_result())

    reasoning_field_names = {f.name for f in dataclasses.fields(facts.reasoning)}
    assert "stars" not in reasoning_field_names
    assert "forks" not in reasoning_field_names
    assert "last_activity" not in reasoning_field_names
    # The popularity numbers still exist, but only in display metadata.
    assert facts.display.stars == 999
    assert facts.display.forks == 111


def test_build_repo_facts_reads_real_signals():
    facts = build_repo_facts(_fetch_result())

    assert facts.reasoning.readme_present is True
    assert facts.reasoning.readme_length == 500
    assert "package.json" in facts.reasoning.build_files_found
    assert "requirements.txt" in facts.reasoning.build_files_found
    assert facts.reasoning.has_tests is True
    assert facts.reasoning.has_ci is True
    assert facts.reasoning.dependencies == ["react", "pytorch"]


def test_extract_skills_only_fires_from_real_detected_signals():
    facts = build_repo_facts(_fetch_result())

    skills = extract_skills(facts.reasoning)
    skill_names = {s.skill for s in skills}

    assert "react" in skill_names
    assert "pytorch" in skill_names
    assert "Python" in skill_names  # a detected language
    # Every finding must cite the real evidence that produced it.
    for finding in skills:
        assert finding.evidence  # never empty


def test_extract_skills_ignores_unknown_technologies():
    facts = build_repo_facts(_fetch_result(languages={"Brainfuck": 1}, dependency_names=[], root_files=[]))

    skills = extract_skills(facts.reasoning)

    assert all(s.skill != "Brainfuck" for s in skills)


def test_extract_skills_never_duplicates_a_skill():
    # "python" appears both as a language and could appear as a dependency
    # name in some ecosystems — must not be recorded twice.
    facts = build_repo_facts(_fetch_result(languages={"Python": 1}, dependency_names=["Python"]))

    skills = extract_skills(facts.reasoning)
    python_findings = [s for s in skills if s.skill.lower() == "python"]

    assert len(python_findings) == 1
