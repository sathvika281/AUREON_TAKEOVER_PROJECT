"""Responsibility: Experiment Matching — finds a real, suggested next
Experience Lab activity for a given topic or career name. A thin,
read-only filter over the already-fetched experiment catalog (reused
verbatim) — never a new scoring model, never touches
experiment_result.py's completion-writing logic. Consumed by Exposure
Universe (`exposure_recommendation.py`).
"""

from aureon.domain.models.experiment import Experiment


def suggest_activity(topic: str, experiment_catalog: list[Experiment], completed_ids: set[str]) -> Experiment | None:
    lowered_topic = topic.lower()
    for experiment in experiment_catalog:
        if experiment.id in completed_ids:
            continue
        haystack = " ".join([experiment.related_world, *experiment.target_traits]).lower()
        if lowered_topic in haystack or haystack in lowered_topic:
            return experiment
    return None
