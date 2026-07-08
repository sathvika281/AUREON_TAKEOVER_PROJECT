from aureon.domain.models.career import Career

#: 9 of the Career Simulator's 15 dimensions are pure facts, read directly
#: from the Career Knowledge Base — same deterministic-extraction
#: discipline as comparison_facts.py, just a different (journey-oriented)
#: vocabulary. The remaining 6 dimensions are either deterministic
#: student-alignment facts (simulation_alignment.py) or genuinely
#: LLM-reasoned narrative (simulation_reasoning.py).
SIMULATION_DIMENSIONS = [
    "required_skills",
    "higher_education_path",
    "work_environment",
    "lifestyle",
    "typical_challenges",
    "growth_potential",
    "risk_factors",
    "research_opportunities",
    "industry_opportunities",
    "future_adaptability",
]


def extract_simulation_facts(career: Career) -> dict[str, str]:
    """Deterministically maps a Career's existing Reality/Future Lens
    fields onto the Career Simulator's 9 fixed fact dimensions — no LLM
    call needed, and the LLM is never trusted as the source of truth for
    these (only for the narrative reasoning layered on top)."""
    reality = career.reality
    future = career.future_lens

    facts = {
        "required_skills": ", ".join(reality.required_skills) or "Not specified",
        "higher_education_path": reality.required_education,
        "work_environment": f"{reality.work_environment}; collaboration: {reality.collaboration_level}",
        "lifestyle": f"{reality.daily_work} Travel: {reality.travel}; remote: {reality.remote_possibility}",
        "typical_challenges": reality.typical_challenges,
        "growth_potential": reality.long_term_growth,
        "risk_factors": f"{reality.stress_factors}; automation risk: {future.automation_risk}",
        "research_opportunities": reality.research_intensity,
        "industry_opportunities": future.emerging_opportunities,
        "future_adaptability": (
            f"2030: {future.demand_2030} | 2035: {future.demand_2035} | 2040: {future.demand_2040}; "
            f"AI impact: {future.ai_impact}"
        ),
    }
    assert set(facts.keys()) == set(SIMULATION_DIMENSIONS)
    return facts
