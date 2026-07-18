"""Responsibility: presentation mapping + real aggregation for the
Global Trends Knowledge Base. Owns: ``build_trend_dto``,
``build_future_skills_view``. Does NOT own: `FutureLens` (a single
career's own narrative — untouched, cross-referenced not duplicated).
Consumed by: ``api/v1/trends.py``, ``api/v1/careers.py`` (related
trends).
"""

from collections import Counter

from aureon.domain.models.trend import Trend
from aureon.shared.schemas import FutureSkillDTO, TrendDTO


def build_trend_dto(trend: Trend) -> TrendDTO:
    return TrendDTO(
        id=trend.id, title=trend.title, category=trend.category, summary=trend.summary,
        description=trend.description, affected_industries=trend.affected_industries,
        affected_skills=trend.affected_skills, regions=trend.regions,
        time_horizon=trend.time_horizon, source_note=trend.source_note,
        key_milestones=trend.key_milestones, countries_leading=trend.countries_leading,
        affected_careers=trend.affected_careers, research_papers=trend.research_papers,
        companies=trend.companies, startups=trend.startups,
        government_initiatives=trend.government_initiatives, risks=trend.risks,
        opportunities=trend.opportunities,
    )


def build_future_skills_view(trends: list[Trend]) -> list[FutureSkillDTO]:
    """A real, deterministic aggregation over seeded Trend rows — never
    a separately stored model. Counts how many real trends mention each
    skill, most-mentioned first."""
    skill_counts: Counter[str] = Counter()
    skill_trend_ids: dict[str, list[str]] = {}
    for trend in trends:
        for skill in trend.affected_skills:
            skill_counts[skill] += 1
            skill_trend_ids.setdefault(skill, []).append(trend.id)

    return [
        FutureSkillDTO(skill=skill, mentioned_in_trend_count=count, related_trend_ids=skill_trend_ids[skill])
        for skill, count in skill_counts.most_common()
    ]
