from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.orbit_status import (
    ORBIT_GUIDANCE,
    build_orbit_explanation,
    get_orbit_status,
)


def test_orbit_guidance_covers_every_real_understanding_stage():
    assert set(ORBIT_GUIDANCE.keys()) == {
        "Seed", "Explorer", "Patterns Emerging", "Identity Taking Shape",
        "Career DNA Forming", "Decision Ready",
    }


def test_orbit_guidance_never_compares_the_student_to_other_students():
    for guidance in ORBIT_GUIDANCE.values():
        assert "other student" not in guidance.message.lower()
        assert "than other" not in guidance.message.lower()


def test_orbit_guidance_never_names_a_career_or_college():
    """Discover only ever answers 'who am I?' — Orbit Status stays
    self-understanding-framed, never a recommendation."""
    forbidden = ("engineer", "doctor", "college", "university", "career:")
    for guidance in ORBIT_GUIDANCE.values():
        combined = " ".join([guidance.message, *guidance.focus, *guidance.avoid]).lower()
        for word in forbidden:
            assert word not in combined


def test_build_orbit_explanation_zero_evidence_case_is_honest():
    explanation = build_orbit_explanation(0, 0)
    assert "just getting started" in explanation


def test_build_orbit_explanation_notebook_entries_but_no_hypotheses():
    explanation = build_orbit_explanation(3, 0)
    assert "3 real observations" in explanation
    assert "nothing has" in explanation


def test_build_orbit_explanation_singular_grammar():
    explanation = build_orbit_explanation(1, 0)
    assert "1 real observation so far" in explanation  # singular, not "observations"


def test_build_orbit_explanation_grounded_case_cites_both_real_counts():
    explanation = build_orbit_explanation(5, 2)
    assert "5 observations" in explanation
    assert "2 early directions" in explanation


def test_get_orbit_status_returns_the_real_matching_guidance():
    profile = StudentProfile(student_id="s1")
    status = get_orbit_status(profile, mode="exploration")

    assert status.current_orbit in ORBIT_GUIDANCE
    expected = ORBIT_GUIDANCE[status.current_orbit]
    assert status.focus == expected.focus
    assert status.avoid == expected.avoid
    assert status.message == expected.message


def test_get_orbit_status_confidence_is_the_real_profile_confidence_not_a_new_metric():
    profile = StudentProfile(student_id="s1", confidence_score=0.42)
    status = get_orbit_status(profile, mode="exploration")
    assert status.confidence == 0.42


def test_get_orbit_status_explanation_reflects_real_counts():
    from aureon.domain.models.notebook import NotebookEntry

    profile = StudentProfile(student_id="s1")
    profile.notebook_entries.append(
        NotebookEntry(id="n1", kind="observation", text="x", source="conversation")
    )
    status = get_orbit_status(profile, mode="exploration")
    assert "1 real observation" in status.explanation
