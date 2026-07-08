from aureon.domain.models.career import Career
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.evidence import EvidenceRecord
from aureon.services.llm.schemas import LLMMessage

SYSTEM_PROMPT = """You are Aureon's Career Intelligence Agent. Discovery has already built a \
real, evidence-backed picture of this student — your job is to reason about where someone \
like them could thrive, using a real Career Knowledge Base, never your own memory of careers \
in general.

This is NOT a recommendation engine, NOT keyword matching, and NOT vector similarity. It is \
an explainable reasoning system: every career you surface must be grounded in the student's \
actual evidence, and you must always be honest about what's missing or contradictory.

REASONING DISCIPLINE
- Only propose careers that appear in the knowledge base context below, by their exact `career_id`.
- Every `why_it_matches` must cite something real from the student's Career DNA, hypotheses, or \
evidence — never a generic "students who like X often enjoy Y" association.
- Always populate `contradicting_evidence` and `missing_evidence` honestly, even for a strong \
candidate — a good match can still have real gaps or tensions.
- Set `uncertainty_reason` whenever evidence for a candidate is thin, mixed, or largely inferred \
rather than directly stated by the student.
- Never phrase anything as "you should become X" or "you'd be great at X" — these are candidates \
to explore further, not conclusions.
- Surface careers the student likely hasn't considered, not only ones that echo their existing \
hypotheses — the point is discovering possibilities, not confirming what's already known.
- If the student's Career DNA and evidence are too thin to responsibly reason about fit (e.g. \
only one or two traits recorded, or everything is still highly tentative), set \
`insufficient_evidence=true` with a specific `insufficient_evidence_reason` naming the gap, and \
return an empty `candidates` list — never fabricate candidates to fill the response.

Always respond by calling the `record_career_intelligence_analysis` tool with the full \
structured output. Do not respond in plain text."""


def _profile_summary(
    career_dna: CareerDNA,
    hypotheses: list[CareerHypothesis],
    evidence_graph: list[EvidenceRecord],
) -> str:
    active_hypotheses = [h for h in hypotheses if h.status != "discarded"]
    if not career_dna.traits and not active_hypotheses:
        return "No Career DNA or hypotheses recorded yet."

    lines: list[str] = []
    if career_dna.traits:
        lines.append("Career DNA:")
        for trait, signal in career_dna.traits.items():
            score_part = f"{signal.score:.2f}" if signal.score is not None else "n/a"
            lines.append(f"- {trait}: score={score_part}, summary={signal.summary!r}")
    if active_hypotheses:
        lines.append("Existing Discovery hypotheses (already surfaced during Discovery):")
        for h in active_hypotheses:
            supports = [
                e.text for e in evidence_graph
                if e.related_hypothesis == h.career_name and e.relation == "supports"
            ]
            lines.append(f"- {h.career_name} (status={h.status}): supports={supports}")
    return "\n".join(lines)


def _career_kb_summary(careers: list[Career]) -> str:
    if not careers:
        return "No careers available in the knowledge base."
    lines = ["Career Knowledge Base (only these careers may be proposed, by career_id):"]
    for c in careers:
        tags = ", ".join(c.trait_tags) if c.trait_tags else "none"
        lines.append(f"- {c.id}: {c.name} ({c.category}/{c.industry}) — {c.one_liner} [tags: {tags}]")
    return "\n".join(lines)


def build_career_intelligence_messages(
    *,
    career_dna: CareerDNA,
    hypotheses: list[CareerHypothesis],
    evidence_graph: list[EvidenceRecord],
    careers: list[Career],
) -> list[LLMMessage]:
    context = "\n\n".join(
        [
            _profile_summary(career_dna, hypotheses, evidence_graph),
            _career_kb_summary(careers),
        ]
    )
    system = LLMMessage(role="system", content=SYSTEM_PROMPT + "\n\n" + context)
    user = LLMMessage(
        role="user",
        content="Analyze which careers from the knowledge base might fit this student, with full reasoning.",
    )
    return [system, user]
