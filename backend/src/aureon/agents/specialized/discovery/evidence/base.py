from abc import ABC, abstractmethod
from typing import ClassVar

from aureon.agents.specialized.discovery.evidence.registry import EvidenceSourceRegistry
from aureon.agents.state import AureonState
from aureon.domain.models.student_profile import ExplorationEvent


class EvidenceSource(ABC):
    """Contract for a single pluggable source of evidence the Discovery
    Agent can draw on: conversation turns, guided reflections,
    micro-challenges, exploration activities, behavioral patterns, student
    feedback, mentor feedback, and whatever else is added later.

    Subclassing auto-registers via ``__init_subclass__``, mirroring
    ``BaseAgent``'s pattern one level down — a new evidence source is added
    by creating one new module here, with zero changes to the Discovery
    Agent itself or to any other evidence source.

    This scaffold defines only the extension point. No concrete evidence
    source is implemented yet: the Discovery Agent has no real inference
    logic in this phase, so a stub "conversation evidence source" would be
    exactly the kind of fake workflow this project avoids. Concrete
    sources are implemented in the Discovery Agent's dedicated module.
    """

    name: ClassVar[str]
    description: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "name", None) or not getattr(cls, "description", None):
            raise TypeError(
                f"{cls.__name__} must define non-empty 'name' and 'description' "
                "class attributes before it can self-register"
            )
        EvidenceSourceRegistry.register(cls)

    @abstractmethod
    async def extract(self, state: AureonState) -> list[ExplorationEvent]:
        """Return zero or more ``ExplorationEvent``s inferred from the
        current state. The Discovery Agent aggregates events from every
        registered source rather than depending on any single one."""
        raise NotImplementedError
