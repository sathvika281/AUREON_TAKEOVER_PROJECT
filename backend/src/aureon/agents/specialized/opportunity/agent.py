"""OpportunityAgent — Aureon's intelligence layer for opportunities,
not a job board. Owns: `find_opportunities` (batch discovery/ranking)
and `evaluate_fit` (single-opportunity deterministic scoring), both
real reasoning entry points reached only through `BuildOrchestrator`
(see `agents/foundation/opportunity_objective_plans.py`) — never
bypassed. `run()` stays the honest no-op conversational-graph
passthrough it always was; this agent's real trigger is Build
Orchestrator objectives, same as Mentor/Institution/Growth.

Reads only Career Memory's own Evidence/Growth/Identity/Opportunities
domains (via `get_career_memory_snapshot`) — never reaches into
Network/Portfolio/Interview/Skill-Evolution/Career-Readiness/
Project-Lab, all of which remain untouched stubs from Stage 1/other
future Phase 2 modules.
"""

from datetime import datetime, timezone

from aureon.agents.base import BaseAgent
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.opportunity.cost import derive_opportunity_cost
from aureon.agents.specialized.opportunity.filtering import OpportunityFilters, apply_filters
from aureon.agents.specialized.opportunity.journey import build_opportunity_journey
from aureon.agents.specialized.opportunity.prompts import build_opportunity_narrative_messages
from aureon.agents.specialized.opportunity.schemas import (
    OPPORTUNITY_NARRATIVE_TOOL,
    OpportunityNarrativeBatchOutput,
    OpportunityRecommendation,
    OpportunityRecommendationsOutput,
)
from aureon.agents.specialized.opportunity.scoring import explain_ranking, score_opportunity
from aureon.agents.specialized.opportunity.scoring_config import RANKING_TIE_ROUNDING
from aureon.agents.specialized.opportunity.search import keyword_semantic_search
from aureon.agents.specialized.opportunity.tools import (
    CompetitionSearchTool,
    InternshipSearchTool,
    OpportunitySearchTool,
    ResearchOpportunitySearchTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import OpportunityFitResult, PreparationInsight
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.foundation.career_memory.service import (
    get_career_memory_snapshot,
    get_opportunity_interactions,
    record_opportunity_score,
)
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class OpportunityAgent(BaseAgent):
    """Surfaces internships, scholarships, competitions, research
    programs, and other real-world opportunities connected to the
    student's Career DNA, ranked by transparent multi-factor fit (see
    `scoring.py`)."""

    name = AgentName.OPPORTUNITY.value
    description = (
        "Surfaces internships, scholarships, competitions, research programs, and jobs "
        "connected to the student's Career DNA."
    )

    async def find_opportunities(
        self,
        profile: StudentProfile,
        opportunities: list[Opportunity],
        *,
        filters: OpportunityFilters | None = None,
        query: str | None = None,
        llm: LLMClient,
        mission: Mission | None = None,
        top_n: int = 5,
    ) -> OpportunityRecommendationsOutput:
        """Fetch (already loaded via the objective plan's `load_resources`,
        through `providers.fetch_all_safely`) -> filter -> optional search
        -> score every candidate -> rank with the long-term-trajectory
        tie-break -> narrate the top N in one batched LLM call -> attach
        each one's real preparation journey and informational cost."""
        stages = AGENT_EXECUTION_STAGES[self.name]
        now = datetime.now(timezone.utc)
        career_memory = get_career_memory_snapshot(profile)
        opportunities_by_id = {o.id: o for o in opportunities}

        candidates = [o for o in opportunities if o.is_active]
        if filters is not None:
            candidates = apply_filters(candidates, filters)
        if query:
            candidates = keyword_semantic_search(candidates, query)
        if mission is not None:
            mission.record_stage(stages[0])  # "Searching Opportunities"
            mission.record_stage(stages[1])  # "Filtering Expired Results"

        if not candidates:
            return OpportunityRecommendationsOutput(
                reply_to_student="No opportunities currently match your filters/search.",
                insufficient_evidence=True,
                insufficient_evidence_reason="No candidate opportunities remained after filtering/search.",
            )

        score_history = profile.foundation_memory.opportunities.score_history
        fits = [
            score_opportunity(profile, career_memory, o, now=now, previous_score=score_history.get(o.id))
            for o in candidates
        ]
        for fit in fits:
            record_opportunity_score(profile, opportunity_id=fit.opportunity_id, score=fit.overall_score)

        # Long-term-trajectory tie-break: opportunities with a close
        # overall_score are sorted by their real career_alignment +
        # career_goal_alignment strength, not just raw overall_score.
        def _sort_key(fit: OpportunityFitResult) -> tuple[float, float]:
            factor_by_key = {f.key: f.score for f in fit.factors}
            trajectory = factor_by_key.get("career_alignment", 0.0) + factor_by_key.get("career_goal_alignment", 0.0)
            return (-round(fit.overall_score, RANKING_TIE_ROUNDING), -trajectory)

        fits.sort(key=_sort_key)

        title_by_id = {o.id: o.title for o in candidates}
        by_category: dict[str, list[OpportunityFitResult]] = {}
        for fit in fits:
            by_category.setdefault(opportunities_by_id[fit.opportunity_id].category, []).append(fit)
        for rank, fit in enumerate(fits, start=1):
            fit.rank = rank
            same_category = by_category[opportunities_by_id[fit.opportunity_id].category]
            fit.ranking_rationale = explain_ranking(fit, same_category, title_by_id)
        if mission is not None:
            mission.record_stage(stages[2])  # "Ranking Opportunities"

        top_fits = fits[:top_n]
        narratives_by_id = await self._narrate(top_fits, opportunities_by_id, llm)

        other_tracked = [
            (entry, opportunities_by_id[entry.ref_id])
            for entry in career_memory.opportunities.entries
            if entry.ref_id is not None and entry.ref_id in opportunities_by_id
        ]

        recommendations: list[OpportunityRecommendation] = []
        for fit in top_fits:
            opportunity = opportunities_by_id[fit.opportunity_id]
            interactions = get_opportunity_interactions(profile, opportunity.id)
            journey = build_opportunity_journey(fit, interactions, career_memory)
            cost = derive_opportunity_cost(opportunity, fit, other_tracked)
            recommendations.append(
                OpportunityRecommendation(
                    opportunity=opportunity, fit=fit,
                    preparation=narratives_by_id[opportunity.id], journey=journey, cost=cost,
                )
            )

        return OpportunityRecommendationsOutput(
            reply_to_student=f"Found {len(recommendations)} opportunities worth your attention.",
            recommendations=recommendations,
        )

    async def _narrate(
        self,
        fits: list[OpportunityFitResult],
        opportunities_by_id: dict[str, Opportunity],
        llm: LLMClient,
    ) -> dict[str, PreparationInsight]:
        """One batched LLM call narrating already-computed facts —
        skipped entirely when there's nothing to narrate ('no LLM call
        for an evidence base this thin')."""
        fallback = {
            fit.opportunity_id: PreparationInsight(
                why_recommended=fit.factors[0].rationale if fit.factors else "Matched your profile.",
                recommended_preparation=(
                    fit.highest_impact_gap.recommended_action if fit.highest_impact_gap else "Keep building real evidence."
                ),
            )
            for fit in fits
        }
        if not fits:
            return fallback

        messages = build_opportunity_narrative_messages(
            [(opportunities_by_id[fit.opportunity_id], fit) for fit in fits]
        )
        response = await llm.complete(messages, tools=[OPPORTUNITY_NARRATIVE_TOOL], tool_choice="required")
        if not response.tool_calls:
            return fallback

        output = OpportunityNarrativeBatchOutput.model_validate(response.tool_calls[0].arguments)
        narrated = {
            n.opportunity_id: PreparationInsight(
                why_recommended=n.why_recommended, recommended_preparation=n.recommended_preparation
            )
            for n in output.narratives
        }
        # Any opportunity the model didn't cover keeps its deterministic fallback.
        return {**fallback, **narrated}

    async def evaluate_fit(
        self, profile: StudentProfile, opportunity: Opportunity, *, mission: Mission | None = None
    ) -> OpportunityFitResult:
        """Single-opportunity, 100% deterministic, no LLM call — used by
        the `opportunity_fit_evaluation` objective."""
        career_memory = get_career_memory_snapshot(profile)
        previous_score = profile.foundation_memory.opportunities.score_history.get(opportunity.id)
        fit = score_opportunity(
            profile, career_memory, opportunity, now=datetime.now(timezone.utc), previous_score=previous_score
        )
        record_opportunity_score(profile, opportunity_id=opportunity.id, score=fit.overall_score)
        if mission is not None:
            stages = AGENT_EXECUTION_STAGES[self.name]
            mission.record_stage(stages[2])  # "Ranking Opportunities" — the closest real analogue for a single-item evaluation
        return fit

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough for the conversational graph loop —
        # Opportunity Hub's real trigger is Build Orchestrator objectives
        # (find_opportunities/evaluate_fit above), not this graph node.
        stages = AGENT_EXECUTION_STAGES[self.name]
        tool_results = [
            await run_tool_safely(OpportunitySearchTool()),
            await run_tool_safely(InternshipSearchTool()),
            await run_tool_safely(ResearchOpportunitySearchTool()),
            await run_tool_safely(CompetitionSearchTool()),
        ]
        executed_stages = list(stages)

        state["agent_outputs"][self.name] = AgentOutput(
            agent_name=self.name,
            payload={
                "execution_stages": executed_stages,
                "tool_results": [r.model_dump() for r in tool_results],
            },
        )
        state["agent_history"].append(self.name)
        return state
