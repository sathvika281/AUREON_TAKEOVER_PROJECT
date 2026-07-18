"""Shared, non-collected (no test_ prefix) fixture builders for the
Opportunity Hub test package."""

from aureon.domain.models.opportunity import Opportunity


def make_opportunity(**overrides) -> Opportunity:
    defaults: dict = dict(
        id="opp_1",
        title="AI Research Internship",
        category="internship",
        organization="Test Org",
        organization_kind="company",
        description="Work on applied AI research with a small team.",
        required_skills=["python", "machine learning"],
        domain_tags=["ai", "machine learning"],
        location="Remote",
        is_remote=True,
        duration_label="10 weeks",
        official_link="https://example.com/opportunity",
    )
    defaults.update(overrides)
    return Opportunity(**defaults)
