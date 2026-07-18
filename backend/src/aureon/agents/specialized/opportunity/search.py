"""Responsibility: keyword-based semantic search over opportunities —
the only search implementation this stage requires. Owns:
`keyword_semantic_search`. Does NOT own: hard filtering (filtering.py)
or fit scoring (scoring.py). Consumed by:
`OpportunityAgent.find_opportunities`.

Deterministic token-overlap, not an embedding/vector search — matches
query tokens against a real per-opportunity text pool (title,
description, category, organization, location, countries, domain tags,
required/preferred skills). Handles the three worked examples ("AI
internships" -> category/domain_tags, "Robotics hackathons" ->
category/domain_tags, "Scholarships for Germany" -> category/countries)
without any AI call.
"""

import re

#: Common connective words stripped so they never contribute to a match
#: or dilute the token-overlap score.
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "for", "in", "of", "on", "or", "the", "to", "with",
})

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN_PATTERN.findall(text.lower()) if t not in _STOPWORDS}


def _haystack(opportunity) -> str:
    parts = [
        opportunity.title,
        opportunity.description,
        opportunity.category,
        opportunity.organization,
        opportunity.location,
        " ".join(opportunity.countries),
        " ".join(opportunity.domain_tags),
        " ".join(opportunity.required_skills),
        " ".join(opportunity.preferred_skills),
    ]
    return " ".join(parts)


def keyword_semantic_search(opportunities: list, query: str) -> list:
    """Returns only opportunities matching at least one real query token,
    ranked by how many distinct query tokens matched (ties keep the
    input's original relative order)."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return list(opportunities)

    scored: list[tuple[int, int, object]] = []
    for position, opportunity in enumerate(opportunities):
        haystack_tokens = _tokenize(_haystack(opportunity))
        match_count = len(query_tokens & haystack_tokens)
        if match_count > 0:
            scored.append((match_count, position, opportunity))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [opportunity for _, _, opportunity in scored]
