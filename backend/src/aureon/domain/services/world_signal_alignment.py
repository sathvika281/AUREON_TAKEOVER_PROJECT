"""Responsibility: the one shared, generic World Signal alignment
computation. Owns: ``compute_tag_alignment``. Does NOT own: what counts
as a "tag" for any given entity — Career Explorer, Exposure Universe,
and Opportunity Equality each assemble their own tag pool (industry/
category/domain_tags/name) and pass it in. Consumed by:
``domain/services/related_careers.py``'s caller in ``api/v1/careers.py``
(personalized ordering, boost aligned), ``domain/services/exposure_engine.py``
(boost *unaligned*, same function inverted), and
``domain/services/exposure_gap.py`` (Opportunity Equality).

Reads ``WorldSignal`` from the frozen Discover Batch 1 model
(``domain/models/discovery_onboarding.py``) read-only — this module
never imports or modifies anything else from that frozen file, and
never writes to it.
"""

from aureon.domain.models.discovery_onboarding import WorldSignal


def compute_tag_alignment(tags: list[str], world_signals: list[WorldSignal]) -> float:
    """Real, case-insensitive substring overlap between ``tags`` (e.g. a
    career's industry/category/name, or an opportunity's domain_tags)
    and each World Signal's real ``world`` name, weighted by that
    signal's real ``confidence`` — deterministic, no LLM, no
    fabrication. Returns 0.0 when there's no real signal to align
    against or no real overlap — never invents a preference."""
    if not tags or not world_signals:
        return 0.0
    tags_lower = [t.lower() for t in tags if t]
    total = 0.0
    for signal in world_signals:
        world_lower = signal.world.lower()
        if any(world_lower in tag or tag in world_lower for tag in tags_lower):
            total += signal.confidence
    return total
