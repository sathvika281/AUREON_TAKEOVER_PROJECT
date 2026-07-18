from datetime import datetime, timezone

from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.services.world_signal_alignment import compute_tag_alignment

NOW = datetime.now(timezone.utc)


def _signal(world: str, confidence: float) -> WorldSignal:
    return WorldSignal(world=world, confidence=confidence, evidence=[], status="curious", first_observed=NOW, last_reinforced=NOW)


def test_no_tags_returns_zero():
    assert compute_tag_alignment([], [_signal("AI", 0.7)]) == 0.0


def test_no_signals_returns_zero():
    assert compute_tag_alignment(["technology"], []) == 0.0


def test_exact_case_insensitive_match_sums_confidence():
    assert compute_tag_alignment(["Healthcare"], [_signal("healthcare", 0.5)]) == 0.5


def test_substring_match_in_either_direction():
    # "aerospace" contains "space" as a real substring.
    assert compute_tag_alignment(["aerospace"], [_signal("Space", 0.6)]) == 0.6
    # "AI" is a substring of a longer tag too.
    assert compute_tag_alignment(["technology & AI"], [_signal("AI", 0.4)]) == 0.4


def test_no_real_overlap_returns_zero_never_fabricated():
    assert compute_tag_alignment(["finance"], [_signal("Psychology", 0.9)]) == 0.0


def test_multiple_matching_signals_sum():
    tags = ["healthcare & technology"]
    signals = [_signal("Healthcare", 0.5), _signal("Technology", 0.3)]
    assert compute_tag_alignment(tags, signals) == 0.8
