"""Responsibility: the one entry point coordinating a Phase 2 feature
request end-to-end. Owns: intent resolution (via
``CareerOrchestratorAgent.plan_execution``), mission execution (via the
existing ``MissionOrchestrator``), output merge, and
confidence/evidence/reasoning computation. Does NOT own: the
conversational graph (``agents/orchestrator/graph.py``, untouched), any
specialist's own reasoning, or Career Memory/Event/Universe
Evolution/Journey Guidance logic (each lives in ``services/foundation``
and is only ever called from here, never reimplemented here). Consumed
by: nothing yet in this foundation — no API route wires to this;
a future route is the first real consumer.

Milestone note: this file is intentionally rewritten across Milestones
B/C/D (see the Architectural Decisions Log in the approved plan) — each
milestone's diff is deliberate, not scope creep.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from aureon.agents.foundation.objective_registry import get_objective_plan
from aureon.agents.mission.mission import MissionStatus
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.mission.snapshot import MissionSnapshot, build_mission_snapshot
from aureon.agents.specialized.institution.schemas import CollegeMatchTurnOutput
from aureon.agents.specialized.mentor.schemas import MentorMatchTurnOutput
from aureon.agents.specialized.opportunity.schemas import OpportunityRecommendationsOutput
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from aureon.domain.models.progress_report import ProgressReport
from aureon.services.foundation.career_memory.service import get_career_memory_snapshot
from aureon.services.foundation.events.bus import get_event_bus
from aureon.services.foundation.events.handlers import register_default_subscribers
from aureon.services.foundation.events.objective_event_registry import get_objective_event
from aureon.services.foundation.events.types import Event, EventType
from aureon.services.foundation.journey_guidance import JourneyGuidance, JourneyGuidanceEngine
from aureon.services.foundation.universe_evolution import UniverseEvent
from aureon.services.llm.base import LLMClient
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)

_EVIDENCE_BASE = 0.2
_EVIDENCE_STEP = 0.15
_FAILURE_PENALTY = 0.1
_MIN_CONFIDENCE = 0.05


@dataclass
class BuildOrchestratorResponse:
    mission_id: str
    objective: str
    executed_agents: list[str]
    failed_agents: list[str]
    artifacts: dict[str, Any]
    mission_snapshot: MissionSnapshot
    confidence: float
    confidence_basis: dict[str, int]
    evidence: list[str]
    reasoning: str
    #: Extension point — see BuildOrchestrator._resolve_conflicts. Empty
    #: today; real and callable, not a stub that fakes per-objective logic.
    conflicts: list[str]
    #: Wired via the Event Bus (Milestone C) — see handle_request.
    memory_changes: list[str] = field(default_factory=list)
    events_emitted: list[EventType] = field(default_factory=list)
    universe_event: UniverseEvent | None = None
    journey_guidance: JourneyGuidance | None = None


class BuildOrchestrator:
    """See module docstring above for Responsibility/Owns/Does NOT
    own/Consumed by."""

    def __init__(self, *, student_profile_repository: StudentProfileRepository) -> None:
        self._profiles = student_profile_repository
        self._bus = get_event_bus()
        register_default_subscribers(self._bus)  # safe to call repeatedly

    async def handle_request(
        self, *, student_id: str, objective: str, llm: LLMClient, context: dict[str, Any] | None = None
    ) -> BuildOrchestratorResponse:
        profile = await self._profiles.get_or_create(student_id)
        plan = get_objective_plan(objective)

        mission = MissionOrchestrator.create_mission(
            student_id=student_id, objective=objective, primary_agent=plan.primary_agent
        )
        resources = await plan.load_resources() if plan.load_resources else {}
        if context:
            # Additive — lets a step's build_call identify which specific
            # entity (e.g. which Opportunity) this request concerns,
            # without bypassing the Orchestrator. Existing objectives
            # never pass this, so their resources dict is unaffected.
            resources = {**resources, **context}

        failed_agents: list[str] = []
        for step in plan.steps:
            try:
                if step.agent_name == plan.primary_agent:
                    MissionOrchestrator.begin_execution(mission)
                    result = await step.build_call(profile, llm, mission, resources)
                    mission.artifacts[step.agent_name] = result
                else:
                    await MissionOrchestrator.delegate(
                        mission,
                        from_agent=plan.primary_agent,
                        to_agent=step.agent_name,
                        capability=step.capability,
                        reason=plan.reasoning,
                        call=lambda s=step: s.build_call(profile, llm, mission, resources),
                    )
            except Exception as exc:  # noqa: BLE001 — one agent's failure must not sink the request
                failed_agents.append(step.agent_name)
                MissionOrchestrator.fail(mission, str(exc))
                continue

        if mission.status != MissionStatus.FAILED:
            MissionOrchestrator.complete(mission)

        # Persist whatever real profile mutations the steps above made
        # (e.g. upsert_mentor_matches) so they survive past this request.
        await self._profiles.save(profile)

        # Milestone C: memory recording and universe evolution both flow
        # through the Event Bus now — not a direct call from here (see
        # the Architectural Decisions Log on why this replaced Milestone
        # B's temporary direct career_memory call).
        memory_changes: list[str] = []
        events_emitted: list[EventType] = []
        universe_event: UniverseEvent | None = None
        event_type = get_objective_event(objective)
        if event_type is not None:
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                student_id=student_id,
                payload={"objective": objective, "profile": profile},
                occurred_at=datetime.now(timezone.utc),
            )
            handler_results = await self._bus.publish(event)
            events_emitted.append(event_type)
            for result in handler_results:
                if isinstance(result, list):
                    memory_changes = result
                elif isinstance(result, UniverseEvent):
                    universe_event = result

        executed_agents = list(mission.specialists_selected)
        evidence = self._extract_evidence(mission.artifacts)
        confidence, confidence_basis = self._compute_confidence(evidence, executed_agents, failed_agents)
        conflicts = self._resolve_conflicts(mission.artifacts)
        reasoning = self._explain(executed_agents, evidence, conflicts, failed_agents)

        # Milestone D: for any objective whose mission produced a real
        # ProgressReport, ask Journey Guidance for the one highest-impact
        # next action. Not objective-name-gated — dispatches on the real
        # artifact type already extracted below, same pattern as
        # _extract_evidence.
        progress_report = next(
            (value for value in mission.artifacts.values() if isinstance(value, ProgressReport)), None
        )
        journey_guidance = JourneyGuidanceEngine().guide(
            progress_report=progress_report, career_memory=get_career_memory_snapshot(profile)
        )

        return BuildOrchestratorResponse(
            mission_id=mission.mission_id,
            objective=objective,
            executed_agents=executed_agents,
            failed_agents=failed_agents,
            artifacts=dict(mission.artifacts),
            mission_snapshot=build_mission_snapshot(mission),
            confidence=confidence,
            confidence_basis=confidence_basis,
            evidence=evidence,
            reasoning=reasoning,
            conflicts=conflicts,
            memory_changes=memory_changes,
            events_emitted=events_emitted,
            universe_event=universe_event,
            journey_guidance=journey_guidance,
        )

    def _extract_evidence(self, artifacts: dict[str, Any]) -> list[str]:
        """Real per-output-type field pulls. Extension point — to surface
        evidence from a new agent's artifact type, add one more isinstance
        branch here; who/when: whichever future objective introduces a new
        output type."""
        evidence: list[str] = []
        for value in artifacts.values():
            if isinstance(value, MentorMatchTurnOutput):
                for match in value.matches:
                    evidence.extend(match.supporting_evidence)
            elif isinstance(value, CollegeMatchTurnOutput):
                for match in value.matches:
                    evidence.extend(match.supporting_evidence)
            elif isinstance(value, ProgressReport):
                for dimension in value.dimensions:
                    evidence.extend(dimension.evidence_summary)
            elif isinstance(value, OpportunityRecommendationsOutput):
                for recommendation in value.recommendations:
                    evidence.extend(recommendation.fit.strengths)
            elif isinstance(value, OpportunityFitResult):
                evidence.extend(value.strengths)
        return evidence

    def _compute_confidence(
        self, evidence: list[str], executed_agents: list[str], failed_agents: list[str]
    ) -> tuple[float, dict[str, int]]:
        """Deterministic ceiling from real counts only — same
        'LLM proposes nothing, code bounds everything' philosophy as
        agents/specialized/career_intelligence/confidence.py, no LLM call
        of its own."""
        basis = {
            "evidence_count": len(evidence),
            "agents_succeeded": len(executed_agents),
            "agents_failed": len(failed_agents),
        }
        if not executed_agents:
            return 0.0, basis
        ceiling = min(1.0, _EVIDENCE_BASE + _EVIDENCE_STEP * len(evidence))
        penalty = _FAILURE_PENALTY * len(failed_agents)
        confidence = max(_MIN_CONFIDENCE, ceiling - penalty)
        return round(confidence, 4), basis

    def _resolve_conflicts(self, artifacts: dict[str, Any]) -> list[str]:
        """Extension point — why: a structural check for overlapping
        field names written by two different agents' artifacts; when:
        once a registered objective plan has 2+ agents producing
        overlapping fields; who: whichever future objective needs it.
        Returns [] today — no two agents in any registered plan produce
        overlapping fields yet."""
        return []

    def _explain(
        self, executed_agents: list[str], evidence: list[str], conflicts: list[str], failed_agents: list[str]
    ) -> str:
        if not executed_agents:
            parts = ["No agents completed successfully"]
        else:
            parts = [f"Combined output from {', '.join(executed_agents)}"]
        parts.append(f"backed by {len(evidence)} piece{'s' if len(evidence) != 1 else ''} of evidence")
        if failed_agents:
            parts.append(f"{len(failed_agents)} agent(s) failed and were skipped")
        if conflicts:
            parts.append(f"{len(conflicts)} conflict(s) detected")
        return " — ".join(parts) + "."
