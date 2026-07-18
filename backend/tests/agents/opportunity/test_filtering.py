from datetime import datetime, timedelta, timezone

from aureon.agents.specialized.opportunity.filtering import OpportunityFilters, apply_filters
from tests.agents.opportunity._factories import make_opportunity

NOW = datetime.now(timezone.utc)


def test_no_filters_returns_everything():
    opportunities = [make_opportunity(id="a"), make_opportunity(id="b")]
    assert apply_filters(opportunities, OpportunityFilters()) == opportunities


def test_category_filter():
    internship = make_opportunity(id="a", category="internship")
    hackathon = make_opportunity(id="b", category="hackathon")
    result = apply_filters([internship, hackathon], OpportunityFilters(categories=frozenset({"hackathon"})))
    assert result == [hackathon]


def test_is_remote_filter():
    remote = make_opportunity(id="a", is_remote=True)
    onsite = make_opportunity(id="b", is_remote=False, countries=["USA"])
    result = apply_filters([remote, onsite], OpportunityFilters(is_remote=True))
    assert result == [remote]


def test_country_filter_keeps_remote_and_matching_country_only():
    remote = make_opportunity(id="a", is_remote=True)
    germany = make_opportunity(id="b", is_remote=False, countries=["Germany"])
    usa = make_opportunity(id="c", is_remote=False, countries=["USA"])
    result = apply_filters([remote, germany, usa], OpportunityFilters(countries=frozenset({"Germany"})))
    assert result == [remote, germany]


def test_paid_filter():
    paid = make_opportunity(id="a", paid=True)
    unpaid = make_opportunity(id="b", paid=False)
    assert apply_filters([paid, unpaid], OpportunityFilters(paid=True)) == [paid]


def test_max_academic_level_excludes_opportunities_requiring_more():
    high_school_ok = make_opportunity(id="a", min_academic_level="high_school")
    grad_only = make_opportunity(id="b", min_academic_level="graduate")
    result = apply_filters([high_school_ok, grad_only], OpportunityFilters(max_academic_level="undergraduate"))
    assert result == [high_school_ok]


def test_difficulty_level_filter():
    beginner = make_opportunity(id="a", difficulty_level="beginner")
    advanced = make_opportunity(id="b", difficulty_level="advanced")
    result = apply_filters([beginner, advanced], OpportunityFilters(difficulty_levels=frozenset({"beginner"})))
    assert result == [beginner]


def test_max_competitiveness_excludes_more_competitive_opportunities():
    low = make_opportunity(id="a", estimated_competitiveness="low")
    very_high = make_opportunity(id="b", estimated_competitiveness="very_high")
    result = apply_filters([low, very_high], OpportunityFilters(max_competitiveness="medium"))
    assert result == [low]


def test_organization_kind_filter():
    university = make_opportunity(id="a", organization_kind="university")
    company = make_opportunity(id="b", organization_kind="company")
    result = apply_filters([university, company], OpportunityFilters(organization_kinds=frozenset({"university"})))
    assert result == [university]


def test_required_skills_any_filter():
    python_opp = make_opportunity(id="a", required_skills=["python"])
    java_opp = make_opportunity(id="b", required_skills=["java"])
    result = apply_filters([python_opp, java_opp], OpportunityFilters(required_skills_any=frozenset({"python"})))
    assert result == [python_opp]


def test_domain_tags_any_filter():
    ai_opp = make_opportunity(id="a", domain_tags=["ai"])
    robotics_opp = make_opportunity(id="b", domain_tags=["robotics"])
    result = apply_filters([ai_opp, robotics_opp], OpportunityFilters(domain_tags_any=frozenset({"robotics"})))
    assert result == [robotics_opp]


def test_duration_weeks_range_filter():
    short = make_opportunity(id="a", duration_weeks=2.0)
    long = make_opportunity(id="b", duration_weeks=20.0)
    result = apply_filters([short, long], OpportunityFilters(min_duration_weeks=10.0, max_duration_weeks=30.0))
    assert result == [long]


def test_deadline_range_filter():
    near = make_opportunity(id="a", application_deadline=NOW + timedelta(days=5))
    far = make_opportunity(id="b", application_deadline=NOW + timedelta(days=100))
    result = apply_filters([near, far], OpportunityFilters(deadline_before=NOW + timedelta(days=30)))
    assert result == [near]


def test_deadline_filter_excludes_rolling_admissions_when_a_bound_is_set():
    rolling = make_opportunity(id="a", application_deadline=None)
    result = apply_filters([rolling], OpportunityFilters(deadline_before=NOW + timedelta(days=30)))
    assert result == []
