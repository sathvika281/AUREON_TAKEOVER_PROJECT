from datetime import datetime, timezone

from pydantic import BaseModel, Field


class GitHubSkillRecord(BaseModel):
    skill: str
    category: str
    evidence: str


class GitHubInvestigationRecord(BaseModel):
    """One GitHub Intelligence (V9) investigation, persisted so it can be
    genuinely reopened from Investigation History (V12) — never
    regenerated. Mirrors ``GitHubInvestigationResult``'s already-real
    data; stars/forks/last_activity are display metadata only, exactly as
    they were during the original investigation (never re-derived as
    evidence of engineering ability)."""

    id: str
    url: str
    owner: str
    repo: str
    name: str
    description: str
    primary_language: str | None = None
    languages: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    license: str | None = None
    stars: int = 0
    forks: int = 0
    last_activity: str | None = None
    skills: list[GitHubSkillRecord] = Field(default_factory=list)
    overall_summary: str
    project_purpose: str
    technical_complexity: str
    problem_solving: str
    code_organization: str
    technology_breadth: str
    documentation_quality: str
    learning_signals: str
    engineering_maturity: str
    research_orientation: str
    ai_ml_signals: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
