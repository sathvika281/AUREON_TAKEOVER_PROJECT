from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.narration import narrate_mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.shared.types import AgentName


def test_narrate_mission_attributes_stages_to_primary_agent():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    mission.record_stage("Reviewing Candidate Careers")
    mission.record_stage("Comparing Trade-offs")

    lines = narrate_mission(mission)

    assert lines == [
        "Decision Agent — Reviewing Candidate Careers",
        "Decision Agent — Comparing Trade-offs",
    ]


async def test_narrate_mission_shows_full_delegation_handoff():
    mission = MissionOrchestrator.create_mission(
        student_id="s1", objective="x", primary_agent=AgentName.DECISION.value,
    )
    mission.record_stage("Reviewing Candidate Careers")

    async def fake_call():
        return "institution profile"

    await MissionOrchestrator.delegate(
        mission,
        from_agent=AgentName.DECISION.value,
        to_agent=AgentName.INSTITUTION.value,
        capability=Capability.INVESTIGATION,
        reason="institution-fit analysis",
        call=fake_call,
    )

    lines = narrate_mission(mission)

    assert lines[0] == "Decision Agent — Reviewing Candidate Careers"
    assert lines[1] == "Decision Agent — Delegating investigation to Institution Agent (institution-fit analysis)"
    assert lines[2] == "Institution Agent working…"
    assert lines[3] == "Institution Profile received"
    assert lines[4] == "Decision Agent continues reasoning"
