from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment
from aureon.domain.models.learning_style import LearningStyle, LearningStyleEvidenceItem
from aureon.domain.services.learning_style_pattern_engine import (
    build_explanation,
    recommended_experiments_for,
    tier_for,
)

NOW = datetime.now(timezone.utc)


def _style(**overrides) -> LearningStyle:
    defaults = dict(id="style_visual", name="Visual", description="d")
    defaults.update(overrides)
    return LearningStyle(**defaults)


def _evidence(source: str) -> LearningStyleEvidenceItem:
    return LearningStyleEvidenceItem(source=source, description="d", observed_at=NOW)


def test_tier_thresholds():
    assert tier_for([]) is None
    assert tier_for([_evidence("career_dna")]) == "still_emerging"
    assert tier_for([_evidence("career_dna"), _evidence("career_dna")]) == "growing"
    assert tier_for([_evidence("career_dna"), _evidence("reflection"), _evidence("evidence_graph")]) == "strong"
    # 3 same-source items without diversity stay "growing", not "strong"
    assert tier_for([_evidence("career_dna")] * 3) == "growing"


def test_explanation_cites_real_sources_and_never_a_score():
    style = _style()
    evidence = [_evidence("career_dna"), _evidence("reflection")]
    explanation = build_explanation(style, evidence, "growing")

    assert explanation
    assert "%" not in explanation


def test_recommended_experiments_matches_category_and_excludes_completed():
    style = _style(name="Visual")
    matching = Experiment(
        id="exp_1", title="Observe a Design", category="observe_design", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="n", related_world="Design", target_traits=[],
        reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )
    non_matching = Experiment(
        id="exp_2", title="Debug a Bug", category="debug_code", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="n", related_world="AI", target_traits=[],
        reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )

    result = recommended_experiments_for(style, [matching, non_matching], completed_ids=set())
    assert result == [matching]

    result_excluded = recommended_experiments_for(style, [matching, non_matching], completed_ids={"exp_1"})
    assert result_excluded == []
