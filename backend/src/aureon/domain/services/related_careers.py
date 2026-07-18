"""Responsibility: the Related Career Engine — "what else might I find
interesting near this career." Owns: ``find_related_careers``. Does NOT
own: recommendation/fit reasoning (Career Intelligence Agent) — this
never ranks careers by how well they'd suit the student, only by real
content adjacency to the career currently being viewed. Consumed by:
``api/v1/careers.py``'s career detail route.

Deterministic, no LLM — real industry match + real ``trait_tags``
overlap, same "tag overlap, not embeddings" philosophy the existing
career detail route already uses for story reordering. Only ever
returns careers with a genuine, real basis for the connection — never
pads out to a fixed count with an unrelated career just to fill space.
"""

from aureon.domain.models.career import Career


def _relatedness(career: Career, other: Career) -> tuple[int, int]:
    industry_match = 1 if other.industry == career.industry else 0
    tag_overlap = len(set(other.trait_tags) & set(career.trait_tags))
    return (industry_match, tag_overlap)


def find_related_careers(career: Career, catalog: list[Career], *, limit: int = 4) -> list[Career]:
    candidates = [c for c in catalog if c.id != career.id]
    real_matches = [c for c in candidates if _relatedness(career, c) != (0, 0)]
    real_matches.sort(key=lambda c: _relatedness(career, c), reverse=True)
    return real_matches[:limit]
