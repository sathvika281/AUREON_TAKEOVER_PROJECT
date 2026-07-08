from aureon.agents.tools.base import Tool, ToolResult, ToolStatus
from aureon.agents.tools.pdf_extraction import extract_pdf_text, pdf_result_to_tool_result

#: Mentor owns these because they're all about investigating and
#: comparing mentors specifically — never careers or institutions.


class MentorProfileReaderTool(Tool):
    name = "mentor_profile_reader"
    description = "Reads a mentor's full public profile beyond what's already seeded."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="Mentor records have no stored external profile URL yet — this tool is wired "
            "into Mentor's toolset and ready for one.",
        )


class PublicationReaderTool(Tool):
    """Real since V8 (Document Intelligence) for a student-uploaded
    faculty/publication PDF — genuine text extraction via pypdf, no OCR."""

    name = "publication_reader"
    description = "Reads a mentor's publications to assess expertise depth."

    async def execute(self, *, content: bytes, filename: str = "publication.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))


class ResearchProfileReaderTool(Tool):
    name = "research_profile_reader"
    description = "Reads a mentor's research focus and history."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No research-profile data source is configured yet — this tool is wired into "
            "Mentor's toolset and ready for one.",
        )
