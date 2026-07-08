from datetime import datetime, timezone

from aureon.agents.base import BaseAgent
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.growth.evidence_summary import assemble_progress_evidence
from aureon.agents.specialized.growth.reasoning import analyze_progress, finalize_progress_report
from aureon.agents.specialized.growth.tools import (
    GrowthDetectionTool,
    ProgressComparisonTool,
    TimelineAnalysisTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.progress_report import ProgressDimension, ProgressReport
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class GrowthAgent(BaseAgent):
    """Tracks progress, learning milestone completion, interest evolution,
    and surfaces continuous recommendations over the student's long-term
    journey (Stage 5: Grow Continuously). Fulfills the V4 architecture's
    "Progress Agent" role — owns Memory Recall + Planning
    (agents/mission/capabilities.py).

    ``build_report`` (below) is Progress Intelligence's real reasoning
    entry point — evidence-driven, never a checklist or streak counter.
    """

    name = AgentName.GROWTH.value
    description = (
        "Tracks progress, roadmap completion, interest evolution, and "
        "surfaces ongoing opportunities and recommendations."
    )

    async def build_report(
        self, profile: StudentProfile, *, llm: LLMClient, mission: Mission | None = None
    ) -> ProgressReport:
        """Progress Intelligence: reasons over evidence already stored on
        the profile (Career DNA, Evidence Graph, Discovery Notebook,
        Reflection Journal, Career Exploration History, Career
        Candidates/Comparisons, Decision Memory) rather than any
        completion percentage. Facts (dimension directions, evidence
        counts, timeline) are computed deterministically in
        evidence_summary.py; only the narrative and next-priority
        reasoning come from the LLM."""
        stages = AGENT_EXECUTION_STAGES[self.name]
        if mission is not None:
            mission.record_stage(stages[0])  # "Reviewing Previous Reports"

        bundle = assemble_progress_evidence(profile)

        # Growth's own tools — genuinely real (no external infrastructure
        # needed, unlike every other specialist's toolset this phase):
        # they repackage the already-deterministic evidence bundle into
        # structured Evidence rather than recomputing anything.
        tool_results = [await run_tool_safely(ProgressComparisonTool(), bundle=bundle)]
        if mission is not None:
            mission.record_stage(stages[1])  # "Comparing Growth"
        tool_results.append(await run_tool_safely(GrowthDetectionTool(), bundle=bundle))
        if mission is not None:
            mission.record_stage(stages[2])  # "Identifying Patterns"
        tool_results.append(await run_tool_safely(TimelineAnalysisTool(), bundle=bundle))

        if mission is not None:
            mission.artifacts.setdefault("tool_results", {})[self.name] = [
                r.model_dump() for r in tool_results
            ]

        if bundle.insufficient_evidence:
            if mission is not None:
                mission.record_stage(stages[3])  # "Preparing Progress Report"
            # No LLM call for an evidence base this thin — the deterministic
            # dimensions/timeline are still real and worth showing, just
            # without a fabricated narrative layered on top.
            return ProgressReport(
                overall_narrative="",
                dimensions=[
                    ProgressDimension(
                        key=dim.key, label=dim.label, direction=dim.direction,
                        evidence_summary=dim.evidence_summary, reasoning="",
                    )
                    for dim in bundle.dimensions
                ],
                timeline=bundle.timeline,
                insufficient_evidence=True,
                insufficient_evidence_reason=bundle.insufficient_evidence_reason,
                generated_at=datetime.now(timezone.utc),
            )

        output = await analyze_progress(bundle, llm=llm)
        if mission is not None:
            mission.record_stage(stages[3])  # "Preparing Progress Report"

        return finalize_progress_report(bundle, output, datetime.now(timezone.utc))

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough for the conversational graph loop —
        # Progress Intelligence's primary trigger is the direct API
        # route ("conversation optional"), reached via build_report() above.
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
