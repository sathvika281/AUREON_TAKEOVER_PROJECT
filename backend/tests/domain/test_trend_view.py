from aureon.domain.models.trend import Trend
from aureon.domain.services.trend_view import build_future_skills_view, build_trend_dto


def _trend(**overrides) -> Trend:
    defaults: dict = dict(
        id="trend_1", title="Test Trend", category="skill_shift", summary="x", description="x",
        time_horizon="near_term",
    )
    defaults.update(overrides)
    return Trend(**defaults)


def test_build_trend_dto_maps_all_fields():
    trend = _trend(affected_industries=["technology"], affected_skills=["python"], regions=["Global"])
    dto = build_trend_dto(trend)
    assert dto.id == "trend_1"
    assert dto.affected_skills == ["python"]
    assert dto.source_note  # honesty disclaimer always present


def test_future_skills_view_counts_real_mentions():
    trends = [
        _trend(id="t1", affected_skills=["python", "communication"]),
        _trend(id="t2", affected_skills=["python"]),
    ]
    skills = build_future_skills_view(trends)
    python_entry = next(s for s in skills if s.skill == "python")
    assert python_entry.mentioned_in_trend_count == 2
    assert set(python_entry.related_trend_ids) == {"t1", "t2"}


def test_future_skills_view_most_mentioned_first():
    trends = [
        _trend(id="t1", affected_skills=["python"]),
        _trend(id="t2", affected_skills=["python", "communication"]),
        _trend(id="t3", affected_skills=["python"]),
    ]
    skills = build_future_skills_view(trends)
    assert skills[0].skill == "python"
    assert skills[0].mentioned_in_trend_count == 3


def test_future_skills_view_empty_when_no_trends():
    assert build_future_skills_view([]) == []
