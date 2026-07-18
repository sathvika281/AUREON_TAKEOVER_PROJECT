from aureon.domain.models.opportunity import Opportunity


def _base(**overrides) -> Opportunity:
    defaults: dict = dict(
        id="opp_1", title="Test Opportunity", category="internship", organization="Org",
        organization_kind="company", description="desc", location="Remote", is_remote=True,
        duration_label="8 weeks", official_link="https://example.com",
    )
    defaults.update(overrides)
    return Opportunity(**defaults)


def test_version_defaults_to_one():
    assert _base().version == 1


def test_version_can_be_set_explicitly_for_a_newer_row():
    assert _base(version=3).version == 3


def test_is_active_defaults_true():
    assert _base().is_active is True


def test_source_note_carries_honesty_disclaimer_by_default():
    assert "not a claim of a live" in _base().source_note


def test_min_academic_level_defaults_to_any():
    assert _base().min_academic_level == "any"


def test_countries_empty_means_open_to_all():
    assert _base().countries == []


def test_application_deadline_defaults_to_none_for_rolling_admissions():
    assert _base().application_deadline is None
