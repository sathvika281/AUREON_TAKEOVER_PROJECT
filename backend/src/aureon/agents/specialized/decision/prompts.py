from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.domain.models.career import Career
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.evidence import EvidenceRecord
from aureon.services.llm.schemas import LLMMessage


def _profile_summary(
    career_dna: CareerDNA,
    evidence_graph: list[EvidenceRecord],
    career_candidates: list[CareerCandidate],
) -> str:
    if not career_dna.traits and not career_candidates:
        return "No Career DNA or career candidates recorded yet."

    lines: list[str] = []
    if career_dna.traits:
        lines.append("Career DNA:")
        for trait, signal in career_dna.traits.items():
            score_part = f"{signal.score:.2f}" if signal.score is not None else "n/a"
            lines.append(f"- {trait}: score={score_part}, summary={signal.summary!r}")
    active_candidates = [c for c in career_candidates if c.status != "discarded"]
    if active_candidates:
        lines.append("Active career candidates (from Career Intelligence):")
        for c in active_candidates:
            supports = [
                e.text for e in evidence_graph
                if e.related_career == c.career_id and e.relation == "supports"
            ]
            lines.append(f"- {c.career_name} ({c.career_id}): why={c.why_it_matches!r}, supports={supports}")
    return "\n".join(lines)


def _career_facts_block(careers: list[Career], facts_by_id: dict[str, dict[str, str]]) -> str:
    lines = ["Career facts (already known — do not restate or invent these, only reason about why they matter):"]
    for career in careers:
        lines.append(f"- {career.id} ({career.name}):")
        for dimension, value in facts_by_id[career.id].items():
            lines.append(f"    {dimension}: {value}")
    return "\n".join(lines)


def build_comparison_messages(
    *,
    career_dna: CareerDNA,
    evidence_graph: list[EvidenceRecord],
    career_candidates: list[CareerCandidate],
    careers: list[Career],
    facts_by_id: dict[str, dict[str, str]],
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Decision Agent, running Decision Lab — an explainable career "
        "comparison engine. This is NOT a recommendation engine and does not rank careers.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "For each dimension in the career facts below, explain why the difference (or "
        "similarity) between these careers matters specifically for THIS student, grounded in "
        "their Career DNA and evidence. Always respond by calling the record_career_comparison "
        "tool."
    )
    context = "\n\n".join(
        [
            _profile_summary(career_dna, evidence_graph, career_candidates),
            _career_facts_block(careers, facts_by_id),
        ]
    )
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="Compare these careers for me."),
    ]


def build_parallel_universe_messages(
    *,
    career_dna: CareerDNA,
    evidence_graph: list[EvidenceRecord],
    career_candidates: list[CareerCandidate],
    careers: list[Career],
    facts_by_id: dict[str, dict[str, str]],
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Decision Agent, running Parallel Universe — Aureon's signature "
        "feature simulating two possible futures side by side. Never predict the student's "
        "actual future; always frame this as \"based on your current profile.\"\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "For each of the exactly two careers given, write a short, grounded narrative for "
        "daily_work, lifestyle, growth, challenges, and future_opportunities — using the career "
        "facts below as your factual backbone and the student's evidence to personalize it. "
        "Always respond by calling the record_parallel_universe_scenario tool."
    )
    context = "\n\n".join(
        [
            _profile_summary(career_dna, evidence_graph, career_candidates),
            _career_facts_block(careers, facts_by_id),
        ]
    )
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="Simulate two possible futures for me."),
    ]
