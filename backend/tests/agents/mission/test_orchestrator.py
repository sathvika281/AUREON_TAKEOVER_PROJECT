import pytest

from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.mission import MissionStatus
from aureon.agents.mission.orchestrator import DelegationNotOwnedError, MissionOrchestrator
from aureon.shared.types import AgentName


def test_create_mission_starts_in_planning_with_primary_agent_selected():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="mentor_match_analysis", primary_agent=AgentName.DECISION.value,
    )
    assert mission.status == MissionStatus.PLANNING
    assert mission.specialists_selected == [AgentName.DECISION.value]
    assert mission.artifacts == {}


def test_create_mission_preloads_prior_artifacts_for_memory_recall():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DISCOVERY.value,
        prior_artifacts={"last_comparison_id": "abc"},
    )
    assert mission.artifacts["prior"] == {"last_comparison_id": "abc"}


async def test_delegate_calls_target_and_records_artifact_and_delegation():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="mentor_match_analysis", primary_agent=AgentName.DECISION.value,
    )

    async def fake_call():
        return {"matches": ["mentor_1"]}

    result = await MissionOrchestrator.delegate(
        mission,
        from_agent=AgentName.DECISION.value,
        to_agent=AgentName.MENTOR.value,
        capability=Capability.INVESTIGATION,
        reason="test delegation",
        call=fake_call,
    )

    assert result == {"matches": ["mentor_1"]}
    assert mission.artifacts[AgentName.MENTOR.value] == {"matches": ["mentor_1"]}
    assert len(mission.delegations) == 1
    assert mission.delegations[0].to_agent == AgentName.MENTOR.value
    assert mission.status == MissionStatus.EXECUTING
    assert AgentName.MENTOR.value in mission.specialists_selected


async def test_delegate_rejects_capability_the_target_does_not_own():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )

    async def fake_call():
        return "should never run"

    with pytest.raises(DelegationNotOwnedError):
        await MissionOrchestrator.delegate(
            mission,
            from_agent=AgentName.DECISION.value,
            to_agent=AgentName.MENTOR.value,
            capability=Capability.DOCUMENT_INTELLIGENCE,  # Mentor doesn't own this
            reason="invalid delegation",
            call=fake_call,
        )


async def test_run_parallel_executes_independent_specialists_concurrently():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )

    async def mentor_call():
        return "mentor result"

    async def institution_call():
        return "institution result"

    results = await MissionOrchestrator.run_parallel(
        mission,
        {AgentName.MENTOR.value: mentor_call, AgentName.INSTITUTION.value: institution_call},
    )

    assert results == {AgentName.MENTOR.value: "mentor result", AgentName.INSTITUTION.value: "institution result"}
    assert mission.artifacts[AgentName.MENTOR.value] == "mentor result"
    assert mission.artifacts[AgentName.INSTITUTION.value] == "institution result"


def test_fuse_knowledge_merges_sources_and_marks_status():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )

    fused = MissionOrchestrator.fuse_knowledge(mission, {"a": 1}, {"b": 2})

    assert fused == {"a": 1, "b": 2}
    assert mission.status == MissionStatus.KNOWLEDGE_FUSION
    assert mission.artifacts["fused"] == {"a": 1, "b": 2}


def test_complete_and_fail_set_terminal_status():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    MissionOrchestrator.complete(mission)
    assert mission.status == MissionStatus.COMPLETED
    assert mission.completed_at is not None

    failed_mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    MissionOrchestrator.fail(failed_mission, "boom")
    assert failed_mission.status == MissionStatus.FAILED
    assert failed_mission.error == "boom"


def test_mission_record_stage_appends_to_stage_log():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.MENTOR.value,
    )
    mission.record_stage("Searching Mentors")
    mission.record_stage("Building Mentor Profile")
    assert mission.stage_log == ["Searching Mentors", "Building Mentor Profile"]
