from typing import Any, Literal

from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Provider-agnostic chat message. Adapter classes (e.g. GroqClient)
    translate to/from this shape so agent code never touches a
    provider-specific message format."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None


class LLMToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class LLMTool(BaseModel):
    """Provider-agnostic tool/function definition passed to `LLMClient.complete`."""

    name: str
    description: str
    parameters: dict[str, Any]


class LLMResponse(BaseModel):
    content: str | None
    tool_calls: list[LLMToolCall] = []
    raw: dict[str, Any] | None = None  # original provider payload, for debugging only


class LLMChunk(BaseModel):
    """A single streamed delta."""

    delta: str
    done: bool = False
