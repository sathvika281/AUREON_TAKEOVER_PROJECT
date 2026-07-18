from aureon.domain.models.institution import (
    InnovationCenter,
    Institution,
    ResearchLab,
    StudentOrganization,
)
from aureon.domain.services.institution_profile import compute_institution_profile


def _institution(**overrides) -> Institution:
    defaults: dict = dict(
        id="inst_1", name="Test University", country="Testland", city="Test City",
        research_culture="x", innovation_ecosystem="x", industry_collaboration="x",
        placements="x", learning_environment="x",
    )
    defaults.update(overrides)
    return Institution(**defaults)


def _labs(n: int) -> list[ResearchLab]:
    return [ResearchLab(id=f"lab_{i}", institution_id="inst_1", name=f"Lab {i}", focus_area="x", description="x") for i in range(n)]


def _centers(n: int) -> list[InnovationCenter]:
    return [
        InnovationCenter(id=f"center_{i}", institution_id="inst_1", name=f"Center {i}", focus_area="x", description="x")
        for i in range(n)
    ]


def _orgs(n: int) -> list[StudentOrganization]:
    return [
        StudentOrganization(id=f"org_{i}", institution_id="inst_1", name=f"Org {i}", focus_area="x", description="x")
        for i in range(n)
    ]


def test_never_produces_a_raw_numeric_score_field_beyond_the_1_to_5_tiers():
    institution = _institution()
    profile = compute_institution_profile(institution, research_labs=[], innovation_centers=[], student_organizations=[])
    for tier in (profile.research, profile.entrepreneurship, profile.campus_life, profile.international_exposure):
        assert 1 <= tier <= 5


def test_zero_real_counts_gives_the_floor_tier():
    institution = _institution()
    profile = compute_institution_profile(institution, research_labs=[], innovation_centers=[], student_organizations=[])
    assert profile.research == 1
    assert profile.entrepreneurship == 1
    assert profile.campus_life == 1
    assert profile.international_exposure == 1


def test_research_tier_scales_with_real_lab_count():
    institution = _institution()
    low = compute_institution_profile(institution, research_labs=_labs(1), innovation_centers=[], student_organizations=[])
    high = compute_institution_profile(institution, research_labs=_labs(6), innovation_centers=[], student_organizations=[])
    assert high.research > low.research
    assert high.research == 5


def test_entrepreneurship_tier_scales_with_real_innovation_center_count():
    institution = _institution()
    low = compute_institution_profile(institution, research_labs=[], innovation_centers=_centers(1), student_organizations=[])
    high = compute_institution_profile(institution, research_labs=[], innovation_centers=_centers(4), student_organizations=[])
    assert high.entrepreneurship > low.entrepreneurship
    assert high.entrepreneurship == 5


def test_campus_life_combines_orgs_hostels_and_facilities():
    institution = _institution(hostels=["Hall A", "Hall B"], campus_facilities=["Gym", "Library"])
    profile = compute_institution_profile(
        institution, research_labs=[], innovation_centers=[], student_organizations=_orgs(2)
    )
    # 2 orgs + 2 hostels + 2 facilities = 6 real items -> above the floor tier
    assert profile.campus_life > 1


def test_international_exposure_scales_with_real_exchange_program_count():
    institution = _institution(exchange_programs=["Exchange A", "Exchange B", "Exchange C", "Exchange D"])
    profile = compute_institution_profile(institution, research_labs=[], innovation_centers=[], student_organizations=[])
    assert profile.international_exposure == 5


def test_profile_is_computed_fresh_never_persisted_on_the_model():
    """Deterministic-ceiling, never-fabricate philosophy — the tiers must
    never be a field stored on Institution itself, only ever derived at
    read time from real counts."""
    assert not hasattr(Institution(**_institution().model_dump(exclude={"created_at", "updated_at"})), "profile")
