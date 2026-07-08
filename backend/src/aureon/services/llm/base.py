from typing import AsyncIterator, Protocol

from aureon.services.llm.schemas import LLMChunk, LLMMessage, LLMResponse, LLMTool


class LLMClient(Protocol):
    """Provider-agnostic LLM interface. Agents and the orchestrator planner
    depend only on this protocol, never on a concrete provider class —
    swapping providers means writing one new adapter (see
    ``services/llm/providers/``) plus one branch in ``factory.py``; no
    agent code changes.
    """

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse: ...

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[LLMChunk]: ...
