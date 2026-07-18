"""Responsibility: the contract every Opportunity data source implements.
Owns: the `OpportunityProvider` protocol. Does NOT own: any specific
data source's fetch logic (seeded.py, or a future DevpostProvider/
MLHProvider/etc.) — this module only defines the shape. Consumed by:
`registry.py`'s aggregation.

Why providers are abstracted: OpportunityAgent must consume providers,
never a database directly, so future data sources (Devpost, MLH, Google
Summer of Code, Hugging Face, university research programs, company
career pages, government/scholarship providers) can plug in later
without touching agent logic. The seeded Knowledge Base (seeded.py) is
the first implementation, not a special case.
"""

from typing import Protocol

from aureon.domain.models.opportunity import Opportunity


class OpportunityProvider(Protocol):
    async def fetch_opportunities(self) -> list[Opportunity]: ...
