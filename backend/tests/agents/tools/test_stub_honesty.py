import pytest

from aureon.agents.specialized.career_intelligence.tools import (
    BrowserInvestigationTool,
    SearchTool,
    TrendInvestigationTool,
)
from aureon.agents.specialized.discovery.tools import (
    ChatExportReaderTool,
    DocumentReaderTool,
    ImageUnderstandingTool,
)
from aureon.agents.specialized.institution.tools import (
    ResearchLabReaderTool,
    UniversityWebsiteReaderTool,
)
from aureon.agents.specialized.mentor.tools import (
    MentorProfileReaderTool,
    ResearchProfileReaderTool,
)
from aureon.agents.specialized.roadmap.tools import AdaptivePlanningTool, MilestonePlannerTool
from aureon.agents.tools.base import ToolStatus, run_tool_safely

#: Every tool that has no real infrastructure to act on yet, across every
#: specialist. None of these may ever claim a fabricated finding.
#: NOTE: URLReaderTool (V6), PDFReaderTool/ResumeReaderTool/
#: CurriculumReaderTool/AdmissionPDFReaderTool/PublicationReaderTool/
#: ResearchPaperReaderTool (V8, Document Intelligence), and
#: OpportunitySearchTool/InternshipSearchTool/ResearchOpportunitySearchTool/
#: CompetitionSearchTool (Phase 2 Stage 2, Opportunity Hub — now real
#: reads through providers/registry.py's fetch_all_safely) graduated to
#: real tools — each has its own test coverage elsewhere and is
#: deliberately excluded from this "still a stub" list.
STUB_TOOLS = [
    DocumentReaderTool, ImageUnderstandingTool, ChatExportReaderTool,
    BrowserInvestigationTool, SearchTool, TrendInvestigationTool,
    UniversityWebsiteReaderTool, ResearchLabReaderTool,
    MentorProfileReaderTool, ResearchProfileReaderTool,
    MilestonePlannerTool, AdaptivePlanningTool,
]


@pytest.mark.parametrize("tool_cls", STUB_TOOLS, ids=lambda cls: cls.name)
async def test_stub_tool_is_honest_never_fabricates(tool_cls):
    result = await run_tool_safely(tool_cls())

    assert result.status == ToolStatus.NOT_CONNECTED
    assert result.evidence == []  # no fabricated findings
    assert result.explanation  # must say exactly what's missing
