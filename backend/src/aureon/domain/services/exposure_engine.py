"""Responsibility: the Exposure Engine — selecting genuinely unfamiliar
careers to surface, never a popularity/fit ranking. Owns:
``select_exposure_careers``. Does NOT own: framing/copy
(``exposure_recommendation.py``) or the underlying Career catalog
(reused as-is from Career Explorer — no duplicate content model).
Consumed by: ``domain/services/exposure_recommendation.py``.

Selection is the inverse of Career Explorer's personalized ordering:
same ``compute_tag_alignment`` function, but here *low* alignment is
what qualifies a career as genuinely unfamiliar rather than merely
unvisited. A career already shown (in any interaction state) is
permanently excluded from being suggested again — a simple, honest
no-repeat policy; a future batch could add time-based re-surfacing
without changing this shape.
"""

import itertools
import random

from aureon.domain.models.career import Career
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.world_signal_alignment import compute_tag_alignment


def _career_tags(career: Career) -> list[str]:
    return [career.industry, career.category, career.name]


def select_exposure_careers(catalog: list[Career], profile: StudentProfile, *, limit: int = 3) -> list[Career]:
    visited_ids = {e.career_id for e in profile.career_exploration_history}
    already_surfaced_ids = {e.career_id for e in profile.exposure_history}
    candidates = [c for c in catalog if c.id not in visited_ids and c.id not in already_surfaced_ids]
    if not candidates:
        return []

    world_signals = profile.discovery_onboarding.world_signals

    def alignment(career: Career) -> float:
        return compute_tag_alignment(_career_tags(career), world_signals)

    candidates.sort(key=alignment)

    # Randomize only *within* equal-alignment ties (real variety across
    # sessions) — a higher-alignment group can never leak ahead of a
    # lower-alignment one just because a slice happened to include both.
    result: list[Career] = []
    for _, group_iter in itertools.groupby(candidates, key=alignment):
        group = list(group_iter)
        random.shuffle(group)
        result.extend(group)
        if len(result) >= limit:
            break
    return result[:limit]
