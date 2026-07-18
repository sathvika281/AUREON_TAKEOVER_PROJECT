"""Responsibility: Experience Lab Service — the minimal composition layer
behind the merged Experience Lab / Life Missions product experience.
Owns nothing new: catalog grouping and a small recommendation heuristic
only. Calls the real catalog helpers (experiment_history.py) and the
real Life Mission engine (life_mission_engine.py) verbatim — neither
domain is rewritten or merged, matching the product decision that this
is a frontend unification, not a backend one.
"""

from dataclasses import dataclass, field
from datetime import datetime

from aureon.domain.models.experiment import Experiment, ExperimentCompletion
from aureon.domain.models.life_mission import LifeMission, MissionResonance
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_history import get_completed_experiment_ids, get_experiment_history
from aureon.domain.services.life_mission_engine import analyze_life_missions

#: How many mission-linked suggestions can appear in "Recommended for
#: You" alongside the one plain next-uncompleted-experiment pick — kept
#: small so the section stays a genuine highlight, not a second full list.
MAX_RECOMMENDED_MISSION_SUGGESTIONS = 2


@dataclass
class EmergingMission:
    resonance: MissionResonance
    suggested_experience: Experiment | None


@dataclass
class ExperienceLabView:
    recommended: list[Experiment] = field(default_factory=list)
    mission_experiences: list[Experiment] = field(default_factory=list)
    career_experiences: list[Experiment] = field(default_factory=list)
    completed: list[ExperimentCompletion] = field(default_factory=list)
    completed_experiment_ids: set[str] = field(default_factory=set)
    emerging_missions: list[EmergingMission] = field(default_factory=list)


def _first_uncompleted(experiments: list[Experiment], completed_ids: set[str]) -> Experiment | None:
    return next((e for e in experiments if e.id not in completed_ids and e.is_active), None)


def build_experience_lab_view(
    profile: StudentProfile, *, experiments: list[Experiment], missions: list[LifeMission], now: datetime
) -> ExperienceLabView:
    completed_ids = get_completed_experiment_ids(profile)
    active = [e for e in experiments if e.is_active]

    career_experiences = [e for e in active if not e.related_life_mission_ids]
    mission_experiences = [e for e in active if e.related_life_mission_ids]

    resonances = analyze_life_missions(profile, missions, now=now)
    emerging_missions: list[EmergingMission] = []
    for resonance in resonances:
        suggested = next(
            (
                e
                for e in mission_experiences
                if e.id not in completed_ids and resonance.mission.id in e.related_life_mission_ids
            ),
            None,
        )
        emerging_missions.append(EmergingMission(resonance=resonance, suggested_experience=suggested))

    recommended: list[Experiment] = []
    next_plain = _first_uncompleted(career_experiences, completed_ids)
    if next_plain is not None:
        recommended.append(next_plain)

    seen_ids = {e.id for e in recommended}
    for emerging in emerging_missions:
        if len(recommended) - (1 if next_plain else 0) >= MAX_RECOMMENDED_MISSION_SUGGESTIONS:
            break
        suggestion = emerging.suggested_experience
        if suggestion is not None and suggestion.id not in seen_ids:
            recommended.append(suggestion)
            seen_ids.add(suggestion.id)

    return ExperienceLabView(
        recommended=recommended,
        mission_experiences=mission_experiences,
        career_experiences=career_experiences,
        completed=get_experiment_history(profile),
        completed_experiment_ids=completed_ids,
        emerging_missions=emerging_missions,
    )
