"""Responsibility: Expert Connect's Knowledge composition — the
expert's own authored projects/research/certifications/etc. plus real
supplementary content pulled from their linked careers' `books`/
`companies`/`certifications`. Owns: ``build_expert_knowledge``. This is
the concrete "reuse the Career catalog" composition point — never a
second, duplicated knowledge catalog. Consumed by:
``api/v1/expert_connect.py``.
"""

from dataclasses import dataclass, field

from aureon.domain.models.career import Career
from aureon.domain.models.mentor import LinkRef, Mentor

MAX_SUGGESTED_ITEMS = 5


@dataclass(frozen=True)
class ExpertKnowledge:
    projects: list[str] = field(default_factory=list)
    research: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    conferences: list[str] = field(default_factory=list)
    organizations: list[str] = field(default_factory=list)
    volunteer_work: list[str] = field(default_factory=list)
    portfolio_links: list[LinkRef] = field(default_factory=list)
    social_links: list[LinkRef] = field(default_factory=list)
    daily_skills: list[str] = field(default_factory=list)
    daily_tools: list[str] = field(default_factory=list)
    recommended_books: list[str] = field(default_factory=list)
    recommended_communities: list[str] = field(default_factory=list)
    #: Real content pulled from the expert's linked careers, deduped
    #: against what the expert already lists themselves.
    suggested_books: list[str] = field(default_factory=list)
    suggested_companies: list[str] = field(default_factory=list)
    suggested_certifications: list[str] = field(default_factory=list)


def _dedupe_supplement(own_items: list[str], career_items: list[str]) -> list[str]:
    own_lower = {item.lower() for item in own_items}
    seen: set[str] = set()
    supplement: list[str] = []
    for item in career_items:
        lowered = item.lower()
        if lowered in own_lower or lowered in seen:
            continue
        seen.add(lowered)
        supplement.append(item)
        if len(supplement) >= MAX_SUGGESTED_ITEMS:
            break
    return supplement


def build_expert_knowledge(expert: Mentor, *, linked_careers: list[Career]) -> ExpertKnowledge:
    all_career_books = [b for c in linked_careers for b in c.books]
    all_career_companies = [co for c in linked_careers for co in c.companies]
    all_career_certifications = [ce for c in linked_careers for ce in c.certifications]

    return ExpertKnowledge(
        projects=expert.projects,
        research=expert.research,
        certifications=expert.certifications,
        conferences=expert.conferences,
        organizations=expert.organizations,
        volunteer_work=expert.volunteer_work,
        portfolio_links=expert.portfolio_links,
        social_links=expert.social_links,
        daily_skills=expert.daily_skills,
        daily_tools=expert.daily_tools,
        recommended_books=expert.recommended_books,
        recommended_communities=expert.recommended_communities,
        suggested_books=_dedupe_supplement(expert.recommended_books, all_career_books),
        suggested_companies=_dedupe_supplement(expert.organizations, all_career_companies),
        suggested_certifications=_dedupe_supplement(expert.certifications, all_career_certifications),
    )
