from datetime import datetime, timezone

from aureon.domain.models.career_memory import CareerMemory
from aureon.domain.models.opportunity_fit import FitFactor, HighestImpactGap, OpportunityFitResult
from aureon.domain.models.progress_report import ProgressPriority, ProgressReport
from aureon.services.foundation.journey_guidance import (
    JourneyActionType,
    JourneyGuidanceEngine,
)

NOW = datetime.now(timezone.utc)
EMPTY_MEMORY = CareerMemory()


def _fit(readiness_label="not_ready", **overrides) -> OpportunityFitResult:
    defaults = dict(
        opportunity_id="opp_1", overall_score=0.3, confidence=0.5, confidence_basis={},
        readiness_label=readiness_label,
        factors=[FitFactor(key="skill_match", label="Skill Match", score=0.2, weight=0.2, data_available=True, rationale="x", evidence=["e"])],
        requirements_met=2, requirements_total=5,
        gaps=["Missing demonstrated evidence for required skill 'python'."],
    )
    defaults.update(overrides)
    return OpportunityFitResult(**defaults)


def test_guide_returns_none_when_report_missing():
    assert JourneyGuidanceEngine().guide(progress_report=None, career_memory=EMPTY_MEMORY) is None


def test_guide_returns_none_when_report_is_insufficient_evidence():
    report = ProgressReport(overall_narrative="", insufficient_evidence=True, generated_at=NOW)
    assert JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY) is None


def test_guide_returns_none_when_report_has_no_priorities():
    report = ProgressReport(overall_narrative="x", next_priorities=[], generated_at=NOW)
    assert JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY) is None


def test_guide_reuses_growths_top_priority():
    report = ProgressReport(
        overall_narrative="x",
        next_priorities=[
            ProgressPriority(rank=2, action="Contact a mentor about research paths", evidence="2 mentor matches found"),
            ProgressPriority(rank=1, action="Build a small project to demonstrate your Python skills", evidence="3 GitHub repos analyzed"),
        ],
        generated_at=NOW,
    )

    guidance = JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY)

    assert guidance is not None
    assert guidance.action_type == JourneyActionType.BUILD_PROJECT  # rank 1, not rank 2
    assert guidance.reason == "Build a small project to demonstrate your Python skills"
    assert guidance.evidence == ["3 GitHub repos analyzed"]


def test_classify_action_falls_back_honestly_when_no_keyword_matches():
    report = ProgressReport(
        overall_narrative="x",
        next_priorities=[ProgressPriority(rank=1, action="Keep exploring what excites you", evidence="steady engagement")],
        generated_at=NOW,
    )

    guidance = JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY)

    assert guidance.action_type == JourneyActionType.COMPLETE_TODAYS_MISSION


def test_guide_prioritizes_a_not_ready_opportunity_fit_over_progress_report():
    """Phase 2 Stage 2 addition: opportunity_fit is checked first, citing
    the real requirements_met/requirements_total and the real
    highest_impact_gap.recommended_action — even when a real
    ProgressReport with its own priorities is also present."""
    report = ProgressReport(
        overall_narrative="x",
        next_priorities=[ProgressPriority(rank=1, action="Practice interviewing", evidence="weak areas noted")],
        generated_at=NOW,
    )
    fit = _fit(
        highest_impact_gap=HighestImpactGap(
            factor_key="skill_match", label="Skill Match", potential_score_gain=0.1,
            recommended_action="Demonstrate the missing required skill with a real project.",
        )
    )

    guidance = JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY, opportunity_fit=fit)

    assert guidance is not None
    assert "2 of 5 requirements" in guidance.reason
    assert "Demonstrate the missing required skill with a real project." in guidance.reason
    assert guidance.evidence == fit.gaps
    assert guidance.action_type == JourneyActionType.BUILD_PROJECT  # "skill" keyword in the real gap text


def test_guide_falls_back_to_stage_1_behavior_when_opportunity_fit_is_ready():
    """A 'ready'/'almost_ready' fit must never override Stage 1's own
    Progress-Report-driven guidance — existing behavior is fully
    preserved when the opportunity isn't the honest blocker."""
    report = ProgressReport(
        overall_narrative="x",
        next_priorities=[ProgressPriority(rank=1, action="Build a small project", evidence="3 repos analyzed")],
        generated_at=NOW,
    )
    fit = _fit(readiness_label="ready")

    guidance = JourneyGuidanceEngine().guide(progress_report=report, career_memory=EMPTY_MEMORY, opportunity_fit=fit)

    assert guidance is not None
    assert guidance.reason == "Build a small project"


def test_guide_opportunity_fit_omitted_keeps_existing_signature_working():
    assert JourneyGuidanceEngine().guide(progress_report=None, career_memory=EMPTY_MEMORY) is None
