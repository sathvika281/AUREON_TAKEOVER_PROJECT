from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.profile_view import build_career_candidate_dtos, build_hypothesis_dtos


def test_hypothesis_dto_pulls_evidence_from_the_graph_not_a_stored_field():
    profile = StudentProfile(student_id="s1")
    profile.career_hypotheses.append(
        CareerHypothesis(career_name="AI Research", confidence=0.4, status="growing")
    )
    profile.evidence_graph.extend(
        [
            EvidenceRecord(
                id="1", text="enjoys research", source="conversation",
                related_hypothesis="AI Research", relation="supports",
            ),
            EvidenceRecord(
                id="2", text="dislikes working alone", source="conversation",
                related_hypothesis="AI Research", relation="contradicts",
            ),
        ]
    )

    dtos = build_hypothesis_dtos(profile)

    assert len(dtos) == 1
    assert dtos[0].supporting_evidence == ["enjoys research"]
    assert dtos[0].contradicting_evidence == ["dislikes working alone"]


def test_discarded_hypotheses_are_excluded_from_the_dto_list():
    profile = StudentProfile(student_id="s1")
    profile.career_hypotheses.append(
        CareerHypothesis(career_name="Old Idea", confidence=0.1, status="discarded")
    )

    assert build_hypothesis_dtos(profile) == []


def test_career_candidate_dto_pulls_evidence_from_the_graph_and_shows_no_raw_number():
    profile = StudentProfile(student_id="s1")
    profile.career_candidates.append(
        CareerCandidate(
            id="c1", career_id="ai_research_scientist", career_name="AI Research Scientist",
            why_it_matches="Loves open-ended investigation", confidence=0.75,
        )
    )
    profile.evidence_graph.extend(
        [
            EvidenceRecord(
                id="1", text="loves open-ended research", source="conversation",
                related_career="ai_research_scientist", relation="supports",
            ),
            EvidenceRecord(
                id="2", text="dislikes long isolated stretches", source="conversation",
                related_career="ai_research_scientist", relation="contradicts",
            ),
        ]
    )

    dtos = build_career_candidate_dtos(profile)

    assert len(dtos) == 1
    assert dtos[0].supporting_evidence == ["loves open-ended research"]
    assert dtos[0].contradicting_evidence == ["dislikes long isolated stretches"]
    assert dtos[0].evidence_strength == "Strong"
    assert not hasattr(dtos[0], "confidence")


def test_discarded_career_candidates_are_excluded_from_the_dto_list():
    profile = StudentProfile(student_id="s1")
    profile.career_candidates.append(
        CareerCandidate(
            id="c1", career_id="old_idea", career_name="Old Idea",
            why_it_matches="x", confidence=0.3, status="discarded",
        )
    )

    assert build_career_candidate_dtos(profile) == []
