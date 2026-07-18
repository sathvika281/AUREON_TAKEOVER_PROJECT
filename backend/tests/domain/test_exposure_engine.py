from datetime import datetime, timezone

from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.models.exposure import ExposureHistoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.exposure_engine import select_exposure_careers
from tests.domain._explore_factories import make_career

NOW = datetime.now(timezone.utc)


def _signal(world: str, confidence: float) -> WorldSignal:
    return WorldSignal(world=world, confidence=confidence, evidence=[], status="curious", first_observed=NOW, last_reinforced=NOW)


def test_empty_profile_and_catalog_returns_empty():
    assert select_exposure_careers([], StudentProfile(student_id="s1")) == []


def test_excludes_already_visited_careers():
    profile = StudentProfile(student_id="s1")
    profile.career_exploration_history.append(
        CareerExplorationEvent(id="e1", career_id="visited", interaction_type="opened", created_at=NOW)
    )
    catalog = [make_career(id="visited"), make_career(id="unvisited")]

    result = select_exposure_careers(catalog, profile, limit=2)

    assert "visited" not in [c.id for c in result]
    assert "unvisited" in [c.id for c in result]


def test_excludes_already_surfaced_careers_no_repeats():
    profile = StudentProfile(student_id="s1")
    profile.exposure_history.append(
        ExposureHistoryEntry(id="x1", career_id="already_shown", shown_at=NOW, interaction="shown")
    )
    catalog = [make_career(id="already_shown"), make_career(id="fresh")]

    result = select_exposure_careers(catalog, profile, limit=2)

    assert [c.id for c in result] == ["fresh"]


def test_never_surfaces_a_high_alignment_career_over_a_low_alignment_one():
    """The core exposure guarantee — repeated across trials since
    selection includes real randomization within ties."""
    profile = StudentProfile(student_id="s1")
    profile.discovery_onboarding.world_signals = [_signal("AI", 0.9)]
    catalog = [
        make_career(id="aligned", industry="technology", category="emerging", name="AI Engineer"),
        make_career(id="unaligned_1", industry="healthcare", category="traditional", name="Nurse"),
        make_career(id="unaligned_2", industry="arts", category="traditional", name="Sculptor"),
    ]

    for _ in range(15):
        result = select_exposure_careers(catalog, profile, limit=2)
        assert "aligned" not in [c.id for c in result]


def test_respects_limit():
    profile = StudentProfile(student_id="s1")
    catalog = [make_career(id=f"c{i}") for i in range(5)]
    result = select_exposure_careers(catalog, profile, limit=2)
    assert len(result) == 2
