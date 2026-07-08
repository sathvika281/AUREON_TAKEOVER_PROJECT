from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SalaryRange(BaseModel):
    region: str
    range: str
    note: str = ""


class CareerReality(BaseModel):
    """Answers "what is this career actually like?" — structured,
    educational content authored as data, not generated per-request, since
    it describes the career in general rather than anything personal to a
    student."""

    daily_work: str
    work_environment: str
    collaboration_level: str
    creativity_level: str
    research_intensity: str
    learning_curve: str
    travel: str
    remote_possibility: str
    stress_factors: str
    typical_challenges: str
    misconceptions: str
    long_term_growth: str
    salary_ranges: list[SalaryRange] = Field(default_factory=list)
    required_education: str
    required_skills: list[str] = Field(default_factory=list)
    #: Phase 3 — one of Decision Lab's comparison dimensions. Backfilled
    #: onto all existing seeded careers alongside the Phase 3 migration.
    entrepreneurship_potential: str = ""


class FutureLens(BaseModel):
    """Today -> 2030 -> 2035 -> 2040 outlook for a career. Written in calm,
    non-fear-based language — never "AI will replace this" framing."""

    ai_impact: str
    automation_risk: str
    demand_2030: str
    demand_2035: str
    demand_2040: str
    emerging_opportunities: str
    skills_becoming_valuable: list[str] = Field(default_factory=list)
    timeline_narrative: str


class Career(BaseModel):
    """One entry in the Career Knowledge Base — data, not prompt text.
    ``trait_tags`` is a loose retrieval aid only; actual matching is done
    by the Career Intelligence Agent reasoning over evidence, not by
    tag-filtering."""

    id: str
    name: str
    category: str
    industry: str
    countries: list[str] = Field(default_factory=list)  # empty = global
    one_liner: str
    trait_tags: list[str] = Field(default_factory=list)
    reality: CareerReality
    future_lens: FutureLens
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CareerStory(BaseModel):
    """An illustrative composite persona connected to a career — labeled by
    role/experience (e.g. "Data Scientist, 6 years experience"), not a
    fabricated named real individual."""

    id: str
    career_id: str
    person_label: str
    background: str
    journey: str
    challenges: str
    turning_points: str
    advice: str
    lessons_learned: str
    trait_tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
