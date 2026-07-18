"""Responsibility: Opportunity Hub's output shapes — the per-request
`OpportunityRecommendationsOutput` and the narrative LLM call's own
tool schema. Owns: `OpportunityRecommendation`,
`OpportunityRecommendationsOutput`, `OpportunityNarrative`,
`OpportunityNarrativeBatchOutput`, `OPPORTUNITY_NARRATIVE_TOOL`. Does
NOT own: any of the deterministic facts these shapes carry (scoring.py,
cost.py, journey.py). Consumed by: `agent.py`,
`build_orchestrator.py`'s `_extract_evidence`.

Same batched-narrative-tool shape as `mentor/schemas.py`'s
`MENTOR_MATCH_TOOL` — the LLM only ever narrates already-computed
facts (see prompts.py), never sees raw profile data, so it cannot
invent a requirement/skill/deadline/evidence item.
"""

from pydantic import BaseModel, Field

from aureon.agents.specialized.opportunity.journey import OpportunityJourney
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import OpportunityCost, OpportunityFitResult, PreparationInsight
from aureon.services.llm.schemas import LLMTool


class OpportunityRecommendation(BaseModel):
    """One fully-explained recommendation — the opportunity itself, its
    deterministic fit, the narrative layer on top of that fit, its
    structured preparation journey, and its informational cost."""

    opportunity: Opportunity
    fit: OpportunityFitResult
    preparation: PreparationInsight
    journey: OpportunityJourney
    cost: OpportunityCost


class OpportunityRecommendationsOutput(BaseModel):
    reply_to_student: str
    recommendations: list[OpportunityRecommendation] = Field(default_factory=list)
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


class OpportunityNarrative(BaseModel):
    opportunity_id: str
    why_recommended: str
    recommended_preparation: str


class OpportunityNarrativeBatchOutput(BaseModel):
    narratives: list[OpportunityNarrative] = Field(default_factory=list)


OPPORTUNITY_NARRATIVE_TOOL = LLMTool(
    name="record_opportunity_narratives",
    description=(
        "Record, for each opportunity given, one narrative entry (matched by opportunity_id) explaining "
        "why it was recommended and what to prepare — using ONLY the facts already provided in context. "
        "Never invent a requirement, skill, deadline, or evidence item not present in those facts."
    ),
    parameters=OpportunityNarrativeBatchOutput.model_json_schema(),
)
