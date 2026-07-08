from aureon.domain.models.mentor_match import CollegeMatch, MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.match_recommendations import (
    top_active_institution_names,
    top_active_mentor_names,
)


def _profile() -> StudentProfile:
    return StudentProfile(student_id="s1")


def test_top_active_mentor_names_excludes_discarded_and_caps_at_limit():
    profile = _profile()
    profile.mentor_matches = [
        MentorMatch(id="m1", mentor_id="a", mentor_name="Strong Match", why_it_matches="x", confidence=0.9),
        MentorMatch(id="m2", mentor_id="b", mentor_name="Discarded Match", why_it_matches="x", confidence=0.99, status="discarded"),
        MentorMatch(id="m3", mentor_id="c", mentor_name="Weaker Match", why_it_matches="x", confidence=0.5),
        MentorMatch(id="m4", mentor_id="d", mentor_name="Weakest Match", why_it_matches="x", confidence=0.3),
    ]

    names = top_active_mentor_names(profile)

    assert names == ["Strong Match", "Weaker Match"]
    assert "Discarded Match" not in names


def test_top_active_institution_names_without_partner_filter():
    profile = _profile()
    profile.college_matches = [
        CollegeMatch(id="c1", institution_id="i1", institution_name="Institution A", why_it_matches="x", confidence=0.8),
    ]

    names = top_active_institution_names(profile)

    assert names == ["Institution A"]


def test_top_active_institution_names_only_surfaces_real_partners_when_filtered():
    profile = _profile()
    profile.college_matches = [
        CollegeMatch(id="c1", institution_id="partner-1", institution_name="Partner College", why_it_matches="x", confidence=0.7),
        CollegeMatch(id="c2", institution_id="non-partner-1", institution_name="Non-Partner College", why_it_matches="x", confidence=0.95),
    ]

    names = top_active_institution_names(profile, partner_ids={"partner-1"})

    assert names == ["Partner College"]
    assert "Non-Partner College" not in names
