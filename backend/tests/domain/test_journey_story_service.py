from datetime import datetime, timezone

from aureon.domain.models.career_journey import CareerJourneyMilestone
from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.journey_story_service import (
    build_journey_story_view,
    personalize_stories,
    record_story_reflection,
)

from ._connect_factories import make_career_story, make_expert
from ._explore_factories import make_career

NOW = datetime.now(timezone.utc)


def _world_signal(**overrides) -> WorldSignal:
    defaults: dict = dict(world="space", confidence=0.7, first_observed=NOW, last_reinforced=NOW)
    defaults.update(overrides)
    return WorldSignal(**defaults)


def test_build_journey_story_view_resolves_career_name():
    story = make_career_story(career_id="c1")
    career = make_career(id="c1", name="Software Engineer")

    view = build_journey_story_view(story, career=career)

    assert view.career_name == "Software Engineer"
    assert view.linked_expert is None
    assert view.linked_life_mission_name is None


def test_build_journey_story_view_never_denormalizes_missing_career():
    story = make_career_story(career_id="does_not_exist")
    view = build_journey_story_view(story, career=None)
    assert view.career_name == ""


def test_build_journey_story_view_resolves_linked_expert_minimally():
    story = make_career_story(linked_expert_id="expert_9")
    expert = make_expert(id="expert_9", name="Dr. Real Expert", profession="Materials Scientist")

    view = build_journey_story_view(story, career=None, linked_expert=expert)

    assert view.linked_expert.id == "expert_9"
    assert view.linked_expert.name == "Dr. Real Expert"
    assert view.linked_expert.profession == "Materials Scientist"


def test_build_journey_story_view_preserves_timeline_order():
    milestones = [
        CareerJourneyMilestone(stage="university", label="a", description="x", year_label="2018"),
        CareerJourneyMilestone(stage="failure", label="b", description="x", year_label="2020"),
        CareerJourneyMilestone(stage="turning_point", label="c", description="x", year_label="2021"),
    ]
    story = make_career_story(timeline=milestones)
    view = build_journey_story_view(story, career=None)
    assert [m.stage for m in view.timeline] == ["university", "failure", "turning_point"]


def test_build_journey_story_view_carries_honesty_fields():
    story = make_career_story(
        story_type="publicly_documented", source_reference="Real, checkable public source",
        career_switch=True, gap_year=True, uncertainty_period="Two years exploring options.",
    )
    view = build_journey_story_view(story, career=None)
    assert view.story_type == "publicly_documented"
    assert view.source_reference == "Real, checkable public source"
    assert view.career_switch is True
    assert view.gap_year is True


def test_build_journey_story_view_carries_discovery_themes():
    story = make_career_story(discovery_themes=["found_my_passion", "gap_year"])
    view = build_journey_story_view(story, career=None)
    assert view.discovery_themes == ["found_my_passion", "gap_year"]


def test_personalize_stories_ranks_by_real_tag_alignment():
    space_story = make_career_story(id="s1", trait_tags=["space", "physics"])
    unrelated_story = make_career_story(id="s2", trait_tags=["cooking"])
    signals = [_world_signal(world="space", confidence=0.9)]

    relevant = personalize_stories([unrelated_story, space_story], signals)

    assert [s.id for s in relevant] == ["s1"]


def test_personalize_stories_excludes_zero_alignment_never_fabricates():
    story = make_career_story(trait_tags=["cooking"])
    signals = [_world_signal(world="space", confidence=0.9)]

    assert personalize_stories([story], signals) == []


def test_personalize_stories_returns_empty_with_no_signals():
    story = make_career_story(trait_tags=["space"])
    assert personalize_stories([story], []) == []


def test_personalize_stories_respects_limit():
    stories = [make_career_story(id=f"s{i}", trait_tags=["space"]) for i in range(5)]
    signals = [_world_signal(world="space", confidence=0.9)]

    relevant = personalize_stories(stories, signals, limit=2)

    assert len(relevant) == 2


def test_record_story_reflection_appends_a_real_entry():
    profile = StudentProfile(student_id="s1")
    record_story_reflection(
        profile, prompt="Did anything in this story feel familiar?", response="Yes, the uncertainty.", now=NOW
    )

    assert len(profile.reflection_journal) == 1
    entry = profile.reflection_journal[0]
    assert entry.prompt == "Did anything in this story feel familiar?"
    assert entry.response == "Yes, the uncertainty."
    assert entry.answered_at == NOW


def test_record_story_reflection_never_touches_evidence_or_exploration_history():
    profile = StudentProfile(student_id="s1")
    record_story_reflection(profile, prompt="x", response="y", now=NOW)

    assert profile.evidence_graph == []
    assert profile.career_exploration_history == []
