from datetime import datetime, timedelta, timezone

from aureon.agents.specialized.growth.evidence_summary import assemble_progress_evidence
from aureon.agents.specialized.growth.tools import (
    GrowthDetectionTool,
    ProgressComparisonTool,
    TimelineAnalysisTool,
)
from aureon.agents.tools.base import ToolStatus, run_tool_safely
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.student_profile import StudentProfile

NOW = datetime(2026, 1, 30, tzinfo=timezone.utc)


def _profile_with_activity() -> StudentProfile:
    profile = StudentProfile(student_id="s1")
    profile.career_exploration_history = [
        CareerExplorationEvent(id=str(i), career_id="ai_research", interaction_type="opened", created_at=NOW - timedelta(days=1))
        for i in range(5)
    ]
    return profile


async def test_progress_comparison_tool_is_real_not_a_stub():
    bundle = assemble_progress_evidence(_profile_with_activity(), now=NOW)

    result = await run_tool_safely(ProgressComparisonTool(), bundle=bundle)

    assert result.status == ToolStatus.COMPLETED
    assert len(result.evidence) == len(bundle.dimensions)
    assert any("exploration" in e.source.lower() for e in result.evidence)


async def test_growth_detection_tool_reflects_real_directions():
    bundle = assemble_progress_evidence(_profile_with_activity(), now=NOW)

    result = await run_tool_safely(GrowthDetectionTool(), bundle=bundle)

    exploration_evidence = next(e for e in result.evidence if "exploration" in e.source.lower())
    assert "improving" in exploration_evidence.summary.lower()


async def test_timeline_analysis_tool_reflects_real_windows():
    bundle = assemble_progress_evidence(_profile_with_activity(), now=NOW)

    result = await run_tool_safely(TimelineAnalysisTool(), bundle=bundle)

    assert len(result.evidence) == len(bundle.timeline)
    assert any("Last Week" in e.source for e in result.evidence)
