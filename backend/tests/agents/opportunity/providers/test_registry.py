import pytest

from aureon.agents.specialized.opportunity.providers import registry
from aureon.domain.models.opportunity import Opportunity
from tests.agents.opportunity._factories import make_opportunity


@pytest.fixture(autouse=True)
def _isolated_provider_list(monkeypatch):
    """Every test gets its own empty provider list — never pollutes the
    real module-level registry (which the seeded provider registers
    itself into at import time)."""
    monkeypatch.setattr(registry, "_PROVIDERS", [])
    yield


class _FakeProvider:
    def __init__(self, opportunities):
        self._opportunities = opportunities

    async def fetch_opportunities(self):
        return self._opportunities


class _FailingProvider:
    async def fetch_opportunities(self):
        raise RuntimeError("simulated provider failure")


class _MalformedProvider:
    async def fetch_opportunities(self):
        return [{"not": "a valid opportunity"}]


async def test_get_providers_returns_registered_providers():
    provider = _FakeProvider([make_opportunity(id="a")])
    registry.register_provider(provider)
    assert registry.get_providers() == [provider]


async def test_fetch_all_safely_aggregates_across_providers():
    registry.register_provider(_FakeProvider([make_opportunity(id="a")]))
    registry.register_provider(_FakeProvider([make_opportunity(id="b")]))

    result = await registry.fetch_all_safely()

    assert {o.id for o in result} == {"a", "b"}


async def test_fetch_all_safely_dedupes_by_id_last_write_wins():
    registry.register_provider(_FakeProvider([make_opportunity(id="a", title="First")]))
    registry.register_provider(_FakeProvider([make_opportunity(id="a", title="Second")]))

    result = await registry.fetch_all_safely()

    assert len(result) == 1
    assert result[0].title == "Second"


async def test_a_failing_provider_never_blocks_the_others():
    registry.register_provider(_FakeProvider([make_opportunity(id="a")]))
    registry.register_provider(_FailingProvider())

    result = await registry.fetch_all_safely()

    assert [o.id for o in result] == ["a"]


async def test_a_malformed_item_is_skipped_without_blocking_the_batch():
    registry.register_provider(_FakeProvider([make_opportunity(id="a")]))
    registry.register_provider(_MalformedProvider())

    result = await registry.fetch_all_safely()

    assert [o.id for o in result] == ["a"]


async def test_no_providers_returns_empty_list():
    assert await registry.fetch_all_safely() == []
