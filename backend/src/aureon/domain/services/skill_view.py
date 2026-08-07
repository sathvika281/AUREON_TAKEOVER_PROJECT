"""Responsibility: presentation mapping + composition for the Skill
Knowledge Base. Owns: ``build_skill_dto``, ``build_skill_detail_view``.
Does NOT own: how a Career's own skill chips are resolved for its own
detail page (that's ``career_view.py``'s job, composing this module's
``SkillRepository`` reads rather than duplicating them). Consumed by:
``api/v1/skills.py``.
"""

from aureon.domain.models.career import Career
from aureon.domain.models.skill import Skill
from aureon.shared.schemas import CareerSummaryDTO, SkillDetailResponse, SkillDTO


def build_skill_dto(skill: Skill) -> SkillDTO:
    return SkillDTO(
        id=skill.id,
        name=skill.name,
        category=skill.category,
        description=skill.description,
        parent_skill_id=skill.parent_skill_id,
        related_skill_ids=skill.related_skill_ids,
        evidence_types_that_count=skill.evidence_types_that_count,
    )


def build_skill_detail_view(skill: Skill, careers_requiring_it: list[Career]) -> SkillDetailResponse:
    """Composes a Skill with the real careers that require it — never a
    stored/duplicated list, always resolved live from Career's own
    ``required_skill_ids`` edge (see CareerRepository.list_careers_requiring_skill)."""
    return SkillDetailResponse(
        skill=build_skill_dto(skill),
        careers_requiring_it=[
            CareerSummaryDTO(
                id=c.id, name=c.name, category=c.category, industry=c.industry,
                countries=c.countries, one_liner=c.one_liner, trait_tags=c.trait_tags,
            )
            for c in careers_requiring_it
        ],
    )
