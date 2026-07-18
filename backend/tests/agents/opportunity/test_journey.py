from datetime import datetime, timezone

from aureon.agents.specialized.opportunity.journey import (
    OpportunityJourneyStage,
    build_opportunity_journey,
)
from aureon.domain.models.career_memory import CareerMemory, OpportunityEntry
from aureon.domain.models.opportunity_fit import FitFactor, OpportunityFitResult
from aureon.domain.models.progress_report import ProgressPriority, ProgressReport
from aureon.services.foundation.journey_guidance import JourneyActionType

NOW = datetime.now(timezone.utc)


def _fit(readiness_label="not_ready", **overrides) -> OpportunityFitResult:
    defaults = dict(
        opportunity_id="opp_1", overall_score=0.3, confidence=0.5, confidence_basis={},
        readiness_label=readiness_label,
        factors=[FitFactor(key="skill_match", label="Skill Match", score=0.2, weight=0.2, data_available=True, rationale="x", evidence=["e"])],
        requirements_met=1, requirements_total=5,
        gaps=["Missing demonstrated evidence for required skill 'python'."],
    )
    defaults.update(overrides)
    return OpportunityFitResult(**defaults)


def _entry(interaction: str) -> OpportunityEntry:
    return OpportunityEntry(interaction=interaction, category="internship", ref_id="opp_1", opportunity_version=1, title="x", occurred_at=NOW)


def test_stage_is_completion_when_a_completed_interaction_exists():
    journey = build_opportunity_journey(_fit(), [_entry("completed")], CareerMemory())
    assert journey.current_stage == OpportunityJourneyStage.COMPLETION
    assert OpportunityJourneyStage.COMPLETION in journey.reached_stages


def test_stage_is_application_when_applied_interaction_exists():
    journey = build_opportunity_journey(_fit(), [_entry("applied")], CareerMemory())
    assert journey.current_stage == OpportunityJourneyStage.APPLICATION


def test_stage_is_ready_to_apply_when_fit_is_ready_and_no_interactions():
    journey = build_opportunity_journey(_fit(readiness_label="ready"), [], CareerMemory())
    assert journey.current_stage == OpportunityJourneyStage.READY_TO_APPLY


def test_stage_is_preparation_when_not_ready_and_no_interactions():
    journey = build_opportunity_journey(_fit(readiness_label="not_ready"), [], CareerMemory())
    assert journey.current_stage == OpportunityJourneyStage.PREPARATION
    assert journey.preparation_guidance is not None
    assert journey.preparation_guidance.action_type == JourneyActionType.BUILD_PROJECT


def test_interview_stage_is_unreachable_from_real_data_this_stage():
    """Documented placeholder — no interaction kind or fit state in this
    stage ever produces INTERVIEW."""
    for interaction in ("viewed", "saved", "applied", "withdrawn", "completed"):
        journey = build_opportunity_journey(_fit(), [_entry(interaction)], CareerMemory())
        assert journey.current_stage != OpportunityJourneyStage.INTERVIEW


def test_reached_stages_is_prefix_of_stage_order():
    journey = build_opportunity_journey(_fit(), [_entry("applied")], CareerMemory())
    assert journey.reached_stages == [
        OpportunityJourneyStage.CURRENT_STATE,
        OpportunityJourneyStage.PREPARATION,
        OpportunityJourneyStage.READY_TO_APPLY,
        OpportunityJourneyStage.APPLICATION,
    ]


def test_preparation_guidance_is_none_outside_preparation_stage():
    journey = build_opportunity_journey(_fit(readiness_label="ready"), [], CareerMemory())
    assert journey.preparation_guidance is None
