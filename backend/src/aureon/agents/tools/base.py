from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class ToolStatus(StrEnum):
    """Terminal states only — every tool call's lifecycle is Queued ->
    Running -> one of these three. Never a fourth ad-hoc status; a
    specialist deciding "what to do next" only ever needs to distinguish
    these three outcomes."""

    COMPLETED = "completed"
    FAILED = "failed"
    NOT_CONNECTED = "not_connected"


class Evidence(BaseModel):
    """Structured evidence a tool produced — specialists consume this,
    never a tool's raw output directly.

    ``source_type``/``title``/``confidence``/``metadata`` were added in
    V6 (URL Intelligence) additively — every V4/V5 ``Evidence(...)``
    construction that doesn't set them keeps working unchanged."""

    source: str
    summary: str
    reliability: str | None = None
    source_type: str | None = None
    title: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolResult(BaseModel):
    """Every tool invocation's outcome, regardless of which tool ran.
    ``lifecycle`` always records the real Queued -> Running -> <terminal>
    transitions ``run_tool_safely`` put this result through — never
    decorative. ``explanation`` is required context whenever ``status``
    isn't COMPLETED: what's missing, or what went wrong, in plain
    language — never a bare failure with no reason given."""

    tool_name: str
    status: ToolStatus
    lifecycle: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    explanation: str | None = None


class Tool(ABC):
    """Contract every specialist's own tool implements. Deliberately not
    self-registering anywhere (no ToolRegistry, no central manager) — a
    specialist's ``tools.py`` module just defines these directly, and that
    specialist's own code instantiates and calls them. The Mission
    Orchestrator never imports this module or any specialist's tools."""

    name: ClassVar[str]
    description: ClassVar[str]

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError


async def run_tool_safely(tool: Tool, **kwargs: Any) -> ToolResult:
    """The single place every specialist calls a tool through — never
    ``tool.execute()`` directly. Records the Queued -> Running transition
    before invoking, then either passes through the tool's own honest
    Completed/Not-Connected result, or converts any unexpected exception
    into a Failed result rather than letting it propagate — a tool
    failure must never crash a mission."""
    lifecycle = ["queued", "running"]
    try:
        result = await tool.execute(**kwargs)
        result.lifecycle = [*lifecycle, result.status.value]
        return result
    except Exception as exc:  # noqa: BLE001 — deliberately broad: any tool failure must be contained here
        return ToolResult(
            tool_name=tool.name,
            status=ToolStatus.FAILED,
            lifecycle=[*lifecycle, ToolStatus.FAILED.value],
            explanation=str(exc),
        )
