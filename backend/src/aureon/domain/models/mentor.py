from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.career import CareerFAQ
from aureon.domain.models.career_dna import TraitName
from aureon.domain.models.career_journey import CareerJourneyMilestone, CareerJourneyStage

__all__ = ["CareerJourneyMilestone", "CareerJourneyStage", "LinkRef", "Mentor"]

#: Sprint 4 — Data Representation audit. Live data already used exactly
#: these 5 values with zero drift; this makes that real discipline a
#: structural guarantee instead of an accidental one (see the inline
#: comment this replaces).
RoleType = Literal["professor", "researcher", "industry_professional", "founder", "creator"]


class LinkRef(BaseModel):
    """Metadata-only external reference (portfolio/social) — never
    fetched, verified, or previewed. Same honesty convention as every
    other seeded knowledge base in this codebase."""

    label: str
    url: str


class Mentor(BaseModel):
    """One entry in the Mentor Knowledge Base — data, not prompt text, same
    treatment as the Career Knowledge Base. ``name`` is an illustrative
    persona label (e.g. "Dr. Priya Nair, Materials Science Professor"),
    not a claim of a specific real, contactable individual — same honesty
    convention as Phase 2's Human Stories.

    Connect Batch 1 — this record is surfaced to users exclusively as
    "Expert" (see ``api/v1/expert_connect.py``, ``ExpertRepository``,
    ``ExpertProfileService``/``ExpertJourneyService``/
    ``ExpertKnowledgeService``). The class and table stay named
    ``Mentor``/``mentors`` since renaming them would touch Decision
    Lab's existing mentor-matching, bookings, and tests for no benefit —
    but every new file/class/function/route built for Expert Connect
    uses Expert terminology, never Mentor. "Mentor" itself is a future
    relationship/state (a student requests it, an expert accepts it),
    not a second profile entity — see ``accepts_mentorship``/
    ``max_students`` below, both forward-looking and unused by any logic
    in this batch.
    """

    id: str
    name: str
    role_type: RoleType
    field: str
    bio: str
    trait_tags: list[TraitName] = Field(default_factory=list)
    learning_style_fit: str
    #: V13 — Expert Connect; additive, richer profile fields for the
    #: existing Mentor Knowledge Base entries (no new parallel "Expert"
    #: model — an expert *is* a Mentor).
    organization: str = ""
    years_experience: int = 0
    journey_highlights: list[str] = Field(default_factory=list)
    discussion_topics: list[str] = Field(default_factory=list)

    #: Connect Batch 1 — Profile.
    profession: str = ""
    specialization: str = ""
    country: str = ""
    city: str = ""
    industries: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    current_role: str = ""
    languages: list[str] = Field(default_factory=list)
    #: Metadata-only external reference, never generated/fabricated.
    photo_url: str | None = None
    #: Forward-looking only for a future mentorship-relationship table —
    #: not read by any logic in this batch.
    accepts_mentorship: bool = False
    max_students: int = 0
    #: "Who should talk to me" — the single biggest aid to picking the
    #: right expert; only the expert themself can honestly say this.
    who_should_talk_to_me: list[str] = Field(default_factory=list)
    #: Reuse link into the Career catalog — never resolved/denormalized
    #: onto this row.
    career_ids: list[str] = Field(default_factory=list)

    #: Connect Batch 1 — Career Journey.
    career_journey: list[CareerJourneyMilestone] = Field(default_factory=list)

    #: Connect Batch 1 — Reality.
    day_in_the_life: str = ""
    weekly_routine: str = ""
    biggest_challenges: list[str] = Field(default_factory=list)
    favourite_part: str = ""
    biggest_misconceptions: list[str] = Field(default_factory=list)
    what_surprised_them: str = ""
    biggest_mistake: str = ""
    one_regret: str = ""
    salary_reality: str = ""
    work_life_balance: str = ""
    daily_skills: list[str] = Field(default_factory=list)
    daily_tools: list[str] = Field(default_factory=list)
    recommended_books: list[str] = Field(default_factory=list)
    recommended_communities: list[str] = Field(default_factory=list)
    advice_for_beginners: str = ""
    advice_for_parents: str = ""
    faqs: list[CareerFAQ] = Field(default_factory=list)

    #: Connect Batch 1 — Knowledge.
    projects: list[str] = Field(default_factory=list)
    research: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    conferences: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    volunteer_work: list[str] = Field(default_factory=list)
    portfolio_links: list[LinkRef] = Field(default_factory=list)
    social_links: list[LinkRef] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
