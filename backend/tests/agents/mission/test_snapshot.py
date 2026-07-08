from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.mission import DelegationRecord
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.tools.base import Evidence
from aureon.shared.types import AgentName


def test_agent_status_only_ever_completed_or_not_required():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    mission.specialists_selected.append(AgentName.MENTOR.value)

    snapshot = build_mission_snapshot(mission)
    statuses = {a.name: a.status for a in snapshot.agents}

    assert statuses[AgentName.DECISION.value] == "completed"
    assert statuses[AgentName.MENTOR.value] == "completed"
    assert statuses[AgentName.INSTITUTION.value] == "not_required"
    # Every status is one of exactly two real values — never a fabricated "waiting".
    assert {a.status for a in snapshot.agents} <= {"completed", "not_required"}


def test_stages_and_delegations_map_directly_from_the_mission():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    mission.record_stage("Reviewing Candidate Careers")
    mission.record_stage("Comparing Trade-offs")
    mission.delegations.append(
        DelegationRecord(
            from_agent=AgentName.DECISION.value, to_agent=AgentName.INSTITUTION.value,
            capability=Capability.INVESTIGATION, reason="institution-fit analysis",
        )
    )

    snapshot = build_mission_snapshot(mission)

    assert snapshot.stages == ["Reviewing Candidate Careers", "Comparing Trade-offs"]
    assert len(snapshot.delegations) == 1
    assert snapshot.delegations[0].to_agent == AgentName.INSTITUTION.value
    assert snapshot.delegations[0].capability == "investigation"
    assert snapshot.narration[0] == "Decision Agent — Reviewing Candidate Careers"


def test_tools_and_evidence_are_read_from_mission_artifacts():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.MENTOR.value,
    )
    mission.artifacts["tool_results"] = {
        AgentName.MENTOR.value: [
            {
                "tool_name": "publication_reader", "status": "not_connected",
                "explanation": "No publication URLs configured yet.", "evidence": [],
            },
        ],
        AgentName.INSTITUTION.value: [
            {
                "tool_name": "curriculum_reader", "status": "completed", "explanation": None,
                "evidence": [Evidence(source="x", summary="real finding", title="A Title").model_dump()],
            },
        ],
    }

    snapshot = build_mission_snapshot(mission)

    assert len(snapshot.tools) == 2
    assert {t.tool_name for t in snapshot.tools} == {"publication_reader", "curriculum_reader"}
    assert len(snapshot.evidence) == 1
    assert snapshot.evidence[0].title == "A Title"


def test_mission_snapshot_to_dto_round_trips_shape():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.CAREER_INTELLIGENCE.value,
    )
    mission.record_stage("Mission Started")

    dto = mission_snapshot_to_dto(build_mission_snapshot(mission))

    assert dto.stages == ["Mission Started"]
    assert any(a.name == AgentName.CAREER_INTELLIGENCE.value for a in dto.agents)
    assert dto.tools == []
    assert dto.evidence == []
