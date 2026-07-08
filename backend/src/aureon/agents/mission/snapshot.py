from dataclasses import dataclass, field
from typing import Literal

from aureon.agents.mission.mission import Mission
from aureon.agents.mission.narration import narrate_mission
from aureon.agents.tools.base import Evidence
from aureon.shared.schemas import (
    AgentStatusDTO,
    DelegationDTO,
    MissionEvidenceDTO,
    MissionSnapshotDTO,
    ToolExecutionDTO,
)
from aureon.shared.types import AgentName

AgentSnapshotStatus = Literal["completed", "not_required"]


@dataclass
class AgentSnapshot:
    name: str
    display_name: str
    status: AgentSnapshotStatus


@dataclass
class DelegationSnapshot:
    from_agent: str
    to_agent: str
    capability: str
    reason: str


@dataclass
class ToolExecutionSnapshot:
    tool_name: str
    status: str
    explanation: str | None
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class MissionSnapshot:
    """A pure, read-only view over a Mission's already-real data — nothing
    computed here that wasn't already tracked during the request. This is
    the one shape every mission-backed route hands to the frontend; it
    never knows or cares which feature produced the Mission it's reading."""

    stages: list[str]
    agents: list[AgentSnapshot]
    delegations: list[DelegationSnapshot]
    tools: list[ToolExecutionSnapshot]
    evidence: list[Evidence]
    narration: list[str]


def _display_name(agent_name: str) -> str:
    return f"{agent_name.replace('_', ' ').title()} Agent"


def build_mission_snapshot(mission: Mission) -> MissionSnapshot:
    """Only two agent states are ever real in a synchronous
    request/response cycle — Completed (the agent is in
    ``specialists_selected``) and Not Required (it isn't). There is no
    in-flight "Waiting" to observe without streaming, which this phase
    deliberately doesn't add."""
    agents = [
        AgentSnapshot(
            name=name.value,
            display_name=_display_name(name.value),
            status="completed" if name.value in mission.specialists_selected else "not_required",
        )
        for name in AgentName
    ]

    delegations = [
        DelegationSnapshot(
            from_agent=d.from_agent, to_agent=d.to_agent,
            capability=d.capability.value, reason=d.reason,
        )
        for d in mission.delegations
    ]

    tools: list[ToolExecutionSnapshot] = []
    evidence: list[Evidence] = []
    for results in mission.artifacts.get("tool_results", {}).values():
        for r in results:
            tool_evidence = [Evidence.model_validate(e) for e in r.get("evidence", [])]
            tools.append(
                ToolExecutionSnapshot(
                    tool_name=r["tool_name"], status=r["status"],
                    explanation=r.get("explanation"), evidence=tool_evidence,
                )
            )
            evidence.extend(tool_evidence)

    return MissionSnapshot(
        stages=list(mission.stage_log),
        agents=agents,
        delegations=delegations,
        tools=tools,
        evidence=evidence,
        narration=narrate_mission(mission),
    )


def _evidence_dto(e: Evidence) -> MissionEvidenceDTO:
    return MissionEvidenceDTO(
        source=e.source, summary=e.summary, reliability=e.reliability,
        source_type=e.source_type, title=e.title, confidence=e.confidence,
        metadata=e.metadata, timestamp=e.timestamp,
    )


def mission_snapshot_to_dto(snapshot: MissionSnapshot) -> MissionSnapshotDTO:
    """The one place a domain-level MissionSnapshot becomes the API's
    MissionSnapshotDTO — every mission-backed route calls this instead of
    building the DTO shape itself, so the mapping stays in one place."""
    return MissionSnapshotDTO(
        stages=snapshot.stages,
        agents=[AgentStatusDTO(name=a.name, display_name=a.display_name, status=a.status) for a in snapshot.agents],
        delegations=[
            DelegationDTO(from_agent=d.from_agent, to_agent=d.to_agent, capability=d.capability, reason=d.reason)
            for d in snapshot.delegations
        ],
        tools=[
            ToolExecutionDTO(
                tool_name=t.tool_name, status=t.status, explanation=t.explanation,
                evidence=[_evidence_dto(e) for e in t.evidence],
            )
            for t in snapshot.tools
        ],
        evidence=[_evidence_dto(e) for e in snapshot.evidence],
        narration=snapshot.narration,
    )
