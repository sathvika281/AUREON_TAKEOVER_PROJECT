from aureon.agents.specialized.opportunity.search import keyword_semantic_search
from tests.agents.opportunity._factories import make_opportunity

AI_INTERNSHIP = make_opportunity(
    id="ai_intern", title="AI Research Internship", category="internship", domain_tags=["ai", "machine learning"]
)
ROBOTICS_HACKATHON = make_opportunity(
    id="robotics_hack", title="Robotics Innovation Hackathon", category="hackathon", domain_tags=["robotics"]
)
GERMANY_SCHOLARSHIP = make_opportunity(
    id="germany_scholar", title="DAAD-style Study Scholarship", category="scholarship",
    countries=["Germany"], is_remote=False, domain_tags=["engineering"],
)
CATALOG = [AI_INTERNSHIP, ROBOTICS_HACKATHON, GERMANY_SCHOLARSHIP]


def test_ai_internships_worked_example():
    result = keyword_semantic_search(CATALOG, "AI internships")
    assert result and result[0].id == "ai_intern"


def test_robotics_hackathons_worked_example():
    result = keyword_semantic_search(CATALOG, "Robotics hackathons")
    assert result and result[0].id == "robotics_hack"


def test_scholarships_for_germany_worked_example():
    result = keyword_semantic_search(CATALOG, "Scholarships for Germany")
    assert result and result[0].id == "germany_scholar"


def test_no_matching_tokens_returns_empty():
    result = keyword_semantic_search(CATALOG, "underwater basket weaving")
    assert result == []


def test_empty_query_returns_full_catalog_unchanged():
    assert keyword_semantic_search(CATALOG, "") == CATALOG


def test_ranks_by_number_of_matching_tokens():
    strong_match = make_opportunity(id="strong", title="AI Robotics Research Internship", domain_tags=["ai", "robotics"])
    weak_match = make_opportunity(id="weak", title="Business Internship", domain_tags=[])
    result = keyword_semantic_search([weak_match, strong_match], "AI robotics internship")
    assert [o.id for o in result] == ["strong", "weak"]
