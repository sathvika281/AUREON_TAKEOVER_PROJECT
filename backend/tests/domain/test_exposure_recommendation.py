from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.exposure_recommendation import (
    build_exposure_enrichment,
    curiosity_hook_for,
    get_exposure_suggestions,
    record_exposure_interaction,
)
from tests.domain._explore_factories import make_career

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults: dict = dict(
        id="exp_1", title="Test Experiment", category="reflect_on_workflow", description="x",
        instructions="x", estimated_minutes=15, age_appropriate_note="x",
        related_world="Test Career", reflection_prompt="x",
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def test_curiosity_hook_uses_real_seeded_hook_when_present():
    career = make_career(curiosity_hook="A real, honest hook.")
    assert curiosity_hook_for(career) == "A real, honest hook."


def test_curiosity_hook_falls_back_honestly_when_absent():
    career = make_career(curiosity_hook=None)
    hook = curiosity_hook_for(career)
    assert hook  # never empty
    assert "haven't explored" in hook or "new" in hook.lower()


def test_get_exposure_suggestions_records_shown_entries():
    profile = StudentProfile(student_id="s1")
    catalog = [make_career(id="a"), make_career(id="b")]

    selected = get_exposure_suggestions(profile, catalog, now=NOW, limit=2)

    assert len(selected) == 2
    assert len(profile.exposure_history) == 2
    assert all(e.interaction == "shown" for e in profile.exposure_history)


def test_record_exposure_interaction_updates_existing_shown_entry():
    profile = StudentProfile(student_id="s1")
    catalog = [make_career(id="a")]
    get_exposure_suggestions(profile, catalog, now=NOW, limit=1)
    assert profile.exposure_history[0].interaction == "shown"

    record_exposure_interaction(profile, career_id="a", interaction="opened", now=NOW)

    assert len(profile.exposure_history) == 1  # updated in place, not duplicated
    assert profile.exposure_history[0].interaction == "opened"


def test_record_exposure_interaction_appends_when_no_prior_entry():
    profile = StudentProfile(student_id="s1")
    record_exposure_interaction(profile, career_id="never_shown", interaction="dismissed", now=NOW)
    assert len(profile.exposure_history) == 1
    assert profile.exposure_history[0].interaction == "dismissed"


def test_build_exposure_enrichment_composes_entirely_from_career_fields():
    career = make_career(
        description="A real description of the career.",
        videos=["Video A", "Video B", "Video C"],
        books=["Book A", "Book B"],
        projects=["Project A"],
        open_source_projects=["OSS Project A"],
        communities=["Community A"],
    )
    enrichment = build_exposure_enrichment(career, experiment_catalog=[], completed_ids=set())

    assert enrichment.mini_introduction == "A real description of the career."
    assert enrichment.quick_project == "Project A"
    assert enrichment.watch == ["Video A", "Video B"]  # capped at MAX_ITEMS_PER_SECTION
    assert enrichment.read == ["Book A", "Book B"]
    assert enrichment.build == ["Project A", "OSS Project A"]  # projects + open_source_projects merged
    assert enrichment.join == ["Community A"]
    assert career.name in enrichment.reflect_prompt


def test_build_exposure_enrichment_honest_empty_state_when_career_has_thin_content():
    career = make_career()  # no videos/books/projects/communities seeded
    enrichment = build_exposure_enrichment(career, experiment_catalog=[], completed_ids=set())

    assert enrichment.quick_project is None
    assert enrichment.watch == []
    assert enrichment.read == []
    assert enrichment.build == []
    assert enrichment.join == []


def test_build_exposure_enrichment_reuses_experiment_matching_verbatim():
    """Explore Polish Batch — must never build a second suggestion
    engine; `suggested_experience` comes directly from
    experiment_matching.suggest_activity, matched on career name
    against the experiment's related_world/target_traits."""
    career = make_career(name="Marine Biologist")
    matching_experiment = _experiment(id="exp_match", related_world="Marine Biologist")
    other_experiment = _experiment(id="exp_other", related_world="Software Engineer")

    enrichment = build_exposure_enrichment(
        career, experiment_catalog=[other_experiment, matching_experiment], completed_ids=set()
    )

    assert enrichment.suggested_experience is not None
    assert enrichment.suggested_experience.id == "exp_match"


def test_build_exposure_enrichment_suggested_experience_none_when_already_completed():
    career = make_career(name="Marine Biologist")
    matching_experiment = _experiment(id="exp_match", related_world="Marine Biologist")

    enrichment = build_exposure_enrichment(
        career, experiment_catalog=[matching_experiment], completed_ids={"exp_match"}
    )

    assert enrichment.suggested_experience is None
