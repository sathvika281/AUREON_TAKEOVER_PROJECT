from datetime import datetime, timezone

from aureon.domain.models.career_memory import CareerMemory, OpportunitiesMemory, OpportunityEntry
from aureon.domain.models.discovery_onboarding import UncertaintySignal, WorldSignal
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.exposure_gap import compute_exposure_gap
from tests.agents.opportunity._factories import make_opportunity

NOW = datetime.now(timezone.utc)


def test_novel_category_is_a_real_contributing_factor():
    opportunity = make_opportunity(category="fellowship", domain_tags=[])
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory()  # no prior opportunity entries at all

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert any("fellowship" in f for f in insight.contributing_factors)


def test_engaged_category_is_not_flagged_as_novel():
    opportunity = make_opportunity(category="fellowship", domain_tags=[])
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory(
        opportunities=OpportunitiesMemory(
            entries=[OpportunityEntry(interaction="viewed", category="fellowship", title="x", occurred_at=NOW)]
        )
    )

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert not any("haven't explored a fellowship" in f for f in insight.contributing_factors)


def test_uncertain_aligned_world_is_a_real_contributing_factor():
    opportunity = make_opportunity(domain_tags=["ai"], category="internship")
    profile = StudentProfile(student_id="s1")
    profile.discovery_onboarding.world_signals = [
        WorldSignal(world="AI", confidence=0.3, evidence=[], status="curious", first_observed=NOW, last_reinforced=NOW)
    ]
    profile.discovery_onboarding.uncertainty_signals = [UncertaintySignal(context="none_yet:AI", observed_at=NOW)]
    memory = CareerMemory()

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.3)

    assert any("AI" in f for f in insight.contributing_factors)


def test_niche_eligibility_is_a_real_contributing_factor():
    opportunity = make_opportunity(min_academic_level="graduate", countries=["Germany"])
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory(opportunities=OpportunitiesMemory(entries=[
        OpportunityEntry(interaction="viewed", category=opportunity.category, title="x", occurred_at=NOW)
    ]))

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert any("eligibility" in f for f in insight.contributing_factors)


def test_no_real_factors_yields_high_likelihood_and_honest_why_shown():
    opportunity = make_opportunity(min_academic_level="any", countries=[])
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory(opportunities=OpportunitiesMemory(entries=[
        OpportunityEntry(interaction="viewed", category=opportunity.category, title="x", occurred_at=NOW)
    ]))

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert insight.likelihood_of_self_discovery == "high"
    assert insight.contributing_factors == []
    assert "well-known" in insight.why_shown


def test_why_shown_always_hedges_never_asserts_certainty():
    opportunity = make_opportunity(category="fellowship")
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory()

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert "could be" in insight.why_shown or "believes" in insight.why_shown
    assert "will be" not in insight.why_shown


def test_multiple_real_factors_yield_low_likelihood():
    opportunity = make_opportunity(category="fellowship", min_academic_level="graduate", countries=["Germany"])
    profile = StudentProfile(student_id="s1")
    memory = CareerMemory()

    insight = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=0.0)

    assert insight.likelihood_of_self_discovery == "low"
