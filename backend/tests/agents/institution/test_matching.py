from datetime import datetime, timezone

from aureon.agents.specialized.institution.matching import analyze_college_matches, upsert_college_matches
from aureon.agents.specialized.institution.schemas import CollegeMatchUpdate
from aureon.domain.models.institution import Institution
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

NOW = datetime.now(timezone.utc)

INSTITUTION = Institution(
    id="inst_1", name="Test University", country="Testland", city="Test City",
    research_culture="x", innovation_ecosystem="x", industry_collaboration="x",
    placements="x", learning_environment="x", trait_tags=["curiosity"],
)


async def test_analyze_college_matches_parses_output():
    args = {
        "reply_to_student": "x",
        "matches": [{"institution_id": "inst_1", "why_it_matches": "strong research culture fit", "supporting_evidence": ["enjoys research"], "confidence": 0.6}],
        "insufficient_evidence": False,
    }
    llm = FakeLLMClient([tool_call_response("record_college_matches", args)])
    profile = StudentProfile(student_id="s1")

    output = await analyze_college_matches(profile, [INSTITUTION], llm=llm)

    assert len(output.matches) == 1
    assert output.matches[0].institution_id == "inst_1"


def test_upsert_college_matches_creates_new_match_with_evidence():
    profile = StudentProfile(student_id="s1")
    update = CollegeMatchUpdate(
        institution_id="inst_1", why_it_matches="strong research culture",
        supporting_evidence=["enjoys research"], confidence=0.6,
    )

    upsert_college_matches(profile, [update], {"inst_1": "Test University"}, NOW)

    assert len(profile.college_matches) == 1
    supports = [e for e in profile.evidence_graph if e.related_institution == "inst_1" and e.relation == "supports"]
    assert len(supports) == 1


def test_college_match_absent_from_later_analysis_is_discarded_not_deleted():
    profile = StudentProfile(student_id="s1")
    update = CollegeMatchUpdate(institution_id="inst_1", why_it_matches="x", confidence=0.6)
    upsert_college_matches(profile, [update], {"inst_1": "Test University"}, NOW)

    upsert_college_matches(profile, [], {"inst_1": "Test University"}, NOW)

    assert len(profile.college_matches) == 1
    assert profile.college_matches[0].status == "discarded"
