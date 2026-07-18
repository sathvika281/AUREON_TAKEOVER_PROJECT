from datetime import datetime, timezone

from pydantic import BaseModel, Field

#: Fixed trait vocabulary. Scalar traits (e.g. curiosity) get a numeric
#: `score`; qualitative traits (e.g. learning_style) leave `score` as
#: `None` and carry their meaning entirely in `summary`. Both shapes reuse
#: the same TraitSignal rather than special-casing per trait type.
TRAIT_NAMES = (
    "curiosity",
    "creativity",
    "analytical_thinking",
    "leadership",
    "communication",
    "learning_style",
    "motivation",
    "values",
    "work_preferences",
    "decision_style",
    #: Discover Batch 2 — added so Talent Discovery Lab's Talent Pattern
    #: Engine has real CareerDNA trait names to read for these three
    #: talents (see domain/services/talent_pattern_engine.py::TALENT_NAMES).
    "persistence",
    "empathy",
    "systems_thinking",
)


class TraitSignal(BaseModel):
    """A single trait's current reading within Career DNA. The evidence
    behind it lives in ``StudentProfile.evidence_graph`` (filtered by
    ``related_trait``) rather than a duplicate list on this model — one
    source of truth for evidence, not two."""

    score: float | None = None
    summary: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CareerDNA(BaseModel):
    """A living profile of the student, built up from accumulated evidence
    rather than a one-time personality-type quiz result. Continuously
    updated by the Discovery Agent as new evidence arrives."""

    traits: dict[str, TraitSignal] = Field(default_factory=dict)

    def apply_update(self, *, trait: str, score: float | None, summary: str) -> None:
        """Merge one trait update in place: clamps scores to [0, 1].
        Evidence for this update is recorded separately into the
        student's ``evidence_graph`` by the caller — this method only
        owns the trait's current reading."""
        existing = self.traits.get(trait)
        clamped_score = None if score is None else max(0.0, min(1.0, score))
        if existing is None:
            self.traits[trait] = TraitSignal(score=clamped_score, summary=summary)
            return

        existing.score = clamped_score if clamped_score is not None else existing.score
        existing.summary = summary or existing.summary
        existing.updated_at = datetime.now(timezone.utc)
