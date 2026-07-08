from datetime import datetime, timedelta, timezone

from aureon.agents.specialized.growth.evidence_summary import assemble_progress_evidence
from aureon.agents.specialized.growth.reasoning import analyze_progress, finalize_progress_report
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

NOW = datetime(2026, 1, 30, tzinfo=timezone.utc)


def _profile_with_activity() -> StudentProfile:
    profile = StudentProfile(student_id="s1")
    profile.career_exploration_history = [
        CareerExplorationEvent(id=str(i), career_id="ai_research", interaction_type="opened", created_at=NOW - timedelta(days=1))
        for i in range(5)
    ]
    return profile


async def test_analyze_progress_parses_dimension_reasoning_and_priorities():
    args = {
        "overall_narrative": "You're exploring AI research consistently.",
        "dimension_reasoning": [{"dimension": "exploration", "reasoning": "You opened several AI research pages this week."}],
        "growing_strengths": ["Exploration"],
        "areas_slowing_down": [],
        "recent_improvements": ["More exploration activity this week"],
        "next_priorities": [
            {"rank": 1, "action": "Explore two more AI research careers", "evidence": "Only one research pathway has been investigated."},
        ],
    }
    llm = FakeLLMClient([tool_call_response("record_progress_report", args)])
    bundle = assemble_progress_evidence(_profile_with_activity(), now=NOW)

    output = await analyze_progress(bundle, llm=llm)

    assert output.overall_narrative == args["overall_narrative"]
    assert output.next_priorities[0].action == "Explore two more AI research careers"


def test_finalize_progress_report_merges_facts_with_llm_narrative():
    bundle = assemble_progress_evidence(_profile_with_activity(), now=NOW)
    args = {
        "overall_narrative": "Solid week of exploring.",
        "dimension_reasoning": [{"dimension": "exploration", "reasoning": "personalized reason"}],
        "growing_strengths": ["Exploration"],
        "areas_slowing_down": [],
        "recent_improvements": [],
        "next_priorities": [{"rank": 1, "action": "Keep exploring", "evidence": "5 exploration events this week."}],
    }
    from aureon.agents.specialized.growth.schemas import ProgressTurnOutput
    output = ProgressTurnOutput.model_validate(args)

    report = finalize_progress_report(bundle, output, NOW)

    exploration_dim = next(d for d in report.dimensions if d.key == "exploration")
    assert exploration_dim.direction == "improving"  # real fact, not from the LLM
    assert exploration_dim.reasoning == "personalized reason"
    # A dimension the LLM didn't cover still gets an honest fallback.
    clarity_dim = next(d for d in report.dimensions if d.key == "career_clarity")
    assert "No specific reasoning available" in clarity_dim.reasoning
    assert report.next_priorities[0].rank == 1
    assert report.insufficient_evidence is False
