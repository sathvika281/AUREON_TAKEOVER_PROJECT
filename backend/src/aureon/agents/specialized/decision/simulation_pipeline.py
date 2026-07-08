import asyncio
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.mission.mission import Mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.specialized.decision.simulation_alignment import compute_alignment
from aureon.agents.specialized.decision.simulation_facts import extract_simulation_facts
from aureon.agents.specialized.decision.simulation_next_actions import build_next_actions
from aureon.agents.specialized.decision.simulation_reasoning import (
    analyze_career_simulation,
    analyze_decision_insights,
)
from aureon.agents.specialized.growth.evidence_summary import assemble_progress_evidence
from aureon.domain.models.career import Career
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_simulation import (
    CareerPathSimulation,
    CareerSimulation,
    DecisionInsights,
    SimulatedJourneyPhase,
    TradeOffAnalysis,
)
from aureon.domain.models.decision_memory import DecisionMemoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.career_exploration import record_exploration_event
from aureon.domain.services.match_recommendations import (
    top_active_institution_names,
    top_active_mentor_names,
)
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName

CAREER_SIMULATION_STAGES = [
    "Mission Created",
    "Collecting Student Context",
    "Collecting Career Evidence",
    "Generating Independent Simulations",
    "Comparing Simulations",
    "Building Decision Insights",
    "Updating Reports",
    "Simulation Complete",
]

class CareerSimulationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    status: str  # "completed" | "insufficient_evidence" | "failed"
    explanation: str | None = None
    simulation: CareerSimulation | None = None
    stages: list[str] = Field(default_factory=list)
    evidence_added: bool = False
    mission: Mission
    artifacts_updated: list[str] = Field(default_factory=list)


def _recommended_resources(profile: StudentProfile, career_ids: list[str]) -> list[str]:
    """Deterministic pointers to Aureon's own real features the student
    hasn't used yet — never a fabricated external book/course/link."""
    resources: list[str] = []
    if not profile.career_investigations:
        resources.append("No Search Intelligence investigations yet — try investigating one of these fields.")
    if not any(e.source == "github" for e in profile.evidence_graph):
        resources.append("No GitHub repository analyzed yet — GitHub Intelligence can extract real skill evidence.")
    if not any(e.source == "document" for e in profile.evidence_graph):
        resources.append("No documents analyzed yet — Document Intelligence can read a resume, transcript, or portfolio.")
    if not profile.mentor_matches:
        resources.append("No mentors matched yet — run Mentor Match to find real mentors aligned with your Career DNA.")
    if not profile.college_matches:
        resources.append("No institutions matched yet — run Institution Match to find real universities aligned with your Career DNA.")
    return resources


async def run_career_simulation(
    career_ids: list[str], *, student_id: str, profile: StudentProfile, careers: list[Career], llm: LLMClient,
) -> CareerSimulationResult:
    """Decision Agent's Career Simulator (V11) — reuses the Mission
    Orchestrator and Knowledge Fusion exactly as V4/V5 built them; no
    delegation, since comparison/simulation reasoning is Decision's own
    capability outright."""
    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="career_simulation", primary_agent=AgentName.DECISION.value,
    )
    mission.record_stage(CAREER_SIMULATION_STAGES[0])  # "Mission Created"
    MissionOrchestrator.begin_execution(mission)

    progress = assemble_progress_evidence(profile)
    candidates_by_id: dict[str, CareerCandidate] = {c.career_id: c for c in profile.career_candidates}
    careers_by_id: dict[str, Career] = {c.id: c for c in careers}
    mission.record_stage(CAREER_SIMULATION_STAGES[1])  # "Collecting Student Context"

    facts_by_id: dict[str, dict[str, str]] = {}
    alignment_by_id = {}
    for career_id in career_ids:
        career = careers_by_id[career_id]
        candidate = candidates_by_id[career_id]
        facts_by_id[career_id] = extract_simulation_facts(career)
        alignment_by_id[career_id] = compute_alignment(profile, career, candidate)
    mission.record_stage(CAREER_SIMULATION_STAGES[2])  # "Collecting Career Evidence"

    outputs = await asyncio.gather(*(
        analyze_career_simulation(
            careers_by_id[cid], facts_by_id[cid], alignment_by_id[cid],
            career_dna=profile.career_dna, progress=progress, llm=llm,
        )
        for cid in career_ids
    ))
    outputs_by_id = dict(zip(career_ids, outputs))
    mission.record_stage(CAREER_SIMULATION_STAGES[3])  # "Generating Independent Simulations"

    career_names = {cid: careers_by_id[cid].name for cid in career_ids}
    entries = [(cid, career_names[cid], outputs_by_id[cid]) for cid in career_ids]
    mission.record_stage(CAREER_SIMULATION_STAGES[4])  # "Comparing Simulations"

    insights_output = await analyze_decision_insights(entries, llm=llm)
    mission.record_stage(CAREER_SIMULATION_STAGES[5])  # "Building Decision Insights"

    MissionOrchestrator.fuse_knowledge(mission, {
        "simulations": {cid: o.model_dump() for cid, o in outputs_by_id.items()},
        "decision_insights": insights_output.model_dump(),
    })

    any_insufficient = insights_output.insufficient_evidence or all(o.insufficient_evidence for o in outputs)
    if any_insufficient:
        MissionOrchestrator.complete(mission)
        mission.record_stage(CAREER_SIMULATION_STAGES[7])  # "Simulation Complete"
        return CareerSimulationResult(
            status="insufficient_evidence",
            explanation=insights_output.insufficient_evidence_reason or "This simulation could not be completed this time.",
            stages=mission.stage_log, mission=mission,
        )

    recommended_mentors = top_active_mentor_names(profile)
    recommended_institutions = top_active_institution_names(profile)
    recommended_resources = _recommended_resources(profile, career_ids)

    simulations: list[CareerPathSimulation] = []
    for cid in career_ids:
        career = careers_by_id[cid]
        facts = facts_by_id[cid]
        alignment = alignment_by_id[cid]
        output = outputs_by_id[cid]
        other_names = [career_names[other] for other in career_ids if other != cid]

        simulations.append(CareerPathSimulation(
            career_id=cid, career_name=career.name,
            required_skills=facts["required_skills"], higher_education_path=facts["higher_education_path"],
            work_environment=facts["work_environment"], lifestyle=facts["lifestyle"],
            typical_challenges=facts["typical_challenges"], growth_potential=facts["growth_potential"],
            risk_factors=facts["risk_factors"], research_opportunities=facts["research_opportunities"],
            industry_opportunities=facts["industry_opportunities"], future_adaptability=facts["future_adaptability"],
            career_dna_alignment=alignment.career_dna_alignment,
            student_interest_alignment=alignment.student_interest_alignment,
            evidence_confidence=alignment.evidence_confidence,
            learning_journey=output.learning_journey, expected_milestones=output.expected_milestones,
            timeline=[
                SimulatedJourneyPhase(phase=p.phase, focus=p.focus, milestones=p.milestones)
                for p in output.timeline
            ],
            trade_offs=TradeOffAnalysis(
                advantages=output.trade_offs.advantages, challenges=output.trade_offs.challenges,
                opportunities=output.trade_offs.opportunities, sacrifices=output.trade_offs.sacrifices,
                uncertainties=output.trade_offs.uncertainties,
            ),
            next_best_actions=build_next_actions(career, other_names, profile),
        ))

    now = datetime.now(timezone.utc)
    simulation = CareerSimulation(
        id=str(uuid.uuid4()), career_ids=career_ids, career_names=career_names, simulations=simulations,
        decision_insights=DecisionInsights(
            strongest_match_career_id=insights_output.strongest_match_career_id,
            why=insights_output.why, possible_risks=insights_output.possible_risks,
            questions_to_explore=insights_output.questions_to_explore,
            recommended_next_investigation=insights_output.recommended_next_investigation,
            recommended_mentors=recommended_mentors, recommended_institutions=recommended_institutions,
            recommended_resources=recommended_resources,
        ),
        created_at=now,
    )
    profile.career_simulations.append(simulation)
    profile.decision_memory.append(DecisionMemoryEntry(
        id=str(uuid.uuid4()), action_type="simulated", career_ids=career_ids, career_names=career_names,
        reason=insights_output.why or "Simulated possible futures across these career paths.",
        created_at=now,
    ))
    for career_id in career_ids:
        record_exploration_event(
            profile, career_id=career_id, interaction_type="simulated",
            metadata={"simulated_with": [cid for cid in career_ids if cid != career_id]}, now=now,
        )
    mission.record_stage(CAREER_SIMULATION_STAGES[6])  # "Updating Reports"

    MissionOrchestrator.complete(mission)
    mission.record_stage(CAREER_SIMULATION_STAGES[7])  # "Simulation Complete"

    return CareerSimulationResult(
        status="completed", simulation=simulation, stages=mission.stage_log,
        evidence_added=True, mission=mission,
        artifacts_updated=["Career Simulations Updated", "Decision Memory Updated", "Career Exploration History Updated"],
    )
