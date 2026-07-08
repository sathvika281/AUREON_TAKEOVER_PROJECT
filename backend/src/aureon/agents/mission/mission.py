import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from aureon.agents.mission.capabilities import Capability


class MissionStatus(StrEnum):
    """Every user request that goes through the Mission Orchestrator moves
    through the same lifecycle. Internal architecture only — no UI change,
    no persisted schema; a ``Mission`` lives for the duration of one
    request/turn."""

    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_FOR_DELEGATION = "waiting_for_delegation"
    KNOWLEDGE_FUSION = "knowledge_fusion"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DelegationRecord:
    from_agent: str
    to_agent: str
    capability: Capability
    reason: str


@dataclass
class Mission:
    """Ephemeral, in-process record of one orchestrated request. Never
    persisted to the database — the actual domain artifacts a mission
    produces (CareerComparison, MentorMatch, CollegeMatch, ...) already
    persist through the existing StudentProfile repositories exactly as
    they did before this package existed. This object only tracks *how*
    the request was coordinated, for the duration of the request."""

    student_id: str
    objective: str
    primary_agent: str
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: MissionStatus = MissionStatus.CREATED
    specialists_selected: list[str] = field(default_factory=list)
    stage_log: list[str] = field(default_factory=list)
    delegations: list[DelegationRecord] = field(default_factory=list)
    #: Keyed by agent name -> whatever that agent's call produced, plus a
    #: reserved "prior" key for pre-loaded prior-mission artifacts (see
    #: MissionOrchestrator.create_mission's ``prior_artifacts`` param).
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def record_stage(self, stage: str) -> None:
        self.stage_log.append(stage)
