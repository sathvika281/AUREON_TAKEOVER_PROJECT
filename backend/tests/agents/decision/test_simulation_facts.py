from aureon.agents.specialized.decision.simulation_facts import (
    SIMULATION_DIMENSIONS,
    extract_simulation_facts,
)
from aureon.domain.models.career import Career, CareerReality, FutureLens

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
        typical_challenges="Long feedback loops before results appear.",
        misconceptions="x",
        long_term_growth="Strong",
        required_education="PhD",
        required_skills=["ml", "statistics"],
    ),
    future_lens=FutureLens(
        ai_impact="Central to the field.",
        automation_risk="Low",
        demand_2030="Strong",
        demand_2035="Strong",
        demand_2040="Strong",
        emerging_opportunities="Foundation model research.",
        timeline_narrative="x",
    ),
)


def test_extracts_all_fixed_dimensions():
    facts = extract_simulation_facts(CAREER)
    assert set(facts.keys()) == set(SIMULATION_DIMENSIONS)


def test_facts_are_read_directly_from_career_fields_not_invented():
    facts = extract_simulation_facts(CAREER)
    assert "ml" in facts["required_skills"]
    assert facts["higher_education_path"] == "PhD"
    assert "Lab-based" in facts["work_environment"]
    assert "Long feedback loops" in facts["typical_challenges"]
    assert facts["growth_potential"] == "Strong"
    assert "Ambiguous problems" in facts["risk_factors"]
    assert facts["research_opportunities"] == "Very high"
    assert "Foundation model research" in facts["industry_opportunities"]
    assert "2030: Strong" in facts["future_adaptability"]
