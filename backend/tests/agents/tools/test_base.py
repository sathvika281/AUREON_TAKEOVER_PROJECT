from aureon.agents.tools.base import Evidence, Tool, ToolResult, ToolStatus, run_tool_safely


class _CompletedTool(Tool):
    name = "completed_tool"
    description = "A tool that succeeds."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            evidence=[Evidence(source="test", summary="found something")],
        )


class _NotConnectedTool(Tool):
    name = "not_connected_tool"
    description = "A tool with no backend configured."

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name, status=ToolStatus.NOT_CONNECTED, explanation="No backend configured."
        )


class _ExplodingTool(Tool):
    name = "exploding_tool"
    description = "A tool whose execute() raises."

    async def execute(self, **kwargs) -> ToolResult:
        raise RuntimeError("network unreachable")


async def test_run_tool_safely_records_real_lifecycle_for_completed_tool():
    result = await run_tool_safely(_CompletedTool())

    assert result.status == ToolStatus.COMPLETED
    assert result.lifecycle == ["queued", "running", "completed"]
    assert result.evidence[0].summary == "found something"


async def test_run_tool_safely_passes_through_not_connected_honestly():
    result = await run_tool_safely(_NotConnectedTool())

    assert result.status == ToolStatus.NOT_CONNECTED
    assert result.lifecycle == ["queued", "running", "not_connected"]
    assert result.explanation == "No backend configured."
    assert result.evidence == []


async def test_run_tool_safely_converts_exception_to_failed_never_raises():
    result = await run_tool_safely(_ExplodingTool())

    assert result.status == ToolStatus.FAILED
    assert result.lifecycle == ["queued", "running", "failed"]
    assert "network unreachable" in result.explanation
