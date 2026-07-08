from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.mentor_match import CollegeMatch, MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.decision_view import build_college_match_dtos, build_mentor_match_dtos


def test_mentor_match_dto_pulls_evidence_from_the_graph_and_shows_no_raw_number():
    profile = StudentProfile(student_id="s1")
    profile.mentor_matches.append(
        MentorMatch(id="1", mentor_id="mentor_1", mentor_name="Dr. Test", why_it_matches="x", confidence=0.75)
    )
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="shared curiosity", source="conversation", related_mentor="mentor_1", relation="supports")
    )

    dtos = build_mentor_match_dtos(profile)

    assert len(dtos) == 1
    assert dtos[0].supporting_evidence == ["shared curiosity"]
    assert dtos[0].evidence_strength == "Strong"
    assert not hasattr(dtos[0], "confidence")


def test_discarded_mentor_matches_are_excluded():
    profile = StudentProfile(student_id="s1")
    profile.mentor_matches.append(
        MentorMatch(id="1", mentor_id="mentor_1", mentor_name="Dr. Test", why_it_matches="x", confidence=0.3, status="discarded")
    )

    assert build_mentor_match_dtos(profile) == []


def test_college_match_dto_pulls_evidence_from_the_graph():
    profile = StudentProfile(student_id="s1")
    profile.college_matches.append(
        CollegeMatch(id="1", institution_id="inst_1", institution_name="Test University", why_it_matches="x", confidence=0.5)
    )
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="enjoys research culture", source="conversation", related_institution="inst_1", relation="supports")
    )

    dtos = build_college_match_dtos(profile)

    assert dtos[0].supporting_evidence == ["enjoys research culture"]
