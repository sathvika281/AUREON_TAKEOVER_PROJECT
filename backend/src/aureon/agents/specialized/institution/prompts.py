from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.institution import Institution
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


def _institution_kb_summary(institutions: list[Institution]) -> str:
    if not institutions:
        return "No institutions available in the knowledge base."
    lines = ["Institution Knowledge Base (only these institutions may be proposed, by institution_id):"]
    for i in institutions:
        tags = ", ".join(i.trait_tags) if i.trait_tags else "none"
        lines.append(
            f"- {i.id}: {i.name} ({i.city}, {i.country}) — research culture: {i.research_culture} [tags: {tags}]"
        )
    return "\n".join(lines)


def build_college_match_messages(
    *,
    career_dna: CareerDNA,
    evidence_graph: list[EvidenceRecord],
    career_candidates: list[CareerCandidate],
    institutions: list[Institution],
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Institution Agent, running College Match AI — never ranking colleges, "
        "always explaining why an institution fits this specific student's Career DNA.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "Always respond by calling the record_college_matches tool."
    )
    context = "\n\n".join(
        [
            _profile_summary(career_dna, evidence_graph, career_candidates),
            _institution_kb_summary(institutions),
        ]
    )
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="Which institutions might fit me?"),
    ]
