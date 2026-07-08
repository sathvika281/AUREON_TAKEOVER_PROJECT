from datetime import datetime, timezone

from pydantic import BaseModel, Field


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
    trait_tags: list[str] = Field(default_factory=list)
    is_partner: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
