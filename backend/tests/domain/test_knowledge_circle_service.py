from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.resource_domain import TopicResourceDomain
from aureon.domain.models.trend import Trend
from aureon.domain.services.knowledge_circle_service import build_circle_view

from ._connect_factories import make_knowledge_circle
from ._explore_factories import make_career


def _career_world(**overrides) -> CareerWorld:
    defaults: dict = dict(
        id="world_1", name="Space", description="x", why_it_matters="x", global_importance="x", future_growth="x",
    )
    defaults.update(overrides)
    return CareerWorld(**defaults)


def _topic_domain(**overrides) -> TopicResourceDomain:
    defaults: dict = dict(id="domain_1", name="Space & Astronomy")
    defaults.update(overrides)
    return TopicResourceDomain(**defaults)


def _trend(**overrides) -> Trend:
    defaults: dict = dict(
        id="trend_1", title="x", category="emerging_industry", summary="x", description="x", time_horizon="near_term",
    )
    defaults.update(overrides)
    return Trend(**defaults)


def _mission(**overrides) -> LifeMission:
    defaults: dict = dict(id="mission_1", name="x", description="x")
    defaults.update(overrides)
    return LifeMission(**defaults)


def test_build_circle_view_composes_books_from_every_linked_source_never_re_authoring():
    circle = make_knowledge_circle()
    world = _career_world(books=["World Book"])
    career = make_career(id="c1", books=["Career Book"])
    mission = _mission(books=["Mission Book"])
    domain = _topic_domain(books=["Domain Book"])

    view = build_circle_view(
        circle, career_world=world, topic_domains=[domain], careers=[career], trends=[], life_missions=[mission],
    )

    assert set(view.books) == {"World Book", "Career Book", "Mission Book", "Domain Book"}


def test_build_circle_view_dedups_case_insensitively_preserving_first_occurrence():
    circle = make_knowledge_circle()
    world = _career_world(books=["NASA Handbook"])
    career = make_career(id="c1", books=["nasa handbook"])

    view = build_circle_view(
        circle, career_world=world, topic_domains=[], careers=[career], trends=[], life_missions=[],
    )

    assert view.books == ["NASA Handbook"]


def test_build_circle_view_merges_circle_own_startups_with_matched_trends():
    circle = make_knowledge_circle(startups=["Own Startup"])
    trend = _trend(startups=["Trend Startup"])

    view = build_circle_view(
        circle, career_world=None, topic_domains=[], careers=[], trends=[trend], life_missions=[],
    )

    assert set(view.startups) == {"Own Startup", "Trend Startup"}


def test_build_circle_view_merges_circle_own_ngos_with_matched_mission_nonprofits():
    circle = make_knowledge_circle(ngos=["Own NGO"])
    mission = _mission(nonprofits=["Mission Nonprofit"])

    view = build_circle_view(
        circle, career_world=None, topic_domains=[], careers=[], trends=[], life_missions=[mission],
    )

    assert set(view.ngos) == {"Own NGO", "Mission Nonprofit"}


def test_build_circle_view_never_composes_beginner_projects_from_other_catalogs():
    """`beginner_projects`/`advanced_projects`/`laboratories`/`scholarships`
    are the circle's own authored content — never merged with anything
    else, unlike books/communities/etc."""
    circle = make_knowledge_circle(beginner_projects=["Own Project"])
    world = _career_world(beginner_projects=["World Project"])

    view = build_circle_view(
        circle, career_world=world, topic_domains=[], careers=[], trends=[], life_missions=[],
    )

    assert view.beginner_projects == ["Own Project"]


def test_build_circle_view_handles_no_linked_sources_gracefully():
    circle = make_knowledge_circle()
    view = build_circle_view(
        circle, career_world=None, topic_domains=[], careers=[], trends=[], life_missions=[],
    )
    assert view.books == []
    assert view.companies == []
    assert view.overview == circle.overview
