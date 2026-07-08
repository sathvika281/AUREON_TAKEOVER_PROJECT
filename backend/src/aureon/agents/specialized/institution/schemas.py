from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class CollegeMatchUpdate(BaseModel):
    institution_id: str = Field(description="Must be one of the institution IDs listed in the knowledge base context")
    why_it_matches: str
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: float
    uncertainty_reason: str | None = None


class CollegeMatchTurnOutput(BaseModel):
    reply_to_student: str
    matches: list[CollegeMatchUpdate] = Field(default_factory=list)
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


COLLEGE_MATCH_TOOL = LLMTool(
    name="record_college_matches",
    description="Record which institutions from the knowledge base might fit this student, with full reasoning.",
    parameters=CollegeMatchTurnOutput.model_json_schema(),
)
