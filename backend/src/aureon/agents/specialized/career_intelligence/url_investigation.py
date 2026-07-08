from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.agents.specialized.career_intelligence.url_classifier import UrlCategory
from aureon.agents.tools.base import Evidence
from aureon.services.llm.base import LLMClient
from aureon.services.llm.schemas import LLMMessage, LLMTool

#: A short extraction is very likely a paywall/JS-rendered shell, not a
#: real signal of low-quality content — the ceiling reflects "how much
#: real text did we actually get," never the LLM's own self-assessment.
_CONFIDENCE_FLOOR_CHARS = 200
_CONFIDENCE_CEILING_CHARS = 3000


def _extraction_confidence(raw_text_length: int) -> float:
    """Deterministic ceiling from real extracted-text length — the same
    'never trust the model's own confidence number' discipline as
    career_intelligence/confidence.py."""
    if raw_text_length < _CONFIDENCE_FLOOR_CHARS:
        return 0.1
    if raw_text_length >= _CONFIDENCE_CEILING_CHARS:
        return 0.9
    span = _CONFIDENCE_CEILING_CHARS - _CONFIDENCE_FLOOR_CHARS
    return round(0.1 + 0.8 * (raw_text_length - _CONFIDENCE_FLOOR_CHARS) / span, 2)


_CATEGORY_FIELD_GUIDANCE: dict[UrlCategory, str] = {
    "career_article": "career insights, required skills, challenges, future trends",
    "medium_article": "career insights, required skills, challenges, future trends",
    "youtube_video": "career insights, required skills, challenges, future trends",
    "github_repository": "languages used, project purpose, complexity, technologies",
    "portfolio_website": "projects, skills, experience, achievements",
    "university_page": "curriculum, research, facilities, admission",
    "research_paper": "topic, contribution, applications, future directions",
    "linkedin_profile": "professional background, expertise areas, career trajectory",
}


class UrlInvestigationTurnOutput(BaseModel):
    """Structured contract for one URL investigation. The raw text is
    already real (extracted deterministically by html_extraction.py) —
    this call only organizes/summarizes what's actually present in it,
    never invents anything beyond it."""

    title: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    structured_fields: dict[str, str] = Field(default_factory=dict)
    insufficient_content: bool = False
    insufficient_content_reason: str | None = None


URL_INVESTIGATION_TOOL = LLMTool(
    name="record_url_investigation",
    description="Record structured findings extracted from a real webpage's content — never invent beyond what's given.",
    parameters=UrlInvestigationTurnOutput.model_json_schema(),
)


def build_url_investigation_messages(
    *, category: UrlCategory, raw_text: str, url: str
) -> list[LLMMessage]:
    field_guidance = _CATEGORY_FIELD_GUIDANCE.get(category, "career insights, required skills, challenges, future trends")
    system = (
        f"You are Aureon's Career Intelligence Agent, investigating a real webpage ({url}, "
        f"classified as {category}).\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "The text below was extracted directly from the real page — it is the ONLY source of "
        "truth you have. Never invent details that aren't present in it. If the extracted text "
        f"is too thin or unclear to responsibly extract {field_guidance}, set insufficient_content "
        "to true and explain why, rather than filling gaps with plausible-sounding guesses.\n\n"
        f"Extract findings relevant to: {field_guidance}. Always respond by calling the "
        "record_url_investigation tool."
    )
    context = f"Extracted page text:\n{raw_text}"
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="What did you find on this page?"),
    ]


async def analyze_url_content(
    *, category: UrlCategory, raw_text: str, url: str, llm: LLMClient
) -> UrlInvestigationTurnOutput:
    messages = build_url_investigation_messages(category=category, raw_text=raw_text, url=url)
    response = await llm.complete(messages, tools=[URL_INVESTIGATION_TOOL], tool_choice="required")
    if not response.tool_calls:
        return UrlInvestigationTurnOutput(
            title=url,
            summary=response.content or "Could not extract structured findings from this page.",
            insufficient_content=True,
            insufficient_content_reason="Investigation could not be completed this time.",
        )
    return UrlInvestigationTurnOutput.model_validate(response.tool_calls[0].arguments)


def finalize_url_evidence(
    *, category: UrlCategory, url: str, raw_text: str, output: UrlInvestigationTurnOutput
) -> Evidence:
    """Merges the deterministic confidence ceiling (from real extracted
    text length) with the LLM's narrative into one Evidence record —
    same facts-vs-reasoning merge pattern as finalize_comparison."""
    return Evidence(
        source=url,
        source_type=f"url:{category}",
        title=output.title,
        summary=output.summary,
        confidence=_extraction_confidence(len(raw_text)),
        metadata={
            "category": category,
            "key_findings": output.key_findings,
            "structured_fields": output.structured_fields,
            "insufficient_content": output.insufficient_content,
            "insufficient_content_reason": output.insufficient_content_reason,
        },
        timestamp=datetime.now(timezone.utc),
    )
