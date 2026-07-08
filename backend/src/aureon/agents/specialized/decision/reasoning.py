import uuid
from datetime import datetime

from aureon.agents.specialized.decision.comparison_facts import extract_comparison_facts
from aureon.agents.specialized.decision.prompts import (
    build_comparison_messages,
    build_parallel_universe_messages,
)
from aureon.agents.specialized.decision.schemas import (
    COMPARISON_TOOL,
    PARALLEL_UNIVERSE_TOOL,
    ComparisonTurnOutput,
    ParallelUniverseTurnOutput,
)
from aureon.domain.models.career import Career
from aureon.domain.models.career_comparison import (
    CareerComparison,
    ComparisonDimension,
    ParallelUniverseBranch,
    ParallelUniverseScenario,
)
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient


def _facts_by_id(careers: list[Career]) -> dict[str, dict[str, str]]:
    return {c.id: extract_comparison_facts(c) for c in careers}


async def analyze_comparison(
    profile: StudentProfile, careers: list[Career], *, llm: LLMClient
) -> ComparisonTurnOutput:
    """The single reasoning entry point for Decision Lab comparisons —
    called both by the conversational agent and the direct API route.
    Decision's own capability — comparison/trade-off reasoning is never
    delegated, it's the one thing this agent genuinely owns."""
    messages = build_comparison_messages(
        career_dna=profile.career_dna,
        evidence_graph=profile.evidence_graph,
        career_candidates=profile.career_candidates,
        careers=careers,
        facts_by_id=_facts_by_id(careers),
    )
    response = await llm.complete(messages, tools=[COMPARISON_TOOL], tool_choice="required")
    if not response.tool_calls:
        return ComparisonTurnOutput(
            reply_to_student=response.content or "Let's gather more evidence before comparing these.",
            summary_reason="Comparison could not be completed this time.",
        )
    return ComparisonTurnOutput.model_validate(response.tool_calls[0].arguments)


async def analyze_parallel_universe(
    profile: StudentProfile, careers: list[Career], *, llm: LLMClient
) -> ParallelUniverseTurnOutput:
    """The single reasoning entry point for Parallel Universe — shares
    the same context-building and career-facts backbone as
    analyze_comparison, just a different output shape (narrative per
    career vs. a dimension matrix)."""
    messages = build_parallel_universe_messages(
        career_dna=profile.career_dna,
        evidence_graph=profile.evidence_graph,
        career_candidates=profile.career_candidates,
        careers=careers,
        facts_by_id=_facts_by_id(careers),
    )
    response = await llm.complete(messages, tools=[PARALLEL_UNIVERSE_TOOL], tool_choice="required")
    if not response.tool_calls:
        return ParallelUniverseTurnOutput(
            reply_to_student=response.content or "Let's gather more evidence before simulating this."
        )
    return ParallelUniverseTurnOutput.model_validate(response.tool_calls[0].arguments)


def finalize_comparison(
    career_ids: list[str],
    careers: list[Career],
    output: ComparisonTurnOutput,
    now: datetime,
) -> CareerComparison:
    """Merges a comparison's *facts* (always deterministic, read straight
    from the Career Knowledge Base) with the LLM's per-dimension
    reasoning, into one persisted CareerComparison. Shared by both
    DecisionAgent.run() and the direct API route so this merge logic
    lives in exactly one place."""
    career_names = {c.id: c.name for c in careers}
    facts_by_id = _facts_by_id(careers)
    reasoning_by_dimension = {r.dimension: r.why_it_matters_to_you for r in output.dimension_reasoning}
    dimension_keys = next(iter(facts_by_id.values()), {}).keys()

    dimensions = [
        ComparisonDimension(
            dimension=dim,
            per_career={cid: facts_by_id[cid][dim] for cid in career_ids if cid in facts_by_id},
            why_it_matters_to_you=reasoning_by_dimension.get(
                dim, "No specific personalization available for this dimension yet."
            ),
        )
        for dim in dimension_keys
    ]

    return CareerComparison(
        id=str(uuid.uuid4()),
        career_ids=career_ids,
        career_names=career_names,
        dimensions=dimensions,
        summary_reason=output.summary_reason,
        missing_evidence=output.missing_evidence,
        created_at=now,
    )


def finalize_parallel_universe(
    output: ParallelUniverseTurnOutput,
    career_names: dict[str, str],
    now: datetime,
) -> ParallelUniverseScenario:
    """Same purpose as finalize_comparison, for Parallel Universe."""
    branches = [
        ParallelUniverseBranch(
            career_id=b.career_id,
            career_name=career_names.get(b.career_id, b.career_id),
            daily_work=b.daily_work,
            lifestyle=b.lifestyle,
            growth=b.growth,
            challenges=b.challenges,
            future_opportunities=b.future_opportunities,
        )
        for b in output.branches
    ]
    return ParallelUniverseScenario(
        id=str(uuid.uuid4()),
        branches=branches,
        missing_evidence=output.missing_evidence,
        created_at=now,
    )
