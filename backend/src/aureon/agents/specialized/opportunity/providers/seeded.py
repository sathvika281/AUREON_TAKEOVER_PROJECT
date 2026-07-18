"""The first, and today the only, real OpportunityProvider — wraps the
seeded Opportunity Knowledge Base (OpportunityRepository). Not a special
case: a future provider implements the exact same protocol
(providers/base.py) and registers itself the same way (see
providers/__init__.py)."""

from aureon.domain.models.opportunity import Opportunity
from aureon.services.supabase.repositories.opportunity_repository import OpportunityRepository


class SeededKnowledgeBaseProvider:
    def __init__(self, repository: OpportunityRepository | None = None) -> None:
        self._repository = repository or OpportunityRepository()

    async def fetch_opportunities(self) -> list[Opportunity]:
        return await self._repository.list_opportunities()
