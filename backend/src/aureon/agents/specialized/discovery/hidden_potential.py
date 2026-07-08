from pydantic import BaseModel

from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.evidence import EvidenceRecord

#: Both traits in a pair must clear this to count as "strong" —
#: deliberately simple co-occurrence thresholding on real scores, not
#: framed as more sophisticated pattern-mining than it actually is.
STRONG_THRESHOLD = 0.5


class HiddenPotentialPattern(BaseModel):
    id: str
    trait_a: str
    trait_b: str
    sentence: str
    supporting_evidence: list[str]


def _trait_label(name: str) -> str:
    return name.replace("_", " ").title()


def derive_hidden_potential(
    career_dna: CareerDNA, evidence_graph: list[EvidenceRecord]
) -> list[HiddenPotentialPattern]:
    """Server-side Hidden Potential detection: the same co-occurrence
    heuristic that used to live entirely client-side, now grounded in
    real evidence pulled from the Evidence Graph rather than stating a
    pattern with nothing behind it. Deterministic — no extra LLM call,
    computed fresh from already-persisted data.
    """
    strong_traits = [
        name
        for name, signal in career_dna.traits.items()
        if (signal.score or 0) >= STRONG_THRESHOLD
    ]

    patterns: list[HiddenPotentialPattern] = []
    for i in range(len(strong_traits)):
        for j in range(i + 1, len(strong_traits)):
            trait_a, trait_b = strong_traits[i], strong_traits[j]
            cited = [e.text for e in evidence_graph if e.related_trait == trait_a][:1] + [
                e.text for e in evidence_graph if e.related_trait == trait_b
            ][:1]
            label_a, label_b = _trait_label(trait_a), _trait_label(trait_b)
            patterns.append(
                HiddenPotentialPattern(
                    id=f"{trait_a}-{trait_b}",
                    trait_a=label_a,
                    trait_b=label_b,
                    sentence=(
                        f"You consistently combine {label_a} with {label_b}. "
                        "Many students only show one."
                    ),
                    supporting_evidence=cited,
                )
            )
    return patterns
