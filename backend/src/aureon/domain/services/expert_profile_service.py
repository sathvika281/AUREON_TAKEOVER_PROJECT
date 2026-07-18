"""Responsibility: Expert Connect's Profile composition — identity
fields plus the expert's real linked Career catalog entries. Owns:
``build_expert_profile``. Does NOT own: Career Journey
(``expert_journey_service.py``) or Knowledge (``expert_knowledge_service.py``).
Consumed by: ``api/v1/expert_connect.py``.
"""

from dataclasses import dataclass, field

from aureon.domain.models.career import Career
from aureon.domain.models.mentor import Mentor
from aureon.domain.services.career_view import build_career_summary_dto
from aureon.shared.schemas import CareerSummaryDTO


@dataclass(frozen=True)
class ExpertProfile:
    id: str
    name: str
    role_type: str
    profession: str
    specialization: str
    field: str
    bio: str
    country: str
    city: str
    industries: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    organization: str = ""
    current_role: str = ""
    years_experience: int = 0
    languages: list[str] = field(default_factory=list)
    photo_url: str | None = None
    who_should_talk_to_me: list[str] = field(default_factory=list)
    trait_tags: list[str] = field(default_factory=list)
    learning_style_fit: str = ""
    linked_careers: list[CareerSummaryDTO] = field(default_factory=list)


def build_expert_profile(expert: Mentor, *, careers: list[Career]) -> ExpertProfile:
    """Resolves ``expert.career_ids`` against the real Career catalog —
    never denormalizes career content onto the expert's own row."""
    careers_by_id = {c.id: c for c in careers}
    linked_careers = [
        build_career_summary_dto(careers_by_id[cid])
        for cid in expert.career_ids
        if cid in careers_by_id
    ]
    return ExpertProfile(
        id=expert.id,
        name=expert.name,
        role_type=expert.role_type,
        profession=expert.profession,
        specialization=expert.specialization,
        field=expert.field,
        bio=expert.bio,
        country=expert.country,
        city=expert.city,
        industries=expert.industries,
        education=expert.education,
        organization=expert.organization,
        current_role=expert.current_role,
        years_experience=expert.years_experience,
        languages=expert.languages,
        photo_url=expert.photo_url,
        who_should_talk_to_me=expert.who_should_talk_to_me,
        trait_tags=expert.trait_tags,
        learning_style_fit=expert.learning_style_fit,
        linked_careers=linked_careers,
    )
