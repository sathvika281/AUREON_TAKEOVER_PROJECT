from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from aureon.agents.base import BaseAgent


@dataclass(frozen=True)
class AgentDescriptor:
    name: str
    description: str
    is_recommendation_stage: bool


class AgentRegistry:
    """Central lookup of every specialized agent, populated entirely by
    self-registration (see ``BaseAgent.__init_subclass__``).

    The orchestrator graph and the planner node both read from this
    registry instead of importing specialized agent modules directly. That
    indirection is what lets a new agent (Research, Scholarship, Resume,
    Interview, Portfolio, Internship, Market Trends, ...) be added later by
    creating one new module under ``agents/specialized/`` — with zero edits
    to the orchestrator or any existing agent.
    """

    _classes: ClassVar[dict[str, type["BaseAgent"]]] = {}
    _instances: ClassVar[dict[str, "BaseAgent"]] = {}

    @classmethod
    def register(cls, agent_cls: type["BaseAgent"]) -> None:
        cls._classes[agent_cls.name] = agent_cls

    @classmethod
    def get(cls, name: str) -> "BaseAgent":
        if name not in cls._classes:
            raise KeyError(f"No agent registered under name '{name}'")
        if name not in cls._instances:
            cls._instances[name] = cls._classes[name]()
        return cls._instances[name]

    @classmethod
    def describe_all(cls) -> list[AgentDescriptor]:
        return [
            AgentDescriptor(
                name=agent_cls.name,
                description=agent_cls.description,
                is_recommendation_stage=agent_cls.is_recommendation_stage,
            )
            for agent_cls in cls._classes.values()
        ]

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._classes.keys())
