"""Responsibility: Expert Connect's Career Journey — an isolated read
path over ``Mentor.career_journey``. Owns: ``build_expert_journey``.
Does NOT own: Profile (``expert_profile_service.py``) or Knowledge
(``expert_knowledge_service.py``). Consumed by: ``api/v1/expert_connect.py``.
"""

from aureon.domain.models.mentor import CareerJourneyMilestone, Mentor


def build_expert_journey(expert: Mentor) -> list[CareerJourneyMilestone]:
    """Returns the expert's real, authored timeline exactly as ordered —
    never reordered or inferred from other fields."""
    return expert.career_journey
