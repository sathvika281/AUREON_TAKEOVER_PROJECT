from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class EvidenceItem(BaseModel):
    kind: str = Field(
        description="Free-form evidence category, e.g. 'conversation', 'motivation', 'behavior'"
    )
    description: str = Field(
        description="One or two sentences describing what was learned and from what"
    )


class CareerDNAUpdate(BaseModel):
    trait: str = Field(
        description=(
            "One of: curiosity, creativity, analytical_thinking, leadership, "
            "communication, learning_style, motivation, values, "
            "work_preferences, decision_style"
        )
    )
    score: float | None = Field(
        default=None,
        description="0-1 strength for scalar traits; omit for purely qualitative ones",
    )
    summary: str = Field(description="Human-readable current reading of this trait")
    rationale: str = Field(
        description="Why this update is justified given the conversation so far — becomes the evidence citation"
    )


class WhyProbe(BaseModel):
    is_probing: bool = Field(
        description="True if reply_to_student asks a 'why' follow-up instead of moving on"
    )
    topic: str = Field(
        default="",
        description="Short stable label for the topic being probed (e.g. 'wants_to_be_doctor')",
    )
    depth: int = Field(
        default=0,
        description="How many times this exact topic has now been probed, including this one",
    )


class HypothesisUpdate(BaseModel):
    career_name: str
    confidence: float = Field(description="0-1 tentative confidence in this specific hypothesis")
    supporting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence that actively points AWAY from this hypothesis, not just absent evidence",
    )


class SuggestedActivity(BaseModel):
    title: str
    description: str = Field(
        description="A concrete, specific micro-activity the student can do to generate more evidence"
    )
    reason: str = Field(
        description=(
            "Why THIS activity, grounded in a specific missing_evidence gap or weak "
            "hypothesis — never a generic 'to learn more about yourself'"
        )
    )


class DiscoveryTurnOutput(BaseModel):
    """Structured contract for a single Discovery Agent turn. Everything
    the LLM reasons about — the reply, extracted evidence, Career DNA
    updates, why-probing, reflection prompting, hypotheses, and confidence
    — comes back atomically via tool-calling rather than being parsed out
    of free text.
    """

    reply_to_student: str = Field(
        description="Warm, mentor-like reply. Never say 'quiz', 'score', or refer to internal mechanics."
    )
    extracted_evidence: list[EvidenceItem] = Field(default_factory=list)
    career_dna_updates: list[CareerDNAUpdate] = Field(default_factory=list)
    probe: WhyProbe
    reflection_prompt: str | None = Field(
        default=None,
        description="A reflective question to ask after a meaningful moment — not every turn",
    )
    hypotheses: list[HypothesisUpdate] = Field(default_factory=list)
    confidence_score: float = Field(
        description="0-1 overall confidence in understanding this student so far"
    )
    suggested_activity: SuggestedActivity | None = Field(
        default=None,
        description="Only when evidence is thin and a concrete activity would help more than more chat",
    )


DISCOVERY_TOOL = LLMTool(
    name="record_discovery_turn",
    description=(
        "Record the structured outcome of this Discovery turn: your reply "
        "to the student plus every piece of evidence, Career DNA update, "
        "hypothesis, and confidence judgment behind it."
    ),
    parameters=DiscoveryTurnOutput.model_json_schema(),
)
