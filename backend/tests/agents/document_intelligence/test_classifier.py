import pytest

from aureon.agents.document_intelligence.classifier import (
    DOCUMENT_CATEGORY_OWNER,
    classify_document,
)
from aureon.shared.types import AgentName

FILENAME_CASES = [
    ("Resume.pdf", "resume", AgentName.DISCOVERY.value),
    ("john_cv.pdf", "cv", AgentName.DISCOVERY.value),
    ("Transcript.pdf", "transcript", AgentName.DISCOVERY.value),
    ("marksheet_2024.pdf", "transcript", AgentName.DISCOVERY.value),
    ("Certificate_AWS.pdf", "certificate", AgentName.DISCOVERY.value),
    ("statement_of_purpose.pdf", "sop", AgentName.DISCOVERY.value),
    ("my_portfolio.pdf", "portfolio", AgentName.DISCOVERY.value),
    ("University_Brochure.pdf", "university_brochure", AgentName.INSTITUTION.value),
    ("admission_requirements.pdf", "admission_document", AgentName.INSTITUTION.value),
    ("cs_curriculum.pdf", "curriculum", AgentName.INSTITUTION.value),
    ("Research_Paper.pdf", "research_paper", AgentName.CAREER_INTELLIGENCE.value),
    ("industry_whitepaper.pdf", "whitepaper", AgentName.CAREER_INTELLIGENCE.value),
    ("industry_report_2024.pdf", "industry_report", AgentName.CAREER_INTELLIGENCE.value),
    ("faculty_profile.pdf", "faculty_profile", AgentName.MENTOR.value),
    ("publication_list.pdf", "publication", AgentName.MENTOR.value),
]


@pytest.mark.parametrize("filename,expected_category,expected_owner", FILENAME_CASES)
def test_classify_by_filename(filename, expected_category, expected_owner):
    result = classify_document(filename, first_page_text=None)

    assert result.category == expected_category
    assert result.owning_specialist == expected_owner
    assert result.matched_on == "filename"


def test_generic_filename_falls_back_to_content_resume():
    result = classify_document(
        "document.pdf",
        "EDUCATION: BSc Computer Science. EXPERIENCE: Intern. SKILLS: Python. PROJECTS: A, B.",
    )
    assert result.category == "resume"
    assert result.matched_on == "content"


def test_generic_filename_falls_back_to_content_research_paper():
    result = classify_document(
        "final.pdf",
        "Abstract: this paper... Introduction: ... Methodology: ... Results: ... Conclusion: ...",
    )
    assert result.category == "research_paper"
    assert result.matched_on == "content"


def test_certificate_override_beats_generic_overlap():
    result = classify_document("file.pdf", "This certificate is awarded to Jane Doe. Issued by Acme Corp.")
    assert result.category == "certificate"


def test_transcript_override_beats_brochure_semester_overlap():
    # "semester" alone appears in both Transcript and Brochure keyword
    # sets — CGPA/credits/grade must be the deciding signal, not semester.
    result = classify_document(
        "file.pdf", "Semester 4 results. CGPA: 8.9. Credits earned: 120. Grade: A.",
    )
    assert result.category == "transcript"


def test_generic_filename_with_no_extractable_text_defaults_to_resume():
    result = classify_document("document.pdf", first_page_text=None)

    assert result.category == "resume"
    assert result.matched_on == "default"


def test_every_category_has_exactly_one_owner():
    for category, owner in DOCUMENT_CATEGORY_OWNER.items():
        assert owner in {
            AgentName.DISCOVERY.value, AgentName.INSTITUTION.value,
            AgentName.CAREER_INTELLIGENCE.value, AgentName.MENTOR.value,
        }
