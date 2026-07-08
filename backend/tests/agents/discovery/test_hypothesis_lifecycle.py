from aureon.agents.specialized.discovery.hypothesis_lifecycle import compute_status


def test_low_confidence_is_investigating():
    assert compute_status(confidence=0.1, mode="exploration", is_top_hypothesis=False) == "investigating"


def test_mid_confidence_is_growing():
    assert compute_status(confidence=0.45, mode="exploration", is_top_hypothesis=False) == "growing"


def test_high_confidence_is_strong():
    assert compute_status(confidence=0.8, mode="exploration", is_top_hypothesis=True) == "strong"


def test_recommendation_mode_validates_only_the_top_hypothesis():
    assert compute_status(confidence=0.9, mode="recommendation", is_top_hypothesis=True) == "validated"
    # Not the leading hypothesis -> still just reflects its own confidence tier.
    assert compute_status(confidence=0.9, mode="recommendation", is_top_hypothesis=False) == "strong"
