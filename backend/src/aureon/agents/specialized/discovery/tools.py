from aureon.agents.specialized.discovery.github_reader import fetch_repository
from aureon.agents.tools.base import Evidence, Tool, ToolResult, ToolStatus
from aureon.agents.tools.pdf_extraction import extract_pdf_text, pdf_result_to_tool_result

#: Discovery owns these because they're all about understanding the
#: student — extracting evidence to feed Career DNA. None of them
#: investigate careers, institutions, or mentors; that's not Discovery's
#: job (see agents/mission/capabilities.py).


class DocumentReaderTool(Tool):
    name = "document_reader"
    description = "Reads a general document the student provides and extracts evidence for Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No document upload pipeline exists yet — this tool is wired into Discovery's "
            "toolset and ready for one.",
        )


class PDFReaderTool(Tool):
    """Real since V8 (Document Intelligence) — genuine PDF text
    extraction via pypdf, no OCR, never fabricated."""

    name = "pdf_reader"
    description = "Extracts text from a student-provided PDF for evidence extraction."

    async def execute(self, *, content: bytes, filename: str = "document.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))


class ImageUnderstandingTool(Tool):
    name = "image_understanding"
    description = "Interprets an image the student provides (e.g. a certificate or project photo) for evidence."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No image/vision model is configured yet — this tool is wired into Discovery's "
            "toolset and ready for one.",
        )


class ResumeReaderTool(Tool):
    """Real since V8 (Document Intelligence) — genuine PDF text
    extraction via pypdf, no OCR, never fabricated."""

    name = "resume_reader"
    description = "Reads a student's resume/CV and extracts evidence for Career DNA."

    async def execute(self, *, content: bytes, filename: str = "resume.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))


class GitHubReaderTool(Tool):
    """Discovery's flagship capability (V9, GitHub Intelligence) — real
    GitHub REST API calls, no scraping, no fabrication. The full
    structured fetch result is carried in Evidence.metadata (an existing
    field, not a new one) so the pipeline can rebuild a complete
    ``GitHubFetchResult`` for deterministic fact/skill extraction without
    inventing anything beyond what GitHub actually returned."""

    name = "github_reader"
    description = "Fetches real GitHub repository data (metadata, languages, README, structure) for engineering evidence."

    async def execute(self, *, owner: str, repo: str, **kwargs) -> ToolResult:
        result = await fetch_repository(owner, repo)
        if result.status != "completed":
            return ToolResult(tool_name=self.name, status=ToolStatus.FAILED, explanation=result.explanation)
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=[
                Evidence(
                    source=f"{owner}/{repo}",
                    source_type="github_repository",
                    summary=f"Repository data fetched for {owner}/{repo}",
                    metadata={
                        "repo_data": result.repo_data,
                        "languages": result.languages,
                        "readme_text": result.readme_text,
                        "root_files": result.root_files,
                        "dependency_names": result.dependency_names,
                        "has_ci_workflows": result.has_ci_workflows,
                    },
                )
            ],
        )


class ChatExportReaderTool(Tool):
    name = "chat_export_reader"
    description = "Reads an exported chat/conversation history the student provides for evidence."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No chat-export ingestion exists yet — this tool is wired into Discovery's "
            "toolset and ready for one.",
        )
