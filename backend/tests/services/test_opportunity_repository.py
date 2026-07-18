from aureon.domain.models.opportunity import Opportunity
from aureon.services.supabase.repositories.opportunity_repository import OpportunityRepository


def _opportunity(**overrides) -> Opportunity:
    defaults: dict = dict(
        id="opp_1", title="Test", category="internship", organization="Org", organization_kind="company",
        description="desc", location="Remote", is_remote=True, duration_label="8 weeks",
        official_link="https://example.com",
    )
    defaults.update(overrides)
    return Opportunity(**defaults)


class _FakeResult:
    def __init__(self, data):
        self.data = data


class _FakeQuery:
    def __init__(self, rows, single=False):
        self._rows = rows
        self._single = single

    def select(self, *_a, **_k):
        return self

    def eq(self, field, value):
        return _FakeQuery([r for r in self._rows if r.get(field) == value], single=self._single)

    def maybe_single(self):
        return _FakeQuery(self._rows, single=True)

    def execute(self):
        if self._single:
            return _FakeResult(self._rows[0] if self._rows else None)
        return _FakeResult(self._rows)


class _FakeUpsertExec:
    def __init__(self, result):
        self._result = result

    def execute(self):
        return self._result


class _FakeTable:
    def __init__(self, store: dict):
        self._store = store

    def select(self, *_a, **_k):
        return _FakeQuery(list(self._store.values()))

    def upsert(self, payload):
        self._store[payload["id"]] = payload
        return _FakeUpsertExec(_FakeResult(None))


class _FakeClient:
    def __init__(self, rows=None):
        self._store = {r["id"]: r for r in (rows or [])}

    def table(self, name):
        assert name == "opportunities"
        return _FakeTable(self._store)


async def test_list_opportunities_returns_parsed_models():
    client = _FakeClient(rows=[_opportunity().model_dump(mode="json")])
    repo = OpportunityRepository(client=client)

    result = await repo.list_opportunities()

    assert len(result) == 1
    assert result[0].id == "opp_1"


async def test_list_opportunities_filters_by_category():
    rows = [
        _opportunity(id="a", category="internship").model_dump(mode="json"),
        _opportunity(id="b", category="hackathon").model_dump(mode="json"),
    ]
    client = _FakeClient(rows=rows)
    repo = OpportunityRepository(client=client)

    result = await repo.list_opportunities(category="hackathon")

    assert [o.id for o in result] == ["b"]


async def test_list_opportunities_filters_by_country_in_python():
    rows = [_opportunity(id="a", countries=["Germany"], is_remote=False).model_dump(mode="json")]
    client = _FakeClient(rows=rows)
    repo = OpportunityRepository(client=client)

    assert len(await repo.list_opportunities(country="Germany")) == 1
    assert await repo.list_opportunities(country="France") == []


async def test_get_opportunity_returns_none_when_missing():
    client = _FakeClient(rows=[])
    repo = OpportunityRepository(client=client)
    assert await repo.get_opportunity("missing") is None


async def test_upsert_creates_a_new_row_at_version_one():
    client = _FakeClient(rows=[])
    repo = OpportunityRepository(client=client)

    result = await repo.upsert_opportunity(_opportunity())

    assert result.version == 1


async def test_upsert_is_idempotent_for_unchanged_content():
    client = _FakeClient(rows=[_opportunity(version=1).model_dump(mode="json")])
    repo = OpportunityRepository(client=client)

    result = await repo.upsert_opportunity(_opportunity(version=1))

    assert result.version == 1  # no bump — nothing actually changed


async def test_upsert_bumps_version_on_real_content_change():
    client = _FakeClient(rows=[_opportunity(version=1, title="Old Title").model_dump(mode="json")])
    repo = OpportunityRepository(client=client)

    result = await repo.upsert_opportunity(_opportunity(version=1, title="New Title"))

    assert result.version == 2
    assert result.title == "New Title"
