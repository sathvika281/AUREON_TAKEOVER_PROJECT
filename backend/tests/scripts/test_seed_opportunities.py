from aureon.scripts import seed_opportunities
from aureon.services.supabase.repositories.opportunity_repository import OpportunityRepository


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


class _FakeTable:
    def __init__(self, store: dict):
        self._store = store

    def select(self, *_a, **_k):
        return _FakeQuery(list(self._store.values()))

    def upsert(self, payload):
        self._store[payload["id"]] = payload
        return self

    def execute(self):
        return _FakeResult(None)


class _FakeClient:
    def __init__(self):
        self.store: dict = {}

    def table(self, name):
        assert name == "opportunities"
        return _FakeTable(self.store)


async def test_seed_is_idempotent_no_duplicate_rows_on_rerun(monkeypatch):
    client = _FakeClient()
    monkeypatch.setattr(seed_opportunities, "OpportunityRepository", lambda: OpportunityRepository(client=client))

    await seed_opportunities.seed()
    await seed_opportunities.seed()

    assert len(client.store) == len(seed_opportunities.OPPORTUNITIES)


async def test_seed_produces_no_version_bump_on_unchanged_rerun(monkeypatch):
    client = _FakeClient()
    monkeypatch.setattr(seed_opportunities, "OpportunityRepository", lambda: OpportunityRepository(client=client))

    await seed_opportunities.seed()
    first_versions = {row["id"]: row["version"] for row in client.store.values()}

    await seed_opportunities.seed()
    second_versions = {row["id"]: row["version"] for row in client.store.values()}

    assert first_versions == second_versions
