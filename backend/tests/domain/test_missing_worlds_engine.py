from datetime import datetime, timezone

from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.exposure import ExposureHistoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.missing_worlds_engine import analyze_missing_worlds

NOW = datetime.now(timezone.utc)


def _world(**overrides) -> CareerWorld:
    defaults = dict(
        id="world_space", name="Space", description="d", why_it_matters="w", global_importance="g",
        future_growth="f", related_industries=["space", "aerospace"],
    )
    defaults.update(overrides)
    return CareerWorld(**defaults)


def _career(**overrides) -> Career:
    defaults = dict(
        id="career_1", name="Aerospace Engineer", category="engineering", industry="aerospace",
        countries=["US"], one_liner="d", trait_tags=["space", "physics"],
        reality=CareerReality(
            daily_work="d", work_environment="w", collaboration_level="c", creativity_level="c",
            research_intensity="r", learning_curve="l", travel="t", remote_possibility="r",
            stress_factors="s", typical_challenges="t", misconceptions="m", long_term_growth="g",
            salary_ranges=[], required_education="e", required_skills=[], entrepreneurship_potential="p",
        ),
        future_lens=FutureLens(
            ai_impact="a", automation_risk="a", demand_2030="d", demand_2035="d", demand_2040="d",
            emerging_opportunities="e", skills_becoming_valuable=[], timeline_narrative="t",
        ),
    )
    defaults.update(overrides)
    return Career(**defaults)


def test_world_with_zero_signal_is_unexplored():
    profile = StudentProfile(student_id="s1")
    analysis = analyze_missing_worlds(profile, [_world()], [])

    assert analysis.explorations[0].level == "unexplored"
    assert analysis.explorations[0].match_count == 0


def test_interests_contribute_real_matches():
    profile = StudentProfile(student_id="s1", interests=["space exploration"])
    analysis = analyze_missing_worlds(profile, [_world()], [])

    assert analysis.explorations[0].match_count >= 1
    assert analysis.explorations[0].level == "partially_explored"


def test_three_matches_classify_as_explored():
    profile = StudentProfile(
        student_id="s1",
        interests=["space", "aerospace engineering", "rockets and space travel"],
    )
    analysis = analyze_missing_worlds(profile, [_world()], [])

    assert analysis.explorations[0].match_count >= 3
    assert analysis.explorations[0].level == "explored"


def test_career_exploration_history_resolves_through_career_catalog():
    profile = StudentProfile(student_id="s1")
    profile.career_exploration_history.append(
        CareerExplorationEvent(id="e1", career_id="career_1", interaction_type="opened", metadata={}, created_at=NOW)
    )
    careers = [_career(id="career_1", industry="aerospace")]
    analysis = analyze_missing_worlds(profile, [_world()], careers)

    assert analysis.explorations[0].match_count >= 1


def test_exposure_history_resolves_through_career_catalog():
    profile = StudentProfile(student_id="s1")
    profile.exposure_history.append(ExposureHistoryEntry(id="x1", career_id="career_1", shown_at=NOW, interaction="opened"))
    careers = [_career(id="career_1", industry="aerospace")]
    analysis = analyze_missing_worlds(profile, [_world()], careers)

    assert analysis.explorations[0].match_count >= 1


def test_shown_but_never_opened_exposure_entry_does_not_count():
    """A merely-shown (never clicked) Exposure Universe suggestion is not
    meaningful exposure — only an `opened` interaction should count,
    otherwise even a passive impression could eliminate a Missing World."""
    profile = StudentProfile(student_id="s1")
    profile.exposure_history.append(ExposureHistoryEntry(id="x1", career_id="career_1", shown_at=NOW, interaction="shown"))
    careers = [_career(id="career_1", industry="aerospace")]
    analysis = analyze_missing_worlds(profile, [_world()], careers)

    assert analysis.explorations[0].match_count == 0
    assert analysis.explorations[0].level == "unexplored"


def test_dismissed_exposure_entry_does_not_count():
    """Dismissing a suggestion is the student actively passing on it, not
    exploring it — it should not count as exposure either."""
    profile = StudentProfile(student_id="s1")
    profile.exposure_history.append(ExposureHistoryEntry(id="x1", career_id="career_1", shown_at=NOW, interaction="dismissed"))
    careers = [_career(id="career_1", industry="aerospace")]
    analysis = analyze_missing_worlds(profile, [_world()], careers)

    assert analysis.explorations[0].match_count == 0


def test_recommended_next_ranks_partial_before_unexplored():
    high_partial = _world(id="world_a", name="A World", related_industries=["alpha"])
    unexplored = _world(id="world_b", name="B World", related_industries=["beta"])
    profile = StudentProfile(student_id="s1", interests=["alpha domain interest"])

    analysis = analyze_missing_worlds(profile, [unexplored, high_partial], [])

    assert analysis.recommended_next[0].id == "world_a"


def test_recommended_next_is_capped_at_five():
    worlds = [_world(id=f"world_{i}", name=f"World {i}", related_industries=[f"tag{i}"]) for i in range(10)]
    profile = StudentProfile(student_id="s1")

    analysis = analyze_missing_worlds(profile, worlds, [])

    assert len(analysis.recommended_next) == 5
