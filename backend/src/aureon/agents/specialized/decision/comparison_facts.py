from aureon.agents.specialized.decision.schemas import COMPARISON_DIMENSIONS
from aureon.domain.models.career import Career


def extract_comparison_facts(career: Career) -> dict[str, str]:
    """Deterministically maps a Career's existing Reality/Future Lens
    fields onto Decision Lab's 15 fixed comparison dimensions — no LLM
    call needed to produce these facts, and the LLM is never trusted as
    the source of truth for them (only for the personalized "why it
    matters" narrative layered on top, see reasoning.py)."""
    reality = career.reality
    future = career.future_lens

    salary_summary = (
        "; ".join(f"{s.region}: {s.range}" for s in reality.salary_ranges) or "Not specified"
    )
    skills_summary = ", ".join(reality.required_skills) or "Not specified"
    future_demand_summary = (
        f"2030: {future.demand_2030} | 2035: {future.demand_2035} | 2040: {future.demand_2040}"
    )

    facts = {
        "work_style": (
            f"{reality.work_environment}; collaboration: {reality.collaboration_level}; "
            f"creativity: {reality.creativity_level}"
        ),
        "creativity": reality.creativity_level,
        "research": reality.research_intensity,
        "collaboration": reality.collaboration_level,
        "work_life_balance": f"{reality.stress_factors}; remote: {reality.remote_possibility}",
        "growth": reality.long_term_growth,
        "future_demand": future_demand_summary,
        "required_education": reality.required_education,
        "skills": skills_summary,
        "lifestyle": f"{reality.daily_work} Travel: {reality.travel}",
        "salary": salary_summary,
        "travel": reality.travel,
        "stress": reality.stress_factors,
        "flexibility": reality.remote_possibility,
        "entrepreneurship_potential": reality.entrepreneurship_potential or "Not specified",
    }
    assert set(facts.keys()) == set(COMPARISON_DIMENSIONS)
    return facts
