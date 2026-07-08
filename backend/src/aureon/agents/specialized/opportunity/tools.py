from aureon.agents.tools.base import Tool, ToolResult, ToolStatus

#: Opportunity owns these because they're all about continuously finding,
#: filtering, and ranking real-world opportunities — matches
#: OpportunityAgent's existing honest no-op status (see agent.py).


class OpportunitySearchTool(Tool):
    name = "opportunity_search"
    description = "Searches for opportunities (internships, scholarships, competitions, research, jobs)."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No opportunity data source is configured yet — this tool is wired into "
            "Opportunity's toolset and ready for one.",
        )


class InternshipSearchTool(Tool):
    name = "internship_search"
    description = "Searches specifically for internships matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No internship data source is configured yet — this tool is wired into "
            "Opportunity's toolset and ready for one.",
        )


class ResearchOpportunitySearchTool(Tool):
    name = "research_opportunity_search"
    description = "Searches for research opportunities matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No research-opportunity data source is configured yet — this tool is wired "
            "into Opportunity's toolset and ready for one.",
        )


class CompetitionSearchTool(Tool):
    name = "competition_search"
    description = "Searches for competitions matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No competition data source is configured yet — this tool is wired into "
            "Opportunity's toolset and ready for one.",
        )
