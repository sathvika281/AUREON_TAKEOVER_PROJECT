from dataclasses import dataclass
from typing import Literal

from aureon.shared.types import AgentName

DocumentCategory = Literal[
    "resume", "cv", "portfolio", "certificate", "transcript", "sop",
    "university_brochure", "admission_document", "curriculum",
    "research_paper", "whitepaper", "industry_report",
    "faculty_profile", "publication",
]

#: Every category has exactly one owner, with no fallback/default owner
#: across categories — unlike URL Intelligence (V6), there is no single
#: "front door" specialist here, so Document Intelligence's pipeline sets
#: Mission.primary_agent directly to whichever owner this table names,
#: with no delegation in the common path.
DOCUMENT_CATEGORY_OWNER: dict[DocumentCategory, str] = {
    "resume": AgentName.DISCOVERY.value,
    "cv": AgentName.DISCOVERY.value,
    "portfolio": AgentName.DISCOVERY.value,
    "certificate": AgentName.DISCOVERY.value,
    "transcript": AgentName.DISCOVERY.value,
    "sop": AgentName.DISCOVERY.value,
    "university_brochure": AgentName.INSTITUTION.value,
    "admission_document": AgentName.INSTITUTION.value,
    "curriculum": AgentName.INSTITUTION.value,
    "research_paper": AgentName.CAREER_INTELLIGENCE.value,
    "whitepaper": AgentName.CAREER_INTELLIGENCE.value,
    "industry_report": AgentName.CAREER_INTELLIGENCE.value,
    "faculty_profile": AgentName.MENTOR.value,
    "publication": AgentName.MENTOR.value,
}

MatchedOn = Literal["filename", "content", "default"]


@dataclass
class DocumentClassification:
    category: DocumentCategory
    owning_specialist: str
    matched_on: MatchedOn
    reason: str


#: Checked in this exact order against the filename — first match wins.
#: Ordered so the most specific/least ambiguous keywords are checked
#: before more generic ones (e.g. "faculty"/"publication" before the bare
#: "research" that also appears in "research paper").
_FILENAME_RULES: list[tuple[list[str], DocumentCategory]] = [
    (["faculty"], "faculty_profile"),
    (["publication"], "publication"),
    (["transcript", "marksheet"], "transcript"),
    (["certificate"], "certificate"),
    (["brochure"], "university_brochure"),
    (["admission"], "admission_document"),
    (["curriculum"], "curriculum"),
    (["whitepaper"], "whitepaper"),
    (["industry"], "industry_report"),
    (["research"], "research_paper"),
    (["sop", "statement_of_purpose", "statement of purpose"], "sop"),
    (["portfolio"], "portfolio"),
    (["resume"], "resume"),
    (["cv"], "cv"),
]

#: Content-keyword sets, used only when the filename is generic (e.g.
#: "document.pdf", "file.pdf", "final.pdf") and real text was extracted.
#: Never used to run an LLM classification — every check here is a plain
#: case-insensitive substring match.
_CONTENT_KEYWORDS: dict[DocumentCategory, list[str]] = {
    "resume": ["education", "experience", "skills", "projects"],
    "research_paper": ["abstract", "introduction", "methodology", "results", "conclusion"],
    "university_brochure": ["admissions", "curriculum", "semester", "departments", "faculty"],
    "certificate": ["certificate", "awarded to", "issued by"],
    "transcript": ["semester", "credits", "cgpa", "grade", "course"],
}

#: Distinctive keywords checked as an override before generic scoring, so
#: Transcript's real signal ("cgpa"/"credits"/"grade") always wins over
#: Brochure's overlapping "semester", and Certificate's real signal
#: ("awarded to"/"issued by") always wins over any partial overlap.
_CERTIFICATE_OVERRIDE_KEYWORDS = ["awarded to", "issued by"]
_TRANSCRIPT_OVERRIDE_KEYWORDS = ["cgpa", "credits", "grade"]

_CONTENT_CATEGORY_ORDER: list[DocumentCategory] = [
    "resume", "research_paper", "university_brochure", "certificate", "transcript",
]


def _classify_by_filename(filename: str) -> DocumentCategory | None:
    lowered = filename.lower()
    for keywords, category in _FILENAME_RULES:
        if any(kw in lowered for kw in keywords):
            return category
    return None


def _classify_by_content(first_page_text: str) -> DocumentCategory | None:
    lowered = first_page_text.lower()

    if any(kw in lowered for kw in _CERTIFICATE_OVERRIDE_KEYWORDS):
        return "certificate"
    if any(kw in lowered for kw in _TRANSCRIPT_OVERRIDE_KEYWORDS):
        return "transcript"

    scores = {
        category: sum(1 for kw in keywords if kw in lowered)
        for category, keywords in _CONTENT_KEYWORDS.items()
    }
    best_category = max(_CONTENT_CATEGORY_ORDER, key=lambda c: scores[c])
    if scores[best_category] == 0:
        return None
    return best_category


def classify_document(filename: str, first_page_text: str | None) -> DocumentClassification:
    """Deterministic, keyword-only — never an LLM call. Filename keywords
    are checked first (cheapest, most explicit signal); only when the
    filename doesn't match anything does real extracted first-page text
    get a second, still-deterministic pass. Defaults to `resume` under
    Discovery when neither signal matches, mirroring V6's
    unmatched-URL -> career_article default."""
    by_filename = _classify_by_filename(filename)
    if by_filename is not None:
        return DocumentClassification(
            category=by_filename,
            owning_specialist=DOCUMENT_CATEGORY_OWNER[by_filename],
            matched_on="filename",
            reason=f"Filename '{filename}' matched a keyword for '{by_filename}'.",
        )

    if first_page_text:
        by_content = _classify_by_content(first_page_text)
        if by_content is not None:
            return DocumentClassification(
                category=by_content,
                owning_specialist=DOCUMENT_CATEGORY_OWNER[by_content],
                matched_on="content",
                reason=f"Filename was generic; first-page text matched keywords for '{by_content}'.",
            )

    return DocumentClassification(
        category="resume",
        owning_specialist=DOCUMENT_CATEGORY_OWNER["resume"],
        matched_on="default",
        reason="No filename or content keywords matched — defaulted to a general personal document.",
    )
