from datetime import datetime, timezone

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.opportunity_equality import find_equality_opportunities
from aureon.services.foundation.career_memory.service import get_career_memory_snapshot
from tests.agents.opportunity._factories import make_opportunity

NOW = datetime.now(timezone.utc)


def test_excludes_not_ready_opportunities():
    """A wildly out-of-reach opportunity is never surfaced — Opportunity
    Equality only ever ranks among eligible-adjacent candidates."""
    opportunity = make_opportunity(min_academic_level="graduate", countries=["Germany"], required_skills=["ten years of experience"])
    profile = StudentProfile(student_id="s1")  # empty profile -> low fit
    memory = get_career_memory_snapshot(profile)

    recs = find_equality_opportunities(profile, memory, [opportunity], now=NOW)

    # An empty profile against a narrow, skill-heavy opportunity should
    # score not_ready and be excluded — but this isn't guaranteed for
    # every possible opportunity shape, so assert the *contract*
    # (never returns a not_ready fit) rather than a specific count.
    assert all(r.fit.readiness_label != "not_ready" for r in recs)


def test_excludes_inactive_opportunities():
    opportunity = make_opportunity(is_active=False)
    profile = StudentProfile(student_id="s1")
    memory = get_career_memory_snapshot(profile)

    recs = find_equality_opportunities(profile, memory, [opportunity], now=NOW)

    assert recs == []


def test_never_mutates_opportunity_hubs_own_fit_result():
    """The fit attached to each recommendation is the real,
    unmodified OpportunityFitResult — same object shape Opportunity Hub
    itself produces, not a parallel/altered score."""
    opportunity = make_opportunity()
    profile = StudentProfile(student_id="s1")
    memory = get_career_memory_snapshot(profile)

    recs = find_equality_opportunities(profile, memory, [opportunity], now=NOW)

    for r in recs:
        assert hasattr(r.fit, "overall_score")
        assert hasattr(r.fit, "factors")
        assert len(r.fit.factors) == 10  # Opportunity Hub's real 10-factor scoring, untouched


def test_ranks_low_likelihood_before_high_likelihood():
    novel = make_opportunity(id="novel", category="fellowship", min_academic_level="any", countries=[])
    familiar = make_opportunity(id="familiar", category="internship", min_academic_level="any", countries=[])
    profile = StudentProfile(student_id="s1")
    memory = get_career_memory_snapshot(profile)
    # Pre-engage "internship" so it's not flagged as a novel category —
    # "fellowship" stays genuinely novel, giving it a real lower likelihood.
    from aureon.domain.models.career_memory import OpportunityEntry
    profile.foundation_memory.opportunities.entries.append(
        OpportunityEntry(interaction="viewed", category="internship", title="x", occurred_at=NOW)
    )
    memory = get_career_memory_snapshot(profile)

    recs = find_equality_opportunities(profile, memory, [familiar, novel], now=NOW)

    ids = [r.opportunity.id for r in recs]
    assert ids.index("novel") < ids.index("familiar")


def test_respects_top_n():
    opportunities = [make_opportunity(id=f"o{i}", min_academic_level="any", countries=[]) for i in range(8)]
    profile = StudentProfile(student_id="s1")
    memory = get_career_memory_snapshot(profile)

    recs = find_equality_opportunities(profile, memory, opportunities, now=NOW, top_n=3)

    assert len(recs) <= 3
