from aureon.domain.services.expert_profile_service import build_expert_profile
from tests.domain._explore_factories import make_career

from ._connect_factories import make_expert


def test_build_expert_profile_resolves_linked_careers_from_real_catalog():
    expert = make_expert(id="e1", career_ids=["c1", "c2"])
    careers = [make_career(id="c1", name="Software Engineer"), make_career(id="c2", name="Data Scientist")]

    profile = build_expert_profile(expert, careers=careers)

    assert profile.id == "e1"
    assert [c.name for c in profile.linked_careers] == ["Software Engineer", "Data Scientist"]


def test_build_expert_profile_never_invents_a_career_not_in_the_catalog():
    expert = make_expert(id="e1", career_ids=["missing_career"])
    profile = build_expert_profile(expert, careers=[make_career(id="c1")])

    assert profile.linked_careers == []


def test_build_expert_profile_carries_who_should_talk_to_me_through_untouched():
    expert = make_expert(who_should_talk_to_me=["Students who like mathematics"])
    profile = build_expert_profile(expert, careers=[])

    assert profile.who_should_talk_to_me == ["Students who like mathematics"]
