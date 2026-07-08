from typing import Any, AsyncIterator

from groq import AsyncGroq

from aureon.services.llm.schemas import (
    LLMChunk,
    LLMMessage,
    LLMResponse,
    LLMTool,
    LLMToolCall,
)


def _to_groq_messages(messages: list[LLMMessage]) -> list[dict[str, Any]]:
    return [m.model_dump(exclude_none=True) for m in messages]


def _to_groq_tools(tools: list[LLMTool] | None) -> list[dict[str, Any]] | None:
    if not tools:
        return None
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in tools
    ]


def _request_kwargs(
    *, tools: list[LLMTool] | None, tool_choice: str | None
) -> dict[str, Any]:
    """Only includes ``tools``/``tool_choice`` when actually provided —
    passing an explicit ``None`` through to the SDK (vs. omitting the
    keyword) risks serializing as JSON ``null``, which some backends
    reject for these particular parameters."""
    kwargs: dict[str, Any] = {}
    groq_tools = _to_groq_tools(tools)
    if groq_tools is not None:
        kwargs["tools"] = groq_tools
    if tool_choice is not None:
        kwargs["tool_choice"] = tool_choice
    return kwargs


class GroqClient:
    """Concrete ``LLMClient`` implementation backed by Groq's chat
    completions API. This is the only adapter this phase implements for
    real (it is infrastructure, not a product feature) — it absorbs every
    Groq-specific shape so agent/orchestrator code only ever depends on the
    provider-agnostic ``LLMClient`` protocol.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncGroq(api_key=api_key)
        self._model = model

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=_to_groq_messages(messages),
            temperature=temperature,
            **_request_kwargs(tools=tools, tool_choice=tool_choice),
        )
        choice = response.choices[0]
        tool_calls = [
            LLMToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=_safe_json(tc.function.arguments),
            )
            for tc in (choice.message.tool_calls or [])
        ]
        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            raw=response.model_dump(),
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        tools: list[LLMTool] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[LLMChunk]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=_to_groq_messages(messages),
            temperature=temperature,
            stream=True,
            **_request_kwargs(tools=tools, tool_choice=tool_choice),
        )
        async for event in stream:
            delta = event.choices[0].delta.content or ""
            finished = event.choices[0].finish_reason is not None
            yield LLMChunk(delta=delta, done=finished)


def _safe_json(raw_arguments: str) -> dict[str, Any]:
    import json

    try:
        return json.loads(raw_arguments)
    except (json.JSONDecodeError, TypeError):
        return {}
