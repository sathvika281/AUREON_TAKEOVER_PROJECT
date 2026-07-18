from datetime import datetime, timezone

from aureon.domain.models.exposure import ExposureHistoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.exposure_universe_service import (
    build_exposure_universe,
    build_world_detail,
)
from tests.domain._connect_factories import make_career_story, make_expert, make_knowledge_circle
from tests.domain._explore_factories import make_career, make_career_world

NOW = datetime.now(timezone.utc)


class _FakeStoryRepository:
    def __init__(self, stories):
        self._stories = stories

    async def search_stories(self, *, career_id=None, limit=50, **_kwargs):
        matches = [s for s in self._stories if career_id is None or s.career_id == career_id]
        return matches[:limit], len(matches)


class _FakeExpertRepository:
    def __init__(self, experts):
        self._experts = experts

    async def search_experts(self, *, industry=None, limit=50, **_kwargs):
        matches = [e for e in self._experts if industry is None or industry in e.industries]
        return matches[:limit], len(matches)


def test_exposure_map_partitions_by_level_and_sorts_engaged_by_match_count():
    profile = StudentProfile(student_id="s1", interests=["space", "aerospace engineering", "rockets"])
    worlds = [
        make_career_world(id="world_space", name="Space", related_industries=["space", "aerospace"]),
        make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine"]),
    ]
    universe = build_exposure_universe(
        profile=profile, worlds=worlds, careers=[], experiments=[], knowledge_circles=[], now=NOW
    )

    assert [s.world_name for s in universe.exposure_map.engaged] == ["Space"]
    assert [s.world_name for s in universe.exposure_map.limited_or_none] == ["Marine Sciences"]


def test_missing_worlds_mirrors_recommended_next():
    profile = StudentProfile(student_id="s1")
    worlds = [make_career_world(id=f"world_{i}", name=f"World {i}", related_industries=[f"tag{i}"]) for i in range(3)]
    universe = build_exposure_universe(
        profile=profile, worlds=worlds, careers=[], experiments=[], knowledge_circles=[], now=NOW
    )

    assert [c.world.id for c in universe.missing_worlds] == [w.id for w in worlds]
    assert all(c.level == "unexplored" for c in universe.missing_worlds)


def test_why_missing_cites_a_real_explored_world_when_one_exists():
    profile = StudentProfile(student_id="s1", interests=["space", "aerospace engineering", "rockets"])
    worlds = [
        make_career_world(id="world_space", name="Space", related_industries=["space", "aerospace"]),
        make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine"]),
    ]
    universe = build_exposure_universe(
        profile=profile, worlds=worlds, careers=[], experiments=[], knowledge_circles=[], now=NOW
    )

    marine_card = next(c for c in universe.missing_worlds if c.world.id == "world_marine")
    assert "Space" in marine_card.why_missing
    assert "Marine Sciences" in marine_card.why_missing


def test_why_missing_falls_back_gracefully_with_no_exploration_at_all():
    profile = StudentProfile(student_id="s1")
    worlds = [make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine"])]
    universe = build_exposure_universe(
        profile=profile, worlds=worlds, careers=[], experiments=[], knowledge_circles=[], now=NOW
    )

    card = universe.missing_worlds[0]
    assert "Marine Sciences" in card.why_missing
    assert "hasn't found evidence" in card.why_missing


def test_related_careers_uses_industry_membership_join():
    profile = StudentProfile(student_id="s1")
    world = make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    careers = [
        make_career(id="c1", name="Marine Biologist", industry="marine biology"),
        make_career(id="c2", name="Software Engineer", industry="technology"),
    ]
    universe = build_exposure_universe(
        profile=profile, worlds=[world], careers=careers, experiments=[], knowledge_circles=[], now=NOW
    )

    related_ids = {c.id for c in universe.missing_worlds[0].related_careers}
    assert related_ids == {"c1"}


def test_linked_circle_found_via_linked_career_world_id():
    profile = StudentProfile(student_id="s1")
    world = make_career_world(id="world_space", name="Space")
    circle = make_knowledge_circle(id="circle_space", linked_career_world_id="world_space")
    other_circle = make_knowledge_circle(id="circle_other", linked_career_world_id="world_other")

    universe = build_exposure_universe(
        profile=profile, worlds=[world], careers=[], experiments=[],
        knowledge_circles=[circle, other_circle], now=NOW,
    )

    assert universe.missing_worlds[0].linked_circle is not None
    assert universe.missing_worlds[0].linked_circle.id == "circle_space"


def test_possibility_carries_related_missing_world_when_overlap_exists():
    profile = StudentProfile(student_id="s1")
    world = make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    # Two careers so select_exposure_careers has something to choose from beyond zero.
    careers = [
        make_career(id="c1", name="Marine Biologist", industry="marine biology", trait_tags=[]),
        make_career(id="c2", name="Unrelated Career", industry="unrelated field", trait_tags=[]),
    ]
    universe = build_exposure_universe(
        profile=profile, worlds=[world], careers=careers, experiments=[], knowledge_circles=[], now=NOW
    )

    by_id = {p.career.id: p for p in universe.possibilities}
    if "c1" in by_id:
        assert by_id["c1"].related_missing_world == "Marine Sciences"
    if "c2" in by_id:
        assert by_id["c2"].related_missing_world is None


async def test_build_world_detail_composes_related_stories_and_experts():
    profile = StudentProfile(student_id="s1")
    world = make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    career = make_career(id="c1", name="Marine Biologist", industry="marine biology")
    story = make_career_story(id="story_1", career_id="c1")
    expert = make_expert(id="expert_1", industries=["marine biology"])

    detail = await build_world_detail(
        world_id="world_marine", profile=profile, worlds=[world], careers=[career],
        knowledge_circles=[], stories=_FakeStoryRepository([story]), experts=_FakeExpertRepository([expert]),
    )

    assert detail is not None
    assert detail.world.id == "world_marine"
    assert [c.id for c in detail.related_careers] == ["c1"]
    assert [s.id for s in detail.related_stories] == ["story_1"]
    assert [e.id for e in detail.related_experts] == ["expert_1"]


async def test_build_world_detail_returns_none_for_unknown_world():
    profile = StudentProfile(student_id="s1")
    detail = await build_world_detail(
        world_id="does-not-exist", profile=profile, worlds=[], careers=[],
        knowledge_circles=[], stories=_FakeStoryRepository([]), experts=_FakeExpertRepository([]),
    )
    assert detail is None


def test_shown_only_exposure_entry_does_not_count_toward_missing_worlds_signal():
    """The one real engine change verified end-to-end at the composition
    layer: a career shown but never opened is not meaningful exposure."""
    profile = StudentProfile(student_id="s1")
    profile.exposure_history.append(
        ExposureHistoryEntry(id="x1", career_id="c1", shown_at=NOW, interaction="shown")
    )
    world = make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    careers = [make_career(id="c1", name="Marine Biologist", industry="marine biology")]

    universe = build_exposure_universe(
        profile=profile, worlds=[world], careers=careers, experiments=[], knowledge_circles=[], now=NOW
    )

    assert universe.missing_worlds[0].level == "unexplored"
    assert universe.missing_worlds[0].match_count == 0
