import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from aureon.agents.mission.capabilities import Capability, owns_capability
from aureon.agents.mission.mission import DelegationRecord, Mission, MissionStatus


class DelegationNotOwnedError(RuntimeError):
    """Raised when a mission tries to delegate a capability to a specialist
    that doesn't own it — keeps ``AGENT_CAPABILITIES`` an enforced
    contract, not just documentation."""


class MissionOrchestrator:
    """Coordinates a mission end-to-end. This class performs NO domain
    reasoning of its own — it only receives an objective, selects/records
    which specialists are involved, sequences or parallelizes their calls,
    mediates delegation between them, and merges their outputs. Every
    method here is mechanical bookkeeping around calls that specialists
    (``BaseAgent`` subclasses and their capability methods) already make;
    it never decides *what* a career, mentor, or institution fits — that
    reasoning lives entirely inside the specialists themselves.
    """

    @staticmethod
    def create_mission(
        *,
        student_id: str,
        objective: str,
        primary_agent: str,
        prior_artifacts: dict[str, Any] | None = None,
    ) -> Mission:
        """Mission Created. ``prior_artifacts`` lets a caller preload
        already-persisted state (e.g. the student's previous comparisons
        or decision-memory entries — all fields that already exist on
        StudentProfile, no schema change) so specialists can consult prior
        mission output without re-deriving it — real Memory Recall, not a
        fresh-every-time conversation."""
        mission = Mission(student_id=student_id, objective=objective, primary_agent=primary_agent)
        mission.specialists_selected.append(primary_agent)
        if prior_artifacts:
            mission.artifacts["prior"] = prior_artifacts
        mission.status = MissionStatus.PLANNING
        return mission

    @staticmethod
    def begin_execution(mission: Mission) -> None:
        mission.status = MissionStatus.EXECUTING

    @staticmethod
    async def delegate(
        mission: Mission,
        *,
        from_agent: str,
        to_agent: str,
        capability: Capability,
        reason: str,
        call: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Whenever expertise belongs to another specialist, delegation
        happens automatically through here rather than one agent quietly
        reaching into another's responsibility. ``call`` is a zero-arg
        async callable the caller supplies, wrapping the target
        specialist's own method — this function never knows or cares how
        that specialist does its work, only that the handoff happened and
        capability ownership was respected.
        """
        if not owns_capability(to_agent, capability):
            raise DelegationNotOwnedError(
                f"'{to_agent}' does not own capability '{capability.value}' — "
                f"cannot delegate from '{from_agent}'"
            )

        if to_agent not in mission.specialists_selected:
            mission.specialists_selected.append(to_agent)
        mission.status = MissionStatus.WAITING_FOR_DELEGATION
        mission.delegations.append(
            DelegationRecord(from_agent=from_agent, to_agent=to_agent, capability=capability, reason=reason)
        )

        result = await call()

        mission.artifacts[to_agent] = result
        mission.status = MissionStatus.EXECUTING
        return result

    @staticmethod
    async def run_parallel(
        mission: Mission, tasks: dict[str, Callable[[], Awaitable[Any]]]
    ) -> dict[str, Any]:
        """Executes genuinely independent specialists concurrently rather
        than serially, whenever a mission's plan doesn't require one
        specialist's output before another can start. Results land in
        ``mission.artifacts`` keyed by specialist name, same as
        ``delegate``."""
        mission.status = MissionStatus.EXECUTING
        for name in tasks:
            if name not in mission.specialists_selected:
                mission.specialists_selected.append(name)

        names = list(tasks.keys())
        results = await asyncio.gather(*(tasks[name]() for name in names))
        for name, result in zip(names, results):
            mission.artifacts[name] = result
        return dict(zip(names, results))

    @staticmethod
    def fuse_knowledge(mission: Mission, *sources: dict[str, Any]) -> dict[str, Any]:
        """Merges artifact dicts produced across a mission's delegated/
        parallel calls into one fused context, tagging which specialist
        each piece came from. This is mechanical bookkeeping — the actual
        reasoning fusion already happens inside each specialist's own
        prompt (which already reads Career DNA + Evidence Graph + Career
        Candidates together); this method only formalizes and records
        that a fusion step occurred before final response assembly."""
        mission.status = MissionStatus.KNOWLEDGE_FUSION
        fused: dict[str, Any] = {}
        for source in sources:
            fused.update(source)
        mission.artifacts["fused"] = fused
        return fused

    @staticmethod
    def complete(mission: Mission) -> Mission:
        mission.status = MissionStatus.REVIEW
        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now(timezone.utc)
        return mission

    @staticmethod
    def fail(mission: Mission, error: str) -> Mission:
        mission.status = MissionStatus.FAILED
        mission.error = error
        mission.completed_at = datetime.now(timezone.utc)
        return mission
