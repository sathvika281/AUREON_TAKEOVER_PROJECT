from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.career_journey import CareerJourneyMilestone


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


class CareerBranch(BaseModel):
    """A specialization path within a career (e.g. AI Research -> NLP
    Research, Robotics Research) — static authored content, not a
    separate ``Career`` row of its own."""

    name: str
    description: str


class CareerFAQ(BaseModel):
    """One real, specific question a student would plausibly ask about
    this career — not a generic filler Q&A."""

    question: str
    answer: str


class Career(BaseModel):
    """One entry in the Career Knowledge Base — data, not prompt text.
    ``trait_tags`` is a loose retrieval aid only; actual matching is done
    by the Career Intelligence Agent reasoning over evidence, not by
    tag-filtering.

    Explore Batch 1 additions — all nullable/defaulted so existing seeded
    rows keep working, backfilled honestly on a meaningful subset (same
    partial-coverage precedent as ``CareerStory``, never fabricated for
    every row at once): ``description`` (the fuller "what this career
    actually is," distinct from the short ``one_liner`` tagline),
    ``why_people_love_it``, ``branches`` (real specialization paths),
    ``curiosity_hook`` (Exposure Universe's honest framing line — e.g.
    "Did you know AI ethicists exist?" — optional, never LLM-invented)."""

    id: str
    name: str
    category: str
    industry: str
    countries: list[str] = Field(default_factory=list)  # empty = global
    one_liner: str
    trait_tags: list[str] = Field(default_factory=list)
    reality: CareerReality
    future_lens: FutureLens
    description: str = ""
    why_people_love_it: str = ""
    branches: list[CareerBranch] = Field(default_factory=list)
    curiosity_hook: str | None = None

    #: Explore Polish Batch — all additive, all defaulted so existing rows
    #: and tests keep working. Backfilled onto every career via
    #: scripts/enrich_careers.py, not this original creation script.
    #: "Specializations" reuses `branches` above, "Required Skills" reuses
    #: `reality.required_skills`, "Future Outlook" reuses `future_lens` —
    #: deliberately not duplicated here.
    day_in_the_life: str = ""
    weekly_routine: str = ""
    daily_tools: list[str] = Field(default_factory=list)
    career_progression: list[str] = Field(default_factory=list)
    related_industries: list[str] = Field(default_factory=list)
    research_areas: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    universities: list[str] = Field(default_factory=list)
    scholarships: list[str] = Field(default_factory=list)
    competitions: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    open_source_projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    videos: list[str] = Field(default_factory=list)
    common_misconceptions: list[str] = Field(default_factory=list)
    faqs: list[CareerFAQ] = Field(default_factory=list)
    #: Cross-field realistic transitions (e.g. Software Engineer -> Product
    #: Manager) — plain names, deliberately separate from
    #: `career_view.py`'s same-field/tag-overlap `related_careers`
    #: computation. Not resolved against the catalog since most adjacent
    #: careers aren't seeded `Career` rows of their own.
    adjacent_careers: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CareerStory(BaseModel):
    """An illustrative composite persona connected to a career — labeled by
    role/experience (e.g. "Data Scientist, 6 years experience"), not a
    fabricated named real individual.

    Connect Batch 2 — "Journey Stories" is this same model, read through
    a new, richer `JourneyStoryRepository`/`JourneyStoryService` layer
    (mirroring how Connect Batch 1's `ExpertRepository` reads `Mentor`
    without a parallel model). All new fields below are additive and
    defaulted so every existing story keeps working unchanged.
    """

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

    #: Connect Batch 2 — structured timeline, reusing the exact sub-model
    #: an expert's own `career_journey` already uses (see
    #: `career_journey.py`) rather than a second, near-identical shape.
    timeline: list[CareerJourneyMilestone] = Field(default_factory=list)
    #: Explicit, filterable "avoid survivorship bias" dimensions — real
    #: structural properties, not just a writing-style request.
    career_switch: bool = False
    gap_year: bool = False
    uncertainty_period: str = ""
    current_outcome: str = ""
    #: Lets a story be found even when it spans a switch between fields —
    #: distinct from `career_id`, which only ever points at one career.
    industry: str = ""
    #: Reuse links — never denormalized content, resolved at read time.
    linked_expert_id: str | None = None
    linked_life_mission_id: str | None = None
    #: Honesty discipline per the user's own explicit guidance: a story
    #: only ever claims `"publicly_documented"` when `source_reference`
    #: names a real, checkable public source — never an invented
    #: biography presented as real.
    #:
    #: Expert Connect / Journey Stories purpose split — "composite" and
    #: "publicly_documented" stay exactly as they were (professional/
    #: workplace narratives; Career Explorer's "Human Stories" section is
    #: their one real consumer, unchanged by this split — `Mentor.career_journey`
    #: is the sole source of truth for a specific real expert's journey,
    #: never this model). "composite_student_discovery" is this batch's new
    #: purpose: illustrative student self-discovery narratives, the
    #: standalone Journey Stories screen's only populated content type.
    #: "student_discovery" is reserved, unpopulated, for a future real,
    #: consented, moderated student submission ("Share My Journey") — not
    #: built in this batch.
    story_type: Literal[
        "composite", "publicly_documented", "composite_student_discovery", "student_discovery"
    ] = "composite"
    source_reference: str = ""
    #: Real, honest per-story tagging backing the standalone Journey
    #: Stories screen's discovery filters (e.g. "found_my_passion",
    #: "parent_expectations") — only ever populated on
    #: composite_student_discovery/student_discovery rows; existing
    #: professional stories default to empty, matching "do not create
    #: empty filters" (nothing queries this for the old rows).
    discovery_themes: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
