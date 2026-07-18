import pytest

import aureon.agents.foundation  # noqa: F401 — registers objective plans, incl. Opportunity Hub's 7
import aureon.agents.specialized  # noqa: F401 — registers every agent
from aureon.agents.foundation.build_orchestrator import BuildOrchestrator
from aureon.agents.specialized.opportunity.providers import registry as provider_registry
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.career_memory import EvidenceArtifact, GrowthSkill
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.foundation.career_memory.service import get_career_memory_snapshot
from aureon.services.foundation.events.types import EventType
from aureon.services.foundation.journey_guidance import JourneyActionType, JourneyGuidanceEngine
from aureon.services.foundation.universe_evolution import UniverseEventType
from aureon.shared.types import AgentName
from tests.agents.opportunity._factories import make_opportunity
from tests.fakes import FakeLLMClient, FakeStudentProfileRepository

HIGH_FIT_OPPORTUNITY = make_opportunity(
    id="opp_high_fit", required_skills=["python"], domain_tags=["ai"], min_academic_level="undergraduate",
)
LOW_FIT_OPPORTUNITY = make_opportunity(
    id="opp_low_fit", required_skills=["python"], domain_tags=["ai"], min_academic_level="graduate",
    countries=["Germany"], is_remote=False, estimated_competitiveness="very_high",
)


class _FakeProvider:
    def __init__(self, opportunities):
        self._opportunities = opportunities

    async def fetch_opportunities(self):
        return self._opportunities


@pytest.fixture(autouse=True)
def _seeded_catalog(monkeypatch):
    """Isolates every test in this module from the real seeded provider
    (which would otherwise attempt a real Supabase call) — a fake
    provider serves both flagship opportunities instead."""
    monkeypatch.setattr(
        provider_registry, "_PROVIDERS", [_FakeProvider([HIGH_FIT_OPPORTUNITY, LOW_FIT_OPPORTUNITY])]
    )
    yield


async def test_high_fit_opportunity_evaluation_end_to_end():
    profile = StudentProfile(
        student_id="s1",
        goals=["ai"],
        career_hypotheses=[CareerHypothesis(career_name="AI Researcher", confidence=0.8)],
        evidence_graph=[EvidenceRecord(id="e1", text="Built a python AI project", source="github", relation="supports")],
    )
    profile.foundation_memory.identity.academic_level = "undergraduate"
    profile.foundation_memory.growth.skills.append(GrowthSkill(skill="python", status="mastered", evidence="Shipped 3 projects"))
    profile.foundation_memory.evidence.artifacts.append(EvidenceArtifact(kind="project", ref_id="p1", title="Python AI Project"))
    profiles = FakeStudentProfileRepository({"s1": profile})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="opportunity_fit_evaluation", llm=FakeLLMClient(),
        context={"opportunity_id": HIGH_FIT_OPPORTUNITY.id},
    )

    fit = response.artifacts[AgentName.OPPORTUNITY.value]
    assert len(fit.factors) == 10
    assert fit.highest_impact_gap is None or fit.highest_impact_gap.factor_key in {f.key for f in fit.factors}
    assert response.evidence  # real per-factor strengths surfaced through _extract_evidence
    assert response.confidence > 0


async def test_low_fit_opportunity_produces_a_real_not_ready_journey_guidance():
    profile = StudentProfile(student_id="s1")  # deliberately empty — no real signal anywhere
    profiles = FakeStudentProfileRepository({"s1": profile})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="opportunity_fit_evaluation", llm=FakeLLMClient(),
        context={"opportunity_id": LOW_FIT_OPPORTUNITY.id},
    )
    fit = response.artifacts[AgentName.OPPORTUNITY.value]
    assert fit.overall_score < 0.40
    assert fit.readiness_label == "not_ready"

    # Not wired into BuildOrchestrator.handle_request itself this stage
    # (its Journey Guidance dispatch is keyed off a real ProgressReport,
    # which no Opportunity Hub objective produces) — proving the rule in
    # isolation, exactly as the approved plan calls for.
    career_memory = get_career_memory_snapshot(await profiles.get_or_create("s1"))
    guidance = JourneyGuidanceEngine().guide(progress_report=None, career_memory=career_memory, opportunity_fit=fit)

    assert guidance is not None
    assert guidance.action_type in {
        JourneyActionType.BUILD_PROJECT, JourneyActionType.IMPROVE_DOCUMENTATION, JourneyActionType.CONTACT_MENTOR,
    }
    assert guidance.evidence == fit.gaps
    assert fit.highest_impact_gap is not None
    assert fit.highest_impact_gap.recommended_action in guidance.reason


async def test_opportunity_applied_records_real_interaction_event_and_universe_change():
    profile = StudentProfile(student_id="s1")
    profiles = FakeStudentProfileRepository({"s1": profile})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="opportunity_applied", llm=FakeLLMClient(),
        context={"opportunity_id": HIGH_FIT_OPPORTUNITY.id},
    )

    assert response.events_emitted == [EventType.OPPORTUNITY_APPLIED]
    assert response.universe_event is not None
    assert response.universe_event.event_type == UniverseEventType.CONSTELLATION_EXPANDED
    assert response.memory_changes  # non-empty — a real OpportunityEntry was recorded

    saved_profile = await profiles.get_or_create("s1")
    entries = saved_profile.foundation_memory.opportunities.entries
    assert len(entries) == 1
    assert entries[0].interaction == "applied"
    assert entries[0].ref_id == HIGH_FIT_OPPORTUNITY.id
    assert entries[0].category == HIGH_FIT_OPPORTUNITY.category


async def test_score_moves_directly_on_a_real_significant_evidence_change():
    profile = StudentProfile(student_id="s1")
    profiles = FakeStudentProfileRepository({"s1": profile})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    first = await orchestrator.handle_request(
        student_id="s1", objective="opportunity_fit_evaluation", llm=FakeLLMClient(),
        context={"opportunity_id": HIGH_FIT_OPPORTUNITY.id},
    )
    first_fit = first.artifacts[AgentName.OPPORTUNITY.value]

    saved_profile = await profiles.get_or_create("s1")
    saved_profile.foundation_memory.growth.skills.append(
        GrowthSkill(skill="python", status="mastered", evidence="Shipped 3 real projects")
    )
    saved_profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="python ai project", source="github", relation="supports")
    )
    saved_profile.foundation_memory.identity.academic_level = "undergraduate"

    second = await orchestrator.handle_request(
        student_id="s1", objective="opportunity_fit_evaluation", llm=FakeLLMClient(),
        context={"opportunity_id": HIGH_FIT_OPPORTUNITY.id},
    )
    second_fit = second.artifacts[AgentName.OPPORTUNITY.value]

    assert second_fit.confidence_basis["smoothed"] is False
    assert second_fit.overall_score > first_fit.overall_score
