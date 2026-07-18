from aureon.agents.specialized.opportunity.providers.registry import fetch_all_safely
from aureon.agents.tools.base import Evidence, Tool, ToolResult, ToolStatus
from aureon.domain.models.opportunity import Opportunity, OpportunityCategory

#: Opportunity owns these because they're all about continuously finding,
#: filtering, and ranking real-world opportunities — matches
#: OpportunityAgent's real ownership (see agent.py). Each tool now reads
#: through the real Provider aggregation (providers/registry.py's
#: fetch_all_safely) rather than a direct repository call, keeping the
#: tools honest about the same abstraction the agent itself uses.


def _to_evidence(opportunity: Opportunity) -> Evidence:
    return Evidence(
        source="opportunity_knowledge_base",
        summary=f"{opportunity.title} ({opportunity.organization}, {opportunity.category})",
        source_type="opportunity",
        title=opportunity.title,
    )


async def _search(category: OpportunityCategory | None = None) -> list[Evidence]:
    opportunities = await fetch_all_safely()
    if category is not None:
        opportunities = [o for o in opportunities if o.category == category]
    return [_to_evidence(o) for o in opportunities]


class OpportunitySearchTool(Tool):
    name = "opportunity_search"
    description = "Searches for opportunities (internships, scholarships, competitions, research, jobs)."

    async def execute(self, **kwargs) -> ToolResult:
        evidence = await _search()
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=evidence,
            explanation=f"Found {len(evidence)} opportunities across the Opportunity Knowledge Base.",
        )


class InternshipSearchTool(Tool):
    name = "internship_search"
    description = "Searches specifically for internships matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        evidence = await _search(category="internship")
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=evidence,
            explanation=f"Found {len(evidence)} internship listings in the Opportunity Knowledge Base.",
        )


class ResearchOpportunitySearchTool(Tool):
    name = "research_opportunity_search"
    description = "Searches for research opportunities matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        evidence = await _search(category="research_program")
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=evidence,
            explanation=f"Found {len(evidence)} research program listings in the Opportunity Knowledge Base.",
        )


class CompetitionSearchTool(Tool):
    name = "competition_search"
    description = "Searches for competitions matching the student's Career DNA."

    async def execute(self, **kwargs) -> ToolResult:
        evidence = await _search(category="competition")
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=evidence,
            explanation=f"Found {len(evidence)} competition listings in the Opportunity Knowledge Base.",
        )
