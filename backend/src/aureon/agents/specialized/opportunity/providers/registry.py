"""Responsibility: the registration mechanism for "which Opportunity
Providers exist" (mirrors agents/foundation/objective_registry.py's
`register_*`/`get_*` pattern exactly), plus resilient aggregation across
all of them. Owns: the provider list and `fetch_all_safely`. Does NOT
own: any provider's own fetch logic. Consumed by:
`opportunity_objective_plans.py`'s resource loading.

Resilience: a provider will eventually be a real external system that
can fail, time out, or return malformed data. `fetch_all_safely` mirrors
`agents/tools/base.py::run_tool_safely`'s exact isolation philosophy —
the same principle already used twice in this codebase (tools, Event
Bus subscribers) — one provider failing must never stop Opportunity Hub.
"""

import asyncio
import logging
from typing import Any

from aureon.agents.specialized.opportunity.providers.base import OpportunityProvider
from aureon.domain.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

_PROVIDERS: list[OpportunityProvider] = []

_DEFAULT_TIMEOUT_SECONDS = 10.0


def register_provider(provider: OpportunityProvider) -> None:
    _PROVIDERS.append(provider)


def get_providers() -> list[OpportunityProvider]:
    return list(_PROVIDERS)


async def fetch_all_safely(*, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> list[Opportunity]:
    """Aggregates every registered provider's opportunities, de-duped by
    id (last-write-wins). A provider that raises, times out, or returns
    a malformed item is logged and skipped — it never prevents the
    remaining providers' real opportunities from coming through."""
    seen: dict[str, Opportunity] = {}
    for provider in get_providers():
        try:
            raw: Any = await asyncio.wait_for(provider.fetch_opportunities(), timeout=timeout_seconds)
        except Exception:
            logger.exception(
                "Opportunity provider %s failed or timed out — skipping it", type(provider).__name__
            )
            continue
        for item in raw:
            try:
                opportunity = item if isinstance(item, Opportunity) else Opportunity.model_validate(item)
            except Exception:
                logger.exception(
                    "Malformed opportunity from provider %s — skipping it", type(provider).__name__
                )
                continue
            seen[opportunity.id] = opportunity
    return list(seen.values())
