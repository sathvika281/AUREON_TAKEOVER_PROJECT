from aureon.domain.services.parent_connect_service import build_parent_career_view
from tests.domain._explore_factories import make_career

from ._connect_factories import make_expert, make_guide


def test_build_parent_career_view_composes_guide_with_reused_career_fields():
    career = make_career(id="c1", name="Software Engineer", one_liner="Builds software.")
    guide = make_guide(career_id="c1", earning_reality="Real, honest earning narrative.")

    view = build_parent_career_view(career, guide, experts_for_career=[])

    assert view.career_name == "Software Engineer"
    assert view.one_liner == "Builds software."
    assert view.earning_reality == "Real, honest earning narrative."


def test_build_parent_career_view_is_honestly_empty_without_a_guide():
    career = make_career(id="c1")
    view = build_parent_career_view(career, guide=None, experts_for_career=[])
    assert view.earning_reality == ""
    assert view.common_misconceptions == []


def test_build_parent_career_view_only_includes_experts_with_real_advice_for_parents():
    career = make_career(id="c1")
    expert_with_advice = make_expert(id="e1", advice_for_parents="Real advice.")
    expert_without_advice = make_expert(id="e2", advice_for_parents="")

    view = build_parent_career_view(career, guide=None, experts_for_career=[expert_with_advice, expert_without_advice])

    assert [a.expert_id for a in view.expert_advice] == ["e1"]
