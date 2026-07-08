from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from aureon.agents.specialized.discovery.evidence.base import EvidenceSource


class EvidenceSourceRegistry:
    """Registry of every pluggable evidence source the Discovery Agent can
    draw on. Populated entirely by self-registration (see
    ``EvidenceSource.__init_subclass__``) — the same pattern as
    ``AgentRegistry``, one level down, so new evidence sources plug in
    without modifying the Discovery Agent or any existing source.
    """

    _classes: ClassVar[dict[str, type["EvidenceSource"]]] = {}

    @classmethod
    def register(cls, source_cls: type["EvidenceSource"]) -> None:
        cls._classes[source_cls.name] = source_cls

    @classmethod
    def all(cls) -> list[type["EvidenceSource"]]:
        return list(cls._classes.values())

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._classes.keys())
