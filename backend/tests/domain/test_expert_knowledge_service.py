from aureon.domain.services.expert_knowledge_service import build_expert_knowledge
from tests.domain._explore_factories import make_career

from ._connect_factories import make_expert


def test_build_expert_knowledge_dedupes_suggested_books_against_experts_own_list():
    expert = make_expert(recommended_books=["Book A"])
    career = make_career(id="c1", books=["Book A", "Book B"])

    knowledge = build_expert_knowledge(expert, linked_careers=[career])

    assert knowledge.suggested_books == ["Book B"]


def test_build_expert_knowledge_dedupes_case_insensitively():
    expert = make_expert(recommended_books=["book a"])
    career = make_career(id="c1", books=["Book A"])

    knowledge = build_expert_knowledge(expert, linked_careers=[career])

    assert knowledge.suggested_books == []


def test_build_expert_knowledge_combines_companies_across_multiple_linked_careers():
    expert = make_expert(organizations=[])
    careers = [make_career(id="c1", companies=["Google"]), make_career(id="c2", companies=["Meta"])]

    knowledge = build_expert_knowledge(expert, linked_careers=careers)

    assert set(knowledge.suggested_companies) == {"Google", "Meta"}


def test_build_expert_knowledge_is_honestly_empty_with_no_linked_careers():
    expert = make_expert()
    knowledge = build_expert_knowledge(expert, linked_careers=[])
    assert knowledge.suggested_books == []
    assert knowledge.suggested_companies == []
    assert knowledge.suggested_certifications == []
