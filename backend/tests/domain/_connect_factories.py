"""Shared, non-collected (no test_ prefix) fixture builders for Connect
Batch 1 and Connect Batch 2 tests."""

from aureon.domain.models.career import CareerStory
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.mentorship import Mentorship
from aureon.domain.models.parent_connect import ParentCareerGuide
from aureon.domain.models.shared_session import SharedSession


def make_expert(**overrides) -> Mentor:
    defaults: dict = dict(
        id="expert_1", name="Test Expert", role_type="industry_professional", field="technology",
        bio="A test expert.", learning_style_fit="x",
    )
    defaults.update(overrides)
    return Mentor(**defaults)


def make_guide(**overrides) -> ParentCareerGuide:
    defaults: dict = dict(
        id="guide_1", career_id="c1", earning_reality="x", career_stability="x",
        work_life_balance="x", growth_opportunities="x", global_demand="x",
    )
    defaults.update(overrides)
    return ParentCareerGuide(**defaults)


def make_shared_session(**overrides) -> SharedSession:
    defaults: dict = dict(
        id="session_1", student_id="student_1", mentor_id="expert_1", access_token="token_1", topic="Exploring careers",
    )
    defaults.update(overrides)
    return SharedSession(**defaults)


def make_career_story(**overrides) -> CareerStory:
    defaults: dict = dict(
        id="story_1", career_id="c1", person_label="Software Engineer, 6 years experience",
        background="x", journey="x", challenges="x", turning_points="x", advice="x", lessons_learned="x",
    )
    defaults.update(overrides)
    return CareerStory(**defaults)


def make_knowledge_circle(**overrides) -> KnowledgeCircle:
    defaults: dict = dict(
        id="circle_1", name="Space", overview="x", what_this_field_is_about="x",
    )
    defaults.update(overrides)
    return KnowledgeCircle(**defaults)


def make_mentorship(**overrides) -> Mentorship:
    defaults: dict = dict(
        id="mentorship_1", student_id="student_1", expert_id="expert_1", review_token="review_token_1",
    )
    defaults.update(overrides)
    return Mentorship(**defaults)
