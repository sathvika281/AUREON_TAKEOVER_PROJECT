"""Responsibility: Missing Worlds Engine — compares real accumulated
student signal (conversations, reflections, Career DNA, experiments,
interests, World Signals, the Evidence Graph, exposure/exploration
history) against the complete Missing Worlds catalog to classify which
entire career ecosystems the student has explored, partially touched,
or never encountered. Pure and stateless: recomputed on every call, no
LLM, no persistence — same philosophy as talent_pattern_engine.py and
hidden_potential.py. Purely data-driven over `related_industries`; a
new CareerWorld row needs no change here.
"""

from dataclasses import dataclass
from typing import Literal

from aureon.domain.models.career import Career
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.student_profile import StudentProfile

ExplorationLevel = Literal["unexplored", "partially_explored", "explored"]

#: Deterministic-ceiling thresholds — same "small step, capped" philosophy
#: as world_signal.py's REINFORCE_STEP and talent_pattern_engine.py's tiers.
PARTIAL_THRESHOLD = 1
EXPLORED_THRESHOLD = 3

#: How many under-explored worlds to surface as "recommended next" — same
#: "never overwhelming" cap as Exposure Universe's limit=3.
MAX_RECOMMENDED = 5


@dataclass(frozen=True)
class WorldExploration:
    world: CareerWorld
    level: ExplorationLevel
    match_count: int


@dataclass(frozen=True)
class MissingWorldsAnalysis:
    explorations: list[WorldExploration]
    recommended_next: list[CareerWorld]


def _collect_signal_fragments(profile: StudentProfile, careers_by_id: dict[str, Career]) -> list[str]:
    """Real, textual signal fragments pulled from every real source the
    student has actually touched. "Conversation history" maps to the
    Evidence Graph's conversation-sourced entries — the same durable,
    already-established interpreted trace of conversations used
    everywhere else in this codebase; there is no separate raw-transcript
    input here."""
    fragments: list[str] = []
    fragments.extend(profile.interests)
    fragments.extend(signal.world for signal in profile.discovery_onboarding.world_signals)
    fragments.extend(record.text for record in profile.evidence_graph)
    fragments.extend(entry.response for entry in profile.reflection_journal if entry.response)
    fragments.extend(trait.summary for trait in profile.career_dna.traits.values() if trait.summary)

    for completion in profile.career_experiments:
        fragments.append(completion.experiment_title)
        fragments.append(completion.related_world)
        fragments.extend(completion.target_traits)

    for event in profile.career_exploration_history:
        career = careers_by_id.get(event.career_id)
        if career:
            fragments.append(career.industry)
            fragments.extend(career.trait_tags)

    #: Only entries the student actually opened count as signal — a
    #: merely-`shown` (never clicked) Exposure Universe suggestion is not
    #: meaningful exposure, and a `dismissed` one is the student actively
    #: passing on it, not exploring it.
    for entry in profile.exposure_history:
        if entry.interaction != "opened":
            continue
        career = careers_by_id.get(entry.career_id)
        if career:
            fragments.append(career.industry)
            fragments.extend(career.trait_tags)

    return [f for f in fragments if f]


def _match_count(world: CareerWorld, fragments: list[str]) -> int:
    tags = [tag.lower() for tag in (*world.related_industries, world.name)]
    count = 0
    for fragment in fragments:
        lowered = fragment.lower()
        if any(tag in lowered or lowered in tag for tag in tags):
            count += 1
    return count


def _exploration_level(match_count: int) -> ExplorationLevel:
    if match_count >= EXPLORED_THRESHOLD:
        return "explored"
    if match_count >= PARTIAL_THRESHOLD:
        return "partially_explored"
    return "unexplored"


def analyze_missing_worlds(
    profile: StudentProfile, worlds: list[CareerWorld], careers: list[Career]
) -> MissingWorldsAnalysis:
    careers_by_id = {career.id: career for career in careers}
    fragments = _collect_signal_fragments(profile, careers_by_id)

    explorations = []
    for world in worlds:
        count = _match_count(world, fragments)
        explorations.append(WorldExploration(world=world, level=_exploration_level(count), match_count=count))

    #: Real "curiosity overlap" — partially-explored worlds (some real
    #: signal, not yet enough to count as explored) are ranked first by
    #: how much overlap already exists, since that's genuine adjacent
    #: curiosity; fully unexplored worlds (zero overlap) follow in
    #: catalog order, a fair, non-arbitrary tiebreak.
    partial = sorted(
        (e for e in explorations if e.level == "partially_explored"), key=lambda e: -e.match_count
    )
    unexplored = [e for e in explorations if e.level == "unexplored"]
    recommended_next = [e.world for e in (partial + unexplored)[:MAX_RECOMMENDED]]

    return MissingWorldsAnalysis(explorations=explorations, recommended_next=recommended_next)
