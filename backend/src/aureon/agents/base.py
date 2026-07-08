from abc import ABC, abstractmethod
from typing import ClassVar

from aureon.agents.registry import AgentRegistry
from aureon.agents.state import AureonState
from aureon.services.llm.base import LLMClient


class BaseAgent(ABC):
    """Contract every specialized agent implements.

    Subclassing this automatically registers the agent in ``AgentRegistry``
    the moment its module is imported (see ``__init_subclass__``) — no
    decorator, no manual registration call, and no change to the
    orchestrator required when a new agent is added.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    is_recommendation_stage: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if ABC in cls.__bases__:
            # Direct abstract subclasses (if any are introduced later) opt
            # out of registration by inheriting ABC again explicitly.
            return
        if not getattr(cls, "name", None) or not getattr(cls, "description", None):
            raise TypeError(
                f"{cls.__name__} must define non-empty 'name' and 'description' "
                "class attributes before it can self-register"
            )
        AgentRegistry.register(cls)

    @abstractmethod
    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        """Read whatever shared state fields this agent needs, do its work,
        and return the (possibly mutated) state. Agents should only write to
        their own entry in ``state['agent_outputs']`` plus the specific
        shared fields they own by contract (e.g. Discovery owns
        ``student_profile``/``confidence_score``).

        ``llm`` is injected by the orchestrator graph (mirrors how
        ``planner_node`` receives it) rather than constructed by the agent
        itself, so agents stay provider-agnostic and easy to test with a
        fake client.
        """
        raise NotImplementedError
