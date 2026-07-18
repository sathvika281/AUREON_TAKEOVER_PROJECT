from aureon.domain.services.expert_journey_service import build_expert_journey

from ._connect_factories import make_expert


def test_build_expert_journey_returns_the_real_authored_order_unchanged():
    milestones = [
        {"stage": "school", "label": "High school", "description": "x", "year_label": "2000"},
        {"stage": "first_job", "label": "First job", "description": "x", "year_label": "2005"},
    ]
    expert = make_expert(career_journey=milestones)

    journey = build_expert_journey(expert)

    assert [m.stage for m in journey] == ["school", "first_job"]


def test_build_expert_journey_is_honestly_empty_when_none_authored():
    expert = make_expert(career_journey=[])
    assert build_expert_journey(expert) == []
