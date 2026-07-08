from datetime import datetime, timezone

from aureon.agents.specialized.mentor.matching import analyze_mentor_matches, upsert_mentor_matches
from aureon.agents.specialized.mentor.schemas import MentorMatchUpdate
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

NOW = datetime.now(timezone.utc)

MENTOR = Mentor(
    id="mentor_1", name="Dr. Test Mentor", role_type="professor", field="AI",
    bio="x", trait_tags=["curiosity"], learning_style_fit="x",
)


async def test_analyze_mentor_matches_parses_output():
    args = {
        "reply_to_student": "x",
        "matches": [{"mentor_id": "mentor_1", "why_it_matches": "shared curiosity about AI", "supporting_evidence": ["loves research"], "confidence": 0.6}],
        "insufficient_evidence": False,
    }
    llm = FakeLLMClient([tool_call_response("record_mentor_matches", args)])
    profile = StudentProfile(student_id="s1")

    output = await analyze_mentor_matches(profile, [MENTOR], llm=llm)

    assert len(output.matches) == 1
    assert output.matches[0].mentor_id == "mentor_1"


def test_upsert_mentor_matches_creates_new_match_with_evidence():
    profile = StudentProfile(student_id="s1")
    update = MentorMatchUpdate(
        mentor_id="mentor_1", why_it_matches="shared curiosity",
        supporting_evidence=["loves research"], confidence=0.6,
    )

    upsert_mentor_matches(profile, [update], {"mentor_1": "Dr. Test"}, NOW)

    assert len(profile.mentor_matches) == 1
    assert profile.mentor_matches[0].mentor_name == "Dr. Test"
    supports = [e for e in profile.evidence_graph if e.related_mentor == "mentor_1" and e.relation == "supports"]
    assert len(supports) == 1


def test_mentor_match_absent_from_later_analysis_is_discarded_not_deleted():
    profile = StudentProfile(student_id="s1")
    update = MentorMatchUpdate(mentor_id="mentor_1", why_it_matches="x", confidence=0.6)
    upsert_mentor_matches(profile, [update], {"mentor_1": "Dr. Test"}, NOW)
    assert profile.mentor_matches[0].status == "active"

    later = NOW
    upsert_mentor_matches(profile, [], {"mentor_1": "Dr. Test"}, later)

    assert len(profile.mentor_matches) == 1  # kept, not deleted
    assert profile.mentor_matches[0].status == "discarded"
    assert profile.mentor_matches[0].transition_reason is not None
