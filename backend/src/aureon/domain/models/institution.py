from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.domain.models.career_dna import TraitName


class ResearchLab(BaseModel):
    id: str
    institution_id: str
    name: str
    focus_area: str
    description: str


class StudentOrganization(BaseModel):
    id: str
    institution_id: str
    name: str
    focus_area: str
    description: str


class AcademicProgram(BaseModel):
    id: str
    institution_id: str
    name: str
    degree_type: str
    field: str
    description: str


class InnovationCenter(BaseModel):
    id: str
    institution_id: str
    name: str
    focus_area: str
    description: str


class FacultyHighlight(BaseModel):
    id: str
    institution_id: str
    name: str
    title: str
    expertise_area: str
    bio: str


class StudentAmbassador(BaseModel):
    """An illustrative persona, not a claim of a specific real,
    contactable individual — same honesty convention as ``Mentor.name``
    and ``CareerStory.person_label``."""

    id: str
    institution_id: str
    student_label: str  # e.g. "Third-year CSE student, AI/ML track"
    program: str
    message: str


class StudentProject(BaseModel):
    """The Student Project Showcase (V13) — same illustrative-persona
    discipline as StudentAmbassador; never a specific claimed-real
    student."""

    id: str
    institution_id: str
    student_label: str
    project_title: str
    description: str
    skills_used: list[str] = Field(default_factory=list)


class InternshipOpportunity(BaseModel):
    id: str
    institution_id: str
    title: str
    field: str
    description: str


class InstitutionReview(BaseModel):
    """An anonymized, role-labeled composite sentiment summary — never a
    specific named real individual. Same honesty discipline as
    ``StudentAmbassador``/``CareerStory.person_label``."""

    role_label: str  # e.g. "Graduate Student, Computer Science"
    quote: str
    sentiment: str = "positive"  # "positive" | "mixed"


class Institution(BaseModel):
    """One entry in the Institution Knowledge Base — data, not prompt
    text. Degree types/locations/industries stay plain fields rather than
    separate lookup tables, same "don't over-normalize enums" reasoning
    Phase 2 applied to Career's category/industry/countries.

    ``is_partner`` (V13) additively flags institutions Aureon actively
    collaborates with (seed: NIAT) — presented to students as "College
    Collaboration"/"Partner Colleges," never as a ranking. Every other
    institution in the Knowledge Base is unaffected and still participates
    in College Match exactly as before.
    """

    id: str
    name: str
    country: str
    city: str
    research_culture: str
    innovation_ecosystem: str
    industry_collaboration: str
    placements: str
    learning_environment: str
    trait_tags: list[TraitName] = Field(default_factory=list)
    is_partner: bool = False
    #: Explore Batch 1 — additive, nullable-defaulted. campus_life_and_culture
    #: intentionally consolidates social-life and ethos into one field
    #: rather than two near-duplicate prose fields. fees_summary/
    #: scholarships_summary are honest, hedged descriptive text — not live
    #: numbers, not a structured link into Opportunity Hub's own
    #: scholarship-category opportunities (see the approved plan's
    #: Decisions Log for why that cross-reference isn't built yet).
    campus_life_and_culture: str = ""
    fees_summary: str = ""
    scholarships_summary: str = ""

    #: Explore Polish Batch — additive, defaulted. Embedded jsonb list
    #: fields directly on Institution (unlike research_labs/etc. above,
    #: which are separate normalized tables) — these don't need their own
    #: structured sub-fields the way a research lab needs a focus_area, so
    #: a plain list (or the small InstitutionReview sub-model) is honest
    #: and sufficient, matching CareerWorld's own plain-list convention.
    hostels: list[str] = Field(default_factory=list)
    exchange_programs: list[str] = Field(default_factory=list)
    campus_facilities: list[str] = Field(default_factory=list)
    student_reviews: list[InstitutionReview] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
