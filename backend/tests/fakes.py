from typing import Any, AsyncIterator

from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.schemas import LLMChunk, LLMMessage, LLMResponse, LLMTool, LLMToolCall


def tool_call_response(tool_name: str, arguments: dict[str, Any]) -> LLMResponse:
    """Builds an ``LLMResponse`` shaped like a real provider's tool-call
    reply, for feeding into ``FakeLLMClient``."""
    return LLMResponse(
        content=None,
        tool_calls=[LLMToolCall(id="fake-call-1", name=tool_name, arguments=arguments)],
    )


class FakeLLMClient:
    """Test double implementing the ``LLMClient`` protocol. Returns queued
    canned responses in order, recording every call so tests can assert on
    what was sent (messages, tools, tool_choice) without ever hitting a
    real provider.
    """

    def __init__(self, responses: list[LLMResponse] | None = None) -> None:
        self._responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        self.calls.append(
            {"messages": messages, "tools": tools, "tool_choice": tool_choice}
        )
        if self._responses:
            return self._responses.pop(0)
        return LLMResponse(content="", tool_calls=[])

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[LLMChunk]:
        yield LLMChunk(delta="", done=True)


class FakeStudentProfileRepository:
    """In-memory test double for StudentProfileRepository — no Supabase
    client, no network. Seed ``profiles`` with pre-built StudentProfile
    instances keyed by student_id; ``get_or_create`` falls back to a
    fresh profile exactly like the real repository does for a new
    student."""

    def __init__(self, profiles: dict[str, StudentProfile] | None = None) -> None:
        self._profiles = dict(profiles or {})
        self.saved: list[StudentProfile] = []

    async def get_or_create(self, student_id: str) -> StudentProfile:
        if student_id not in self._profiles:
            self._profiles[student_id] = StudentProfile(student_id=student_id)
        return self._profiles[student_id]

    async def save(self, profile: StudentProfile) -> None:
        self._profiles[profile.student_id] = profile
        self.saved.append(profile)
