from aureon.agents.specialized.decision.comparison_facts import extract_comparison_facts
from aureon.agents.specialized.decision.schemas import COMPARISON_DIMENSIONS
from aureon.domain.models.career import Career, CareerReality, FutureLens, SalaryRange

CAREER = Career(
    id="ai_research_scientist",
    name="AI Research Scientist",
    category="research",
    industry="technology",
    one_liner="x",
    reality=CareerReality(
        daily_work="Researching new methods.",
        work_environment="Lab-based.",
        collaboration_level="High",
        creativity_level="High",
        research_intensity="Very high",
        learning_curve="Steep",
        travel="Minimal",
        remote_possibility="High",
        stress_factors="Ambiguous problems",
        typical_challenges="x",
        misconceptions="x",
        long_term_growth="Strong",
        salary_ranges=[SalaryRange(region="US", range="$100k-$160k", note="")],
        required_education="PhD",
        required_skills=["ml", "statistics"],
        entrepreneurship_potential="Moderate — many spin out startups from research.",
    ),
    future_lens=FutureLens(
        ai_impact="x", automation_risk="Low", demand_2030="Strong", demand_2035="Strong",
        demand_2040="Strong", emerging_opportunities="x", timeline_narrative="x",
    ),
)


def test_extracts_all_fixed_dimensions():
    facts = extract_comparison_facts(CAREER)
    assert set(facts.keys()) == set(COMPARISON_DIMENSIONS)


def test_facts_are_read_directly_from_career_fields_not_invented():
    facts = extract_comparison_facts(CAREER)
    assert facts["creativity"] == "High"
    assert facts["research"] == "Very high"
    assert facts["required_education"] == "PhD"
    assert "ml" in facts["skills"]
    assert "$100k-$160k" in facts["salary"]
    assert facts["entrepreneurship_potential"] == "Moderate — many spin out startups from research."


def test_missing_entrepreneurship_potential_does_not_crash():
    career = CAREER.model_copy(deep=True)
    career.reality.entrepreneurship_potential = ""
    facts = extract_comparison_facts(career)
    assert facts["entrepreneurship_potential"] == "Not specified"
