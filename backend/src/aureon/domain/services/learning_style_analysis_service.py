"""Responsibility: Learning Style Analysis Service — the thin
composition entry point consumed by api/v1/learning_styles.py. Calls
the Learning Style Evidence Builder and Pattern Engine, plus the
existing Talent Pattern Engine (reused, called exactly once). Never
persists a result — recomputed fresh on every call.
"""

from aureon.domain.models.experiment import Experiment
from aureon.domain.models.learning_style import LearningStyle, LearningStylePattern
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_history import get_completed_experiment_ids
from aureon.domain.services.learning_style_evidence import build_evidence
from aureon.domain.services.learning_style_pattern_engine import (
    build_explanation,
    recommended_experiments_for,
    tier_for,
)
from aureon.domain.services.talent_pattern_engine import analyze_talents


def analyze_learning_styles(
    profile: StudentProfile, styles: list[LearningStyle], experiment_catalog: list[Experiment]
) -> list[LearningStylePattern]:
    talent_patterns = analyze_talents(profile)
    completed_ids = get_completed_experiment_ids(profile)

    patterns: list[LearningStylePattern] = []
    for style in styles:
        evidence = build_evidence(style, profile, talent_patterns, experiment_catalog)
        tier = tier_for(evidence)
        if tier is None:
            continue
        patterns.append(
            LearningStylePattern(
                style=style,
                tier=tier,
                explanation=build_explanation(style, evidence, tier),
                evidence=evidence,
                recommended_experiments=recommended_experiments_for(style, experiment_catalog, completed_ids),
            )
        )
    return patterns
