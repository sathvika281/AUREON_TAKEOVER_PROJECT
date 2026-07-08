from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.agents.specialized.decision.simulation_alignment import AlignmentFacts
from aureon.agents.specialized.decision.simulation_schemas import CareerSimulationTurnOutput
from aureon.agents.specialized.growth.evidence_summary import ProgressEvidenceBundle
from aureon.domain.models.career import Career
from aureon.domain.models.career_dna import CareerDNA
from aureon.services.llm.schemas import LLMMessage

#: Never promise a schedule or a guaranteed outcome — the same
#: never-a-prediction framing Parallel Universe already uses.
SIMULATION_FRAMING = (
    "This is a Decision Laboratory, not a prediction engine. Every simulation is one possible, "
    "evidence-informed path — never a certainty, never a guarantee. Frame everything as "
    '"based on your current evidence" rather than what will actually happen.'
)


def _student_context_block(career_dna: CareerDNA, progress: ProgressEvidenceBundle) -> str:
    lines: list[str] = []
    if career_dna.traits:
        lines.append("Career DNA:")
        for trait, signal in career_dna.traits.items():
            score_part = f"{signal.score:.2f}" if signal.score is not None else "n/a"
            lines.append(f"- {trait}: score={score_part}, summary={signal.summary!r}")
    else:
        lines.append("No Career DNA recorded yet.")

    if not progress.insufficient_evidence:
        lines.append("Progress Intelligence (real trends, not a fresh assessment):")
        for dim in progress.dimensions:
            lines.append(f"- {dim.label}: {dim.direction}")
    return "\n".join(lines)


def _facts_block(facts: dict[str, str], alignment: AlignmentFacts) -> str:
    lines = ["Career facts (already known — do not restate or invent these, only reason on top of them):"]
    for dimension, value in facts.items():
        lines.append(f"    {dimension}: {value}")
    lines.append("Student alignment facts (already computed — never re-derive or contradict these):")
    lines.append(f"    career_dna_alignment: {alignment.career_dna_alignment}")
    lines.append(f"    student_interest_alignment: {alignment.student_interest_alignment}")
    lines.append(f"    evidence_confidence: {alignment.evidence_confidence}")
    return "\n".join(lines)


def build_simulation_messages(
    *,
    career: Career,
    facts: dict[str, str],
    alignment: AlignmentFacts,
    career_dna: CareerDNA,
    progress: ProgressEvidenceBundle,
) -> list[LLMMessage]:
    system = (
        f"You are Aureon's Decision Agent, running the Career Simulator for {career.name}. "
        "This simulation must be generated INDEPENDENTLY of any other career the student may also "
        "be considering — reason only about this one path on its own merits, never in contrast "
        "to another career.\n\n"
        f"{SIMULATION_FRAMING}\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "Using the real facts below, write: a short learning_journey narrative, a short list of "
        "expected_milestones, an illustrative timeline of exactly 3 phases (\"Year 1\", \"Year 2\", "
        "\"Year 3+\") each with a focus and milestones, and a trade_offs analysis (advantages, "
        "challenges, opportunities, sacrifices, uncertainties). If the facts are too thin to "
        "responsibly simulate this path, set insufficient_evidence to true and explain why. Always "
        "respond by calling the record_career_simulation tool."
    )
    context = "\n\n".join([
        _student_context_block(career_dna, progress),
        _facts_block(facts, alignment),
    ])
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content=f"Simulate what pursuing {career.name} could look like for me."),
    ]


def _simulation_summary_block(
    entries: list[tuple[str, str, CareerSimulationTurnOutput]],
) -> str:
    lines = ["Independently-generated simulations (already real — do not re-derive, only compare):"]
    for career_id, career_name, output in entries:
        lines.append(f"- {career_id} ({career_name}):")
        lines.append(f"    learning_journey: {output.learning_journey}")
        lines.append(f"    advantages: {output.trade_offs.advantages}")
        lines.append(f"    challenges: {output.trade_offs.challenges}")
        lines.append(f"    sacrifices: {output.trade_offs.sacrifices}")
    return "\n".join(lines)


def build_decision_insights_messages(
    *, entries: list[tuple[str, str, CareerSimulationTurnOutput]]
) -> list[LLMMessage]:
    career_ids = [cid for cid, _, _ in entries]
    system = (
        "You are Aureon's Decision Agent, synthesizing Decision Insights across several "
        "already-independently-simulated career paths. This is the only step where you may "
        "compare or contrast them.\n\n"
        f"{SIMULATION_FRAMING}\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        f"Valid career IDs for this run: {career_ids}. If you name a strongest_match_career_id, it "
        "MUST be exactly one of these IDs — never invent a new one, and leave it null if none "
        "clearly stands out. Explain why, name possible risks, suggest questions the student should "
        "still explore, and recommend one concrete next investigation. Never force a decision — "
        "encourage further exploration. Always respond by calling the record_decision_insights tool."
    )
    context = _simulation_summary_block(entries)
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="What insights can you draw across these simulated paths?"),
    ]
