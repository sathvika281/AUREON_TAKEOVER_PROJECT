from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SimulatedJourneyPhase(BaseModel):
    """One illustrative phase of a simulated journey — never a scheduled,
    deterministic plan, always a possible shape the path could take."""

    phase: str  # "Year 1", "Year 2", "Year 3+"
    focus: str
    milestones: list[str] = Field(default_factory=list)


class TradeOffAnalysis(BaseModel):
    advantages: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    sacrifices: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class CareerPathSimulation(BaseModel):
    """One independently-generated simulation for a single career path —
    15 dimensions total: 9 pure facts (required_skills through
    future_adaptability, read straight from the Career Knowledge Base),
    3 deterministic student-alignment facts (career_dna_alignment,
    student_interest_alignment, evidence_confidence — never LLM
    self-assessment), and 3 narrative fields the LLM genuinely reasons
    about (learning_journey, timeline, trade_offs)."""

    career_id: str
    career_name: str

    # Deterministic facts (simulation_facts.py) — never LLM output.
    required_skills: str
    higher_education_path: str
    work_environment: str
    lifestyle: str
    typical_challenges: str
    growth_potential: str
    risk_factors: str
    research_opportunities: str
    industry_opportunities: str
    future_adaptability: str

    # Deterministic student-alignment facts (simulation_alignment.py) —
    # never LLM self-assessment.
    career_dna_alignment: str
    student_interest_alignment: str
    evidence_confidence: str

    # LLM-reasoned, grounded in the facts above (simulation_reasoning.py).
    learning_journey: str
    expected_milestones: list[str] = Field(default_factory=list)
    timeline: list[SimulatedJourneyPhase] = Field(default_factory=list)
    trade_offs: TradeOffAnalysis = Field(default_factory=TradeOffAnalysis)

    # Deterministic, built after the LLM call (simulation_next_actions.py)
    # — never sent to or produced by the LLM.
    next_best_actions: list[str] = Field(default_factory=list)


class DecisionInsights(BaseModel):
    """Cross-career synthesis — the only place comparison/contrast
    reasoning happens. Encourages exploration, never forces a decision."""

    strongest_match_career_id: str | None = None
    why: str = ""
    possible_risks: list[str] = Field(default_factory=list)
    questions_to_explore: list[str] = Field(default_factory=list)
    recommended_next_investigation: str = ""
    #: All three below are filled in deterministically from real profile
    #: data (never LLM-invented names) — see simulation_pipeline.py.
    recommended_mentors: list[str] = Field(default_factory=list)
    recommended_institutions: list[str] = Field(default_factory=list)
    recommended_resources: list[str] = Field(default_factory=list)


class CareerSimulation(BaseModel):
    """One Career Simulator run — append-only history, same
    never-overwritten reasoning as CareerComparison/ParallelUniverseScenario."""

    id: str
    career_ids: list[str]
    career_names: dict[str, str]
    simulations: list[CareerPathSimulation] = Field(default_factory=list)
    decision_insights: DecisionInsights = Field(default_factory=DecisionInsights)
    missing_evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
