from aureon.agents.specialized.career_intelligence.confidence import evidence_strength_label
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.schemas import (
    CareerComparisonDTO,
    CareerPathSimulationDTO,
    CareerSimulationDTO,
    CollegeMatchDTO,
    ComparisonDimensionDTO,
    DecisionInsightsDTO,
    DecisionMemoryEntryDTO,
    MentorMatchDTO,
    ParallelUniverseBranchDTO,
    ParallelUniverseScenarioDTO,
    SimulatedJourneyPhaseDTO,
    TradeOffAnalysisDTO,
)

"""Shared presentation mapping from StudentProfile -> Phase 3 API DTOs.
Kept separate from profile_view.py (Discovery/Career Intelligence
concerns) and career_view.py (Career Knowledge Base), same
separation-of-concerns convention established in Phase 2."""


def _evidence(profile: StudentProfile, *, field: str, subject_id: str, relation: str) -> list[str]:
    return [
        e.text
        for e in profile.evidence_graph
        if getattr(e, field) == subject_id and e.relation == relation
    ]


def build_mentor_match_dtos(profile: StudentProfile) -> list[MentorMatchDTO]:
    """No raw confidence number is ever exposed — same treatment as
    Career Candidates. Discarded matches are omitted."""
    return [
        MentorMatchDTO(
            mentor_id=m.mentor_id,
            mentor_name=m.mentor_name,
            why_it_matches=m.why_it_matches,
            evidence_strength=evidence_strength_label(m.confidence),
            uncertainty_reason=m.uncertainty_reason,
            supporting_evidence=_evidence(profile, field="related_mentor", subject_id=m.mentor_id, relation="supports"),
            contradicting_evidence=_evidence(profile, field="related_mentor", subject_id=m.mentor_id, relation="contradicts"),
            missing_evidence=m.missing_evidence,
        )
        for m in profile.mentor_matches
        if m.status != "discarded"
    ]


def build_college_match_dtos(profile: StudentProfile) -> list[CollegeMatchDTO]:
    return [
        CollegeMatchDTO(
            institution_id=c.institution_id,
            institution_name=c.institution_name,
            why_it_matches=c.why_it_matches,
            evidence_strength=evidence_strength_label(c.confidence),
            uncertainty_reason=c.uncertainty_reason,
            supporting_evidence=_evidence(profile, field="related_institution", subject_id=c.institution_id, relation="supports"),
            contradicting_evidence=_evidence(profile, field="related_institution", subject_id=c.institution_id, relation="contradicts"),
            missing_evidence=c.missing_evidence,
        )
        for c in profile.college_matches
        if c.status != "discarded"
    ]


def build_career_comparison_dtos(profile: StudentProfile) -> list[CareerComparisonDTO]:
    return [
        CareerComparisonDTO(
            id=comp.id,
            career_ids=comp.career_ids,
            career_names=comp.career_names,
            dimensions=[
                ComparisonDimensionDTO(
                    dimension=d.dimension, per_career=d.per_career, why_it_matters_to_you=d.why_it_matters_to_you
                )
                for d in comp.dimensions
            ],
            summary_reason=comp.summary_reason,
            missing_evidence=comp.missing_evidence,
            created_at=comp.created_at,
        )
        for comp in profile.career_comparisons
    ]


def build_parallel_universe_dtos(profile: StudentProfile) -> list[ParallelUniverseScenarioDTO]:
    return [
        ParallelUniverseScenarioDTO(
            id=scenario.id,
            branches=[
                ParallelUniverseBranchDTO(
                    career_id=b.career_id, career_name=b.career_name, daily_work=b.daily_work,
                    lifestyle=b.lifestyle, growth=b.growth, challenges=b.challenges,
                    future_opportunities=b.future_opportunities,
                )
                for b in scenario.branches
            ],
            framing_note=scenario.framing_note,
            missing_evidence=scenario.missing_evidence,
            created_at=scenario.created_at,
        )
        for scenario in profile.parallel_universe_scenarios
    ]


def build_career_simulation_dtos(profile: StudentProfile) -> list[CareerSimulationDTO]:
    return [
        CareerSimulationDTO(
            id=sim.id,
            career_ids=sim.career_ids,
            career_names=sim.career_names,
            simulations=[
                CareerPathSimulationDTO(
                    career_id=p.career_id, career_name=p.career_name,
                    required_skills=p.required_skills, higher_education_path=p.higher_education_path,
                    work_environment=p.work_environment, lifestyle=p.lifestyle,
                    typical_challenges=p.typical_challenges, growth_potential=p.growth_potential,
                    risk_factors=p.risk_factors, research_opportunities=p.research_opportunities,
                    industry_opportunities=p.industry_opportunities, future_adaptability=p.future_adaptability,
                    career_dna_alignment=p.career_dna_alignment,
                    student_interest_alignment=p.student_interest_alignment,
                    evidence_confidence=p.evidence_confidence,
                    learning_journey=p.learning_journey, expected_milestones=p.expected_milestones,
                    timeline=[
                        SimulatedJourneyPhaseDTO(phase=t.phase, focus=t.focus, milestones=t.milestones)
                        for t in p.timeline
                    ],
                    trade_offs=TradeOffAnalysisDTO(
                        advantages=p.trade_offs.advantages, challenges=p.trade_offs.challenges,
                        opportunities=p.trade_offs.opportunities, sacrifices=p.trade_offs.sacrifices,
                        uncertainties=p.trade_offs.uncertainties,
                    ),
                    next_best_actions=p.next_best_actions,
                )
                for p in sim.simulations
            ],
            decision_insights=DecisionInsightsDTO(
                strongest_match_career_id=sim.decision_insights.strongest_match_career_id,
                why=sim.decision_insights.why, possible_risks=sim.decision_insights.possible_risks,
                questions_to_explore=sim.decision_insights.questions_to_explore,
                recommended_next_investigation=sim.decision_insights.recommended_next_investigation,
                recommended_mentors=sim.decision_insights.recommended_mentors,
                recommended_institutions=sim.decision_insights.recommended_institutions,
                recommended_resources=sim.decision_insights.recommended_resources,
            ),
            missing_evidence=sim.missing_evidence,
            created_at=sim.created_at,
        )
        for sim in profile.career_simulations
    ]


def build_decision_memory_dtos(profile: StudentProfile) -> list[DecisionMemoryEntryDTO]:
    ordered = sorted(profile.decision_memory, key=lambda e: e.created_at, reverse=True)
    return [
        DecisionMemoryEntryDTO(
            id=e.id, action_type=e.action_type, career_ids=e.career_ids,
            career_names=e.career_names, reason=e.reason, created_at=e.created_at,
        )
        for e in ordered
    ]
