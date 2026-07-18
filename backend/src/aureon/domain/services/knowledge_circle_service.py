"""Responsibility: Knowledge Circles' read-time composition — merges a
``KnowledgeCircle``'s own authored fields with content pulled live from
its linked ``CareerWorld``, ``TopicResourceDomain``(s), matching
``Career`` rows, matching ``Trend`` rows, and matching ``LifeMission``
rows. Owns: ``build_circle_view``. Never re-authors or denormalizes any
resource that already exists in one of those five catalogs — this is
the literal "compose, don't duplicate" execution for Connect Batch 2.
Consumed by: ``api/v1/knowledge_circles.py``.
"""

from dataclasses import dataclass, field

from aureon.domain.models.career import Career
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.resource_domain import TopicResourceDomain
from aureon.domain.models.trend import Trend


def _dedup(*groups: list[str]) -> list[str]:
    """Order-preserving, case-insensitive dedup across several merged
    source lists — the same real entry seeded in two catalogs (e.g. a
    book both the CareerWorld and a matched Career recommend) should
    only render once."""
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for item in group:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                result.append(item)
    return result


@dataclass(frozen=True)
class KnowledgeCircleView:
    id: str
    name: str
    overview: str
    what_this_field_is_about: str
    beginner_roadmap: list[str] = field(default_factory=list)
    beginner_projects: list[str] = field(default_factory=list)
    advanced_projects: list[str] = field(default_factory=list)
    laboratories: list[str] = field(default_factory=list)
    startups: list[str] = field(default_factory=list)
    ngos: list[str] = field(default_factory=list)
    scholarships: list[str] = field(default_factory=list)
    books: list[str] = field(default_factory=list)
    documentaries: list[str] = field(default_factory=list)
    podcasts: list[str] = field(default_factory=list)
    youtube_channels: list[str] = field(default_factory=list)
    journals_and_newsletters: list[str] = field(default_factory=list)
    conferences: list[str] = field(default_factory=list)
    competitions: list[str] = field(default_factory=list)
    hackathons: list[str] = field(default_factory=list)
    workshops: list[str] = field(default_factory=list)
    communities: list[str] = field(default_factory=list)
    open_source_projects: list[str] = field(default_factory=list)
    research_organizations: list[str] = field(default_factory=list)
    museums: list[str] = field(default_factory=list)
    companies: list[str] = field(default_factory=list)
    universities: list[str] = field(default_factory=list)
    internships: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    research_papers: list[str] = field(default_factory=list)
    government_initiatives: list[str] = field(default_factory=list)
    volunteering_opportunities: list[str] = field(default_factory=list)


def build_circle_view(
    circle: KnowledgeCircle,
    *,
    career_world: CareerWorld | None,
    topic_domains: list[TopicResourceDomain],
    careers: list[Career],
    trends: list[Trend],
    life_missions: list[LifeMission],
) -> KnowledgeCircleView:
    world_books = career_world.books if career_world else []
    world_communities = career_world.communities if career_world else []
    world_companies = career_world.companies if career_world else []
    world_colleges = career_world.colleges if career_world else []
    world_beginner_roadmap = career_world.beginner_roadmap if career_world else []
    world_internships = career_world.internships if career_world else []

    return KnowledgeCircleView(
        id=circle.id,
        name=circle.name,
        overview=circle.overview,
        what_this_field_is_about=circle.what_this_field_is_about,
        beginner_roadmap=_dedup(world_beginner_roadmap),
        beginner_projects=_dedup(circle.beginner_projects),
        advanced_projects=_dedup(circle.advanced_projects),
        laboratories=_dedup(circle.laboratories),
        scholarships=_dedup(circle.scholarships),
        #: Circle's own seeded startups/ngos, merged with matching real
        #: catalog content — never re-authored twice.
        startups=_dedup(circle.startups, [s for t in trends for s in t.startups]),
        ngos=_dedup(circle.ngos, [n for m in life_missions for n in m.nonprofits]),
        books=_dedup(
            world_books,
            [b for c in careers for b in c.books],
            [b for m in life_missions for b in m.books],
            [b for pd in topic_domains for b in pd.books],
        ),
        documentaries=_dedup(
            [d for pd in topic_domains for d in pd.documentaries],
            [d for m in life_missions for d in m.documentaries],
        ),
        podcasts=_dedup(
            [p for pd in topic_domains for p in pd.podcasts],
            [p for m in life_missions for p in m.podcasts],
        ),
        youtube_channels=_dedup([c for pd in topic_domains for c in pd.youtube_channels]),
        journals_and_newsletters=_dedup([j for pd in topic_domains for j in pd.journals_and_newsletters]),
        conferences=_dedup([c for pd in topic_domains for c in pd.exhibitions_and_conferences]),
        competitions=_dedup([c for career in careers for c in career.competitions]),
        hackathons=_dedup([h for pd in topic_domains for h in pd.hackathons]),
        workshops=_dedup([w for pd in topic_domains for w in pd.workshops]),
        communities=_dedup(
            world_communities,
            [c for pd in topic_domains for c in pd.communities],
            [c for m in life_missions for c in m.communities],
            [c for career in careers for c in career.communities],
        ),
        open_source_projects=_dedup(
            [o for pd in topic_domains for o in pd.open_source_projects],
            [o for career in careers for o in career.open_source_projects],
        ),
        research_organizations=_dedup(
            [r for pd in topic_domains for r in pd.research_organizations],
            [r for m in life_missions for r in m.organizations],
        ),
        museums=_dedup([m for pd in topic_domains for m in pd.museums_and_science_centers]),
        companies=_dedup(
            world_companies,
            [c for career in careers for c in career.companies],
            [c for m in life_missions for c in m.companies],
        ),
        universities=_dedup(world_colleges, [u for career in careers for u in career.universities]),
        internships=_dedup(world_internships),
        certifications=_dedup([c for career in careers for c in career.certifications]),
        research_papers=_dedup([r for t in trends for r in t.research_papers]),
        government_initiatives=_dedup([g for t in trends for g in t.government_initiatives]),
        volunteering_opportunities=_dedup([v for m in life_missions for v in m.volunteering_opportunities]),
    )
