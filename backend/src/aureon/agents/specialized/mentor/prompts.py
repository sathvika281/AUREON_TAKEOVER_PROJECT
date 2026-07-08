from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.mentor import Mentor
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


def _mentor_kb_summary(mentors: list[Mentor]) -> str:
    if not mentors:
        return "No mentors available in the knowledge base."
    lines = ["Mentor Knowledge Base (only these mentors may be proposed, by mentor_id):"]
    for m in mentors:
        tags = ", ".join(m.trait_tags) if m.trait_tags else "none"
        lines.append(f"- {m.id}: {m.name} ({m.role_type}, {m.field}) — {m.bio} [tags: {tags}]")
    return "\n".join(lines)


def build_mentor_match_messages(
    *,
    career_dna: CareerDNA,
    evidence_graph: list[EvidenceRecord],
    career_candidates: list[CareerCandidate],
    mentors: list[Mentor],
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Mentor Agent, running Mentor Match — matching mentors by Career "
        "DNA, interests, learning style, and thinking style, never by popularity.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "Always respond by calling the record_mentor_matches tool."
    )
    context = "\n\n".join(
        [
            _profile_summary(career_dna, evidence_graph, career_candidates),
            _mentor_kb_summary(mentors),
        ]
    )
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="Which mentors might fit me?"),
    ]
