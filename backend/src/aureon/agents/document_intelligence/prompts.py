from aureon.agents.document_intelligence.classifier import DocumentCategory
from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.services.llm.schemas import LLMMessage

_CATEGORY_FIELD_GUIDANCE: dict[DocumentCategory, str] = {
    "resume": "skills, experience, and education",
    "cv": "skills, experience, and education",
    "portfolio": "projects, skills, and demonstrated experience",
    "certificate": "what was awarded, by whom, and in what area",
    "transcript": "courses, grades, and academic performance",
    "sop": "goals, motivations, and fit for the stated direction",
    "university_brochure": "curriculum, facilities, and admission details",
    "admission_document": "curriculum, facilities, and admission details",
    "curriculum": "curriculum, facilities, and admission details",
    "research_paper": "topic, contribution, and applications",
    "whitepaper": "topic, contribution, and applications",
    "industry_report": "topic, contribution, and applications",
    "faculty_profile": "expertise and research focus",
    "publication": "expertise and research focus",
}


def build_document_investigation_messages(
    *, category: DocumentCategory, filename: str, raw_text: str
) -> list[LLMMessage]:
    field_guidance = _CATEGORY_FIELD_GUIDANCE.get(category, "the document's key content")
    system = (
        f"You are investigating a real document ({filename}, classified as {category}).\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "The text below was extracted directly from the real document — it is the ONLY source of "
        "truth you have. Never invent details that aren't present in it. If the extracted text is "
        f"too thin or unclear to responsibly extract {field_guidance}, set insufficient_content to "
        "true and explain why, rather than filling gaps with plausible-sounding guesses.\n\n"
        f"Extract findings relevant to: {field_guidance}. Always respond by calling the "
        "record_document_investigation tool."
    )
    context = f"Extracted document text:\n{raw_text}"
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="What did you find in this document?"),
    ]
