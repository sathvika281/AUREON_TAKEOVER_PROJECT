from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class CareerCandidateUpdate(BaseModel):
    career_id: str = Field(description="Must be one of the career IDs listed in the knowledge base context")
    why_it_matches: str = Field(
        description="Grounded explanation citing the student's actual evidence — never a generic trait/career association"
    )
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence that actively points AWAY from this career, not just absent evidence",
    )
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(description="0-1 tentative confidence this career is a real fit")
    uncertainty_reason: str | None = Field(
        default=None,
        description="Why Aureon is still uncertain about this candidate, when applicable — never omitted if confidence is low",
    )


class CareerIntelligenceTurnOutput(BaseModel):
    """Structured contract for one Career Intelligence analysis — mirrors
    the Discovery Agent's tool-calling pattern so career reasoning is
    atomic and auditable rather than parsed from free text."""

    reply_to_student: str = Field(
        description="A short, calm framing of what was found — never phrased as a final recommendation"
    )
    candidates: list[CareerCandidateUpdate] = Field(default_factory=list)
    insufficient_evidence: bool = Field(
        description="True if the student's Career DNA/evidence is too thin to responsibly produce any candidates"
    )
    insufficient_evidence_reason: str | None = Field(
        default=None,
        description="Required when insufficient_evidence is true — names the specific gap, e.g. which traits are still unread",
    )


CAREER_INTELLIGENCE_TOOL = LLMTool(
    name="record_career_intelligence_analysis",
    description=(
        "Record the structured outcome of a Career Intelligence analysis: which "
        "careers from the knowledge base might fit this student, why, and what "
        "evidence supports, contradicts, or is still missing for each."
    ),
    parameters=CareerIntelligenceTurnOutput.model_json_schema(),
)
