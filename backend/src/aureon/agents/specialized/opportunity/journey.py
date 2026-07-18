"""Responsibility: one opportunity's own structured preparation path —
not a roadmap feature. Owns: `OpportunityJourneyStage`, `OpportunityJourney`,
`build_opportunity_journey`. Does NOT own: "what should the student do to
progress" reasoning — that's `JourneyGuidanceEngine.guide()`
(services/foundation/journey_guidance.py), reused directly here, never
duplicated. Consumed by: `OpportunityAgent.find_opportunities`, which
attaches the result to `OpportunityRecommendation.journey`.

Deterministic stage derivation from real interaction history + real
fit — never fabricated progress. The `INTERVIEW` stage exists in the
enum but is honestly unreachable from real data this stage: no
interview-tracking event exists yet (Interview Intelligence is
explicitly out of scope) — it's a defined placeholder for that future
feature, not a fabricated live status.
"""

from enum import StrEnum

from pydantic import BaseModel

from aureon.domain.models.career_memory import CareerMemory, OpportunityEntry
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from aureon.services.foundation.journey_guidance import JourneyGuidance, JourneyGuidanceEngine


class OpportunityJourneyStage(StrEnum):
    CURRENT_STATE = "current_state"
    PREPARATION = "preparation"
    READY_TO_APPLY = "ready_to_apply"
    APPLICATION = "application"
    INTERVIEW = "interview"
    COMPLETION = "completion"


#: The real order a student can move through — used to compute
#: `reached_stages` (every stage up to and including the current one).
_STAGE_ORDER = [
    OpportunityJourneyStage.CURRENT_STATE,
    OpportunityJourneyStage.PREPARATION,
    OpportunityJourneyStage.READY_TO_APPLY,
    OpportunityJourneyStage.APPLICATION,
    OpportunityJourneyStage.INTERVIEW,
    OpportunityJourneyStage.COMPLETION,
]


class OpportunityJourney(BaseModel):
    current_stage: OpportunityJourneyStage
    #: Reused directly from Journey Guidance, never a second reasoning
    #: system — only populated when current_stage is PREPARATION.
    preparation_guidance: JourneyGuidance | None = None
    reached_stages: list[OpportunityJourneyStage]


def build_opportunity_journey(
    fit: OpportunityFitResult, interactions: list[OpportunityEntry], career_memory: CareerMemory
) -> OpportunityJourney:
    if any(entry.interaction == "completed" for entry in interactions):
        stage = OpportunityJourneyStage.COMPLETION
    elif any(entry.interaction == "applied" for entry in interactions):
        stage = OpportunityJourneyStage.APPLICATION
    elif fit.readiness_label == "ready":
        stage = OpportunityJourneyStage.READY_TO_APPLY
    else:
        stage = OpportunityJourneyStage.PREPARATION

    guidance = None
    if stage == OpportunityJourneyStage.PREPARATION:
        guidance = JourneyGuidanceEngine().guide(progress_report=None, career_memory=career_memory, opportunity_fit=fit)

    stage_index = _STAGE_ORDER.index(stage)
    reached = _STAGE_ORDER[: stage_index + 1]

    return OpportunityJourney(current_stage=stage, preparation_guidance=guidance, reached_stages=reached)
