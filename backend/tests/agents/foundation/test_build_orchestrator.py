from datetime import datetime, timezone

import aureon.agents.foundation  # noqa: F401  (registers default objective plans)
import aureon.agents.specialized  # noqa: F401  (registers every agent)
from aureon.agents.foundation.build_orchestrator import BuildOrchestrator
from aureon.agents.foundation.objective_registry import (
    ExecutionPlan,
    ExecutionStep,
    register_objective_plan,
)
from aureon.agents.mission.capabilities import Capability
from aureon.domain.models.mentor_match import MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.foundation.events.objective_event_registry import register_objective_event
from aureon.services.foundation.events.types import EventType
from aureon.services.foundation.universe_evolution import UniverseEventType
from aureon.shared.types import AgentName
from tests.fakes import FakeLLMClient, FakeStudentProfileRepository


async def _failing_call(profile, llm, mission, resources):
    raise RuntimeError("simulated agent failure")


register_objective_plan(
    "test_synthetic_one_agent_fails",
    ExecutionPlan(
        primary_agent=AgentName.DECISION.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.MENTOR.value,
                capability=Capability.INVESTIGATION,
                build_call=_failing_call,
            )
        ],
        reasoning="Synthetic objective for Milestone A failure-handling verification.",
    ),
)


async def _records_a_mentor_match(profile, llm, mission, resources):
    """Simulates what the real mentor_match_analysis objective's
    _mentor_call does after upsert_mentor_matches — seeds a real active
    MentorMatch directly, without hitting the real MentorRepository (no
    network in this unit test)."""
    profile.mentor_matches.append(
        MentorMatch(
            id="m1", mentor_id="mentor_1", mentor_name="Dr. Ada", why_it_matches="shared curiosity",
            confidence=0.6, status="active", updated_at=datetime.now(timezone.utc),
        )
    )
    return {"seeded": True}


register_objective_plan(
    "test_synthetic_records_mentor_match",
    ExecutionPlan(
        primary_agent=AgentName.DECISION.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.MENTOR.value,
                capability=Capability.INVESTIGATION,
                build_call=_records_a_mentor_match,
            )
        ],
        reasoning="Synthetic objective for Career Memory + Event Bus wiring verification.",
    ),
)
# Synthetic objective->event registration, made only in this test module,
# proving the Milestone C bus-based plumbing end-to-end — none of the 3
# real objectives honestly map to an EventType yet (see the Architectural
# Decisions Log).
register_objective_event("test_synthetic_records_mentor_match", EventType.MENTOR_CONNECTED)


async def test_handle_request_resolves_plan_and_returns_populated_response():
    profiles = FakeStudentProfileRepository({"s1": StudentProfile(student_id="s1")})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="progress_intelligence_analysis", llm=FakeLLMClient()
    )

    assert response.objective == "progress_intelligence_analysis"
    assert AgentName.GROWTH.value in response.executed_agents
    assert response.failed_agents == []
    assert 0.0 <= response.confidence <= 1.0
    assert response.confidence_basis["agents_succeeded"] == len(response.executed_agents)
    assert response.reasoning  # non-empty, mentions what happened
    assert response.conflicts == []
    assert response.mission_snapshot.stages  # real stages were recorded
    # Not wired until later milestones — must stay at their honest defaults here.
    assert response.memory_changes == []
    assert response.events_emitted == []
    assert response.universe_event is None
    assert response.journey_guidance is None


async def test_handle_request_degrades_gracefully_when_an_agent_fails():
    profiles = FakeStudentProfileRepository({"s1": StudentProfile(student_id="s1")})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="test_synthetic_one_agent_fails", llm=FakeLLMClient()
    )

    assert response.failed_agents == [AgentName.MENTOR.value]
    assert AgentName.MENTOR.value not in response.artifacts
    assert "failed" in response.reasoning.lower()


async def test_handle_request_populates_memory_changes_after_a_real_profile_mutation():
    profiles = FakeStudentProfileRepository({"s1": StudentProfile(student_id="s1")})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="test_synthetic_records_mentor_match", llm=FakeLLMClient()
    )

    assert response.memory_changes == ["connections: 1 active"]
    assert response.events_emitted == [EventType.MENTOR_CONNECTED]
    assert response.universe_event is not None
    assert response.universe_event.event_type == UniverseEventType.GUIDING_STAR_BRIGHTENED
    saved_profile = await profiles.get_or_create("s1")
    assert len(saved_profile.mentor_matches) == 1


async def test_handle_request_progress_intelligence_analysis_full_pipeline():
    """The one fully real, non-synthetic end-to-end path through all
    four milestones: intent resolution -> mission execution -> artifact
    merge -> confidence/evidence/reasoning -> Career Memory (no
    connections here, so honestly empty) -> Journey Guidance, all backed
    by genuinely computed data. Seeds 5 real notebook entries — Growth's
    own MIN_EVIDENCE_FOR_PROGRESS_REPORT threshold — so build_report
    produces a real, non-insufficient-evidence ProgressReport."""
    from aureon.domain.models.notebook import NotebookEntry

    profile = StudentProfile(student_id="s1")
    for i in range(5):
        profile.notebook_entries.append(
            NotebookEntry(id=f"n{i}", kind="observation", text=f"Observation {i}", source="conversation")
        )
    profiles = FakeStudentProfileRepository({"s1": profile})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    response = await orchestrator.handle_request(
        student_id="s1", objective="progress_intelligence_analysis", llm=FakeLLMClient()
    )

    growth_report = response.artifacts[AgentName.GROWTH.value]
    assert growth_report.insufficient_evidence is False
    assert response.executed_agents == [AgentName.GROWTH.value]
    assert response.failed_agents == []
    assert response.evidence  # real per-dimension evidence_summary entries
    assert 0.0 <= response.confidence <= 1.0
    if growth_report.next_priorities:
        assert response.journey_guidance is not None
        top = min(growth_report.next_priorities, key=lambda p: p.rank)
        assert response.journey_guidance.reason == top.action
        assert response.journey_guidance.evidence == [top.evidence]


async def test_handle_request_raises_for_unregistered_objective():
    import pytest

    profiles = FakeStudentProfileRepository({"s1": StudentProfile(student_id="s1")})
    orchestrator = BuildOrchestrator(student_profile_repository=profiles)

    with pytest.raises(ValueError):
        await orchestrator.handle_request(student_id="s1", objective="never_registered", llm=FakeLLMClient())
