from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class MentorMatchUpdate(BaseModel):
    mentor_id: str = Field(description="Must be one of the mentor IDs listed in the knowledge base context")
    why_it_matches: str
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: float
    uncertainty_reason: str | None = None


class MentorMatchTurnOutput(BaseModel):
    reply_to_student: str
    matches: list[MentorMatchUpdate] = Field(default_factory=list)
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


MENTOR_MATCH_TOOL = LLMTool(
    name="record_mentor_matches",
    description="Record which mentors from the knowledge base might fit this student, with full reasoning.",
    parameters=MentorMatchTurnOutput.model_json_schema(),
)
