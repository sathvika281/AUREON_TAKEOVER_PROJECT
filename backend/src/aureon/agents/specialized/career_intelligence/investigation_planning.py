from pydantic import BaseModel

from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.services.llm.base import LLMClient
from aureon.services.llm.schemas import LLMMessage, LLMTool


class InvestigationPlan(BaseModel):
    """The only output of Investigation Planning — three source-specific
    search queries and a one-line rationale. This never touches facts; it
    only decides search terms from the student's real question."""

    wikipedia_query: str
    arxiv_query: str
    semantic_scholar_query: str
    rationale: str


PLAN_INVESTIGATION_TOOL = LLMTool(
    name="record_investigation_plan",
    description="Record the search queries to run against Wikipedia, arXiv, and Semantic Scholar for a student's career question.",
    parameters=InvestigationPlan.model_json_schema(),
)


def _fallback_plan(question: str) -> InvestigationPlan:
    """A planning-call failure must never block the investigation — falls
    back to the raw question as every source's query rather than
    guessing at a 'smarter' rewrite."""
    return InvestigationPlan(
        wikipedia_query=question,
        arxiv_query=question,
        semantic_scholar_query=question,
        rationale="Used the question as-is; the planning step could not run this time.",
    )


def build_investigation_planning_messages(
    *, question: str, known_candidates: list[str]
) -> list[LLMMessage]:
    candidates_line = (
        f"The student is currently considering: {', '.join(known_candidates)}."
        if known_candidates
        else "The student has no tracked career candidates yet."
    )
    system = (
        "You are Aureon's Career Intelligence Agent, planning a real multi-source investigation "
        "of a student's career question.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "You have three real, trusted sources available: Wikipedia (general/encyclopedic "
        "overview), arXiv (research papers), and Semantic Scholar (academic paper search). "
        "Write one focused search query for each source, tailored to what that source is good "
        "at — Wikipedia queries should be broad/encyclopedic, arXiv/Semantic Scholar queries "
        "should use academic/technical phrasing. Do not invent facts about the question itself; "
        "only decide what to search for.\n\n"
        f"{candidates_line}\n\n"
        "Always respond by calling the record_investigation_plan tool."
    )
    return [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user", content=f"The student's question: {question}"),
    ]


async def plan_investigation(
    question: str, *, known_candidates: list[str], llm: LLMClient
) -> InvestigationPlan:
    messages = build_investigation_planning_messages(question=question, known_candidates=known_candidates)
    try:
        response = await llm.complete(messages, tools=[PLAN_INVESTIGATION_TOOL], tool_choice="required")
    except Exception:  # noqa: BLE001 — a provider-side error must never block the investigation
        return _fallback_plan(question)

    if not response.tool_calls:
        return _fallback_plan(question)

    try:
        return InvestigationPlan.model_validate(response.tool_calls[0].arguments)
    except Exception:  # noqa: BLE001 — malformed arguments from the model are never trusted blindly
        return _fallback_plan(question)
