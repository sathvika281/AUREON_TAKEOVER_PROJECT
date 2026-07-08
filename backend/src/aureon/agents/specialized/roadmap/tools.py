from aureon.agents.tools.base import Tool, ToolResult, ToolStatus

#: Roadmap owns these because they're all about planning and adapting a
#: student's milestone sequence — matches RoadmapAgent's existing honest
#: no-op status (see agent.py); no persisted roadmap data model exists yet.


class MilestonePlannerTool(Tool):
    name = "milestone_planner"
    description = "Plans concrete milestones from a student's skill gaps and career direction."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No persisted roadmap or skill-gap data exists yet — this tool is wired into "
            "Roadmap's toolset and ready for one.",
        )


class AdaptivePlanningTool(Tool):
    name = "adaptive_planning"
    description = "Replans a roadmap's milestones as new evidence arrives."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.NOT_CONNECTED,
            explanation="No persisted roadmap exists yet to adapt — this tool is wired into Roadmap's "
            "toolset and ready for one.",
        )
