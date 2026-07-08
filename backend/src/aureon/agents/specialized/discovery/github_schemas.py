from pydantic import BaseModel, Field

from aureon.services.llm.schemas import LLMTool


class GitHubInvestigationTurnOutput(BaseModel):
    """Structured contract for one GitHub Engineering Intelligence
    Report. Grounded only in real structural repository facts and
    skills — never popularity metrics, never invented beyond what the
    GitHub API actually returned."""

    overall_summary: str
    project_purpose: str
    technical_complexity: str
    problem_solving: str
    code_organization: str
    technology_breadth: str
    documentation_quality: str
    learning_signals: str
    engineering_maturity: str
    research_orientation: str
    ai_ml_signals: str
    insufficient_content: bool = False
    insufficient_content_reason: str | None = None


GITHUB_INVESTIGATION_TOOL = LLMTool(
    name="record_github_investigation",
    description=(
        "Record an engineering analysis of a real GitHub repository — grounded only in real "
        "structural evidence given, never popularity metrics, never invented."
    ),
    parameters=GitHubInvestigationTurnOutput.model_json_schema(),
)
