from aureon.agents.tools.base import Tool, ToolResult, ToolStatus
from aureon.agents.tools.pdf_extraction import extract_pdf_text, pdf_result_to_tool_result

#: Institution owns these because they're all about investigating
#: educational institutions specifically — never careers or mentors.


class UniversityWebsiteReaderTool(Tool):
    name = "university_website_reader"
    description = "Reads a university's official website content."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="Institution records have no stored website URL yet, and no fetch backend "
            "exists — this tool is wired into Institution's toolset and ready for both.",
        )


class CurriculumReaderTool(Tool):
    """Real since V8 (Document Intelligence) for a student-uploaded
    curriculum PDF — genuine text extraction via pypdf, no OCR."""

    name = "curriculum_reader"
    description = "Reads an institution's published curriculum for a given program."

    async def execute(self, *, content: bytes, filename: str = "curriculum.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))


class ResearchLabReaderTool(Tool):
    name = "research_lab_reader"
    description = "Reads details about an institution's research labs beyond what's already seeded."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No external research-lab data source is configured yet — this tool is wired "
            "into Institution's toolset and ready for one.",
        )


class AdmissionPDFReaderTool(Tool):
    """Real since V8 (Document Intelligence) — genuine PDF text
    extraction via pypdf, no OCR, never fabricated."""

    name = "admission_pdf_reader"
    description = "Extracts admission requirements from an institution's published PDF."

    async def execute(self, *, content: bytes, filename: str = "admission.pdf", **kwargs) -> ToolResult:
        return pdf_result_to_tool_result(self.name, filename, extract_pdf_text(content))
