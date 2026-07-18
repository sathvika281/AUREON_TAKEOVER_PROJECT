from aureon.domain.services.related_careers import find_related_careers
from tests.domain._explore_factories import make_career


def test_returns_careers_with_real_industry_match():
    target = make_career(id="a", industry="technology", trait_tags=[])
    same_industry = make_career(id="b", industry="technology", trait_tags=[])
    other_industry = make_career(id="c", industry="healthcare", trait_tags=[])

    result = find_related_careers(target, [target, same_industry, other_industry])

    assert [c.id for c in result] == ["b"]


def test_returns_careers_with_real_trait_tag_overlap():
    target = make_career(id="a", industry="technology", trait_tags=["curiosity", "analytical_thinking"])
    overlapping = make_career(id="b", industry="finance", trait_tags=["curiosity"])
    no_overlap = make_career(id="c", industry="finance", trait_tags=["leadership"])

    result = find_related_careers(target, [target, overlapping, no_overlap])

    assert [c.id for c in result] == ["b"]


def test_never_pads_with_a_career_with_zero_real_basis():
    target = make_career(id="a", industry="technology", trait_tags=["curiosity"])
    unrelated = make_career(id="b", industry="healthcare", trait_tags=["leadership"])

    assert find_related_careers(target, [target, unrelated]) == []


def test_ranks_industry_and_trait_match_above_industry_only():
    target = make_career(id="a", industry="technology", trait_tags=["curiosity"])
    industry_and_trait = make_career(id="b", industry="technology", trait_tags=["curiosity"])
    industry_only = make_career(id="c", industry="technology", trait_tags=["leadership"])

    result = find_related_careers(target, [target, industry_only, industry_and_trait])

    assert [c.id for c in result] == ["b", "c"]


def test_excludes_the_career_itself():
    target = make_career(id="a", industry="technology")
    assert find_related_careers(target, [target]) == []


def test_respects_limit():
    target = make_career(id="a", industry="technology")
    others = [make_career(id=f"c{i}", industry="technology") for i in range(6)]
    result = find_related_careers(target, [target, *others], limit=3)
    assert len(result) == 3
