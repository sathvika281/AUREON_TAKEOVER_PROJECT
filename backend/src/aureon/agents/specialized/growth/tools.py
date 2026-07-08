from datetime import datetime, timezone

from aureon.agents.specialized.growth.evidence_summary import ProgressEvidenceBundle
from aureon.agents.tools.base import Evidence, Tool, ToolResult, ToolStatus

#: Unlike every other specialist's tools this phase, Progress's three
#: tools need no external infrastructure at all — they operate entirely
#: on the deterministic ProgressEvidenceBundle already computed by
#: evidence_summary.py (built in the Progress Intelligence phase). Real
#: work, not stubs: "real work where possible" applied honestly.


class ProgressComparisonTool(Tool):
    name = "progress_comparison"
    description = "Compares each progress dimension's recent activity against what came before it."

    async def execute(self, *, bundle: ProgressEvidenceBundle, **kwargs) -> ToolResult:
        evidence = [
            Evidence(
                source=f"Progress dimension: {dim.label}",
                summary="; ".join(dim.evidence_summary),
                reliability="deterministic — computed from stored timestamps, not LLM-estimated",
            )
            for dim in bundle.dimensions
        ]
        return ToolResult(tool_name=self.name, status=ToolStatus.COMPLETED, evidence=evidence)


class TimelineAnalysisTool(Tool):
    name = "timeline_analysis"
    description = "Analyzes the student's activity across Last Week / Last Month / Overall Journey."

    async def execute(self, *, bundle: ProgressEvidenceBundle, **kwargs) -> ToolResult:
        evidence = [
            Evidence(source=f"Timeline: {window.label}", summary=window.description)
            for window in bundle.timeline
        ]
        return ToolResult(tool_name=self.name, status=ToolStatus.COMPLETED, evidence=evidence)


class GrowthDetectionTool(Tool):
    name = "growth_detection"
    description = "Identifies which dimensions are genuinely improving or slowing, from real deltas only."

    async def execute(self, *, bundle: ProgressEvidenceBundle, **kwargs) -> ToolResult:
        evidence = [
            Evidence(
                source=f"Growth signal: {dim.label}",
                summary=f"Direction: {dim.direction}",
                reliability="deterministic — never asserted by the LLM",
            )
            for dim in bundle.dimensions
        ]
        return ToolResult(tool_name=self.name, status=ToolStatus.COMPLETED, evidence=evidence)
