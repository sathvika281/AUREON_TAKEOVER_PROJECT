from datetime import datetime

from aureon.agents.specialized.growth.evidence_summary import ProgressEvidenceBundle
from aureon.agents.specialized.growth.prompts import build_progress_messages
from aureon.agents.specialized.growth.schemas import PROGRESS_TOOL, ProgressTurnOutput
from aureon.domain.models.progress_report import ProgressDimension, ProgressPriority, ProgressReport
from aureon.services.llm.base import LLMClient


async def analyze_progress(bundle: ProgressEvidenceBundle, *, llm: LLMClient) -> ProgressTurnOutput:
    """The single reasoning entry point for Progress Intelligence — the
    evidence bundle (facts) is already fully computed by
    evidence_summary.py; this call only produces the personalized
    narrative layered on top, same facts-vs-reasoning split as Decision
    Lab's analyze_comparison."""
    messages = build_progress_messages(bundle)
    response = await llm.complete(messages, tools=[PROGRESS_TOOL], tool_choice="required")
    if not response.tool_calls:
        return ProgressTurnOutput(
            overall_narrative=response.content or "Progress could not be analyzed this time.",
        )
    return ProgressTurnOutput.model_validate(response.tool_calls[0].arguments)


def finalize_progress_report(
    bundle: ProgressEvidenceBundle, output: ProgressTurnOutput, now: datetime
) -> ProgressReport:
    """Merges the deterministic evidence bundle (facts — direction and
    evidence_summary per dimension, timeline) with the LLM's narrative
    layer, into one ProgressReport. Shared merge-in-one-place pattern,
    same purpose as finalize_comparison for Decision Lab."""
    reasoning_by_dimension = {r.dimension: r.reasoning for r in output.dimension_reasoning}

    dimensions = [
        ProgressDimension(
            key=dim.key,
            label=dim.label,
            direction=dim.direction,
            evidence_summary=dim.evidence_summary,
            reasoning=reasoning_by_dimension.get(
                dim.key, "No specific reasoning available for this dimension yet."
            ),
        )
        for dim in bundle.dimensions
    ]

    next_priorities = [
        ProgressPriority(rank=p.rank, action=p.action, evidence=p.evidence)
        for p in sorted(output.next_priorities, key=lambda p: p.rank)
    ]

    return ProgressReport(
        overall_narrative=output.overall_narrative,
        dimensions=dimensions,
        growing_strengths=output.growing_strengths,
        areas_slowing_down=output.areas_slowing_down,
        recent_improvements=output.recent_improvements,
        timeline=bundle.timeline,
        next_priorities=next_priorities,
        insufficient_evidence=bundle.insufficient_evidence,
        insufficient_evidence_reason=bundle.insufficient_evidence_reason,
        generated_at=now,
    )
