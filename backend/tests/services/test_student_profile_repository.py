from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        return self._result


class _FakeUpsertExec:
    def execute(self):
        return None


class _FakeTable:
    def __init__(self, parent):
        self._parent = parent

    def select(self, *_args, **_kwargs):
        return _FakeQuery(self._parent.select_result)

    def upsert(self, payload):
        self._parent.upserted.append(payload)
        return _FakeUpsertExec()


class _FakeSupabaseClient:
    """Mimics the exact chained-builder shape this repository calls:
    ``.table(...).select(...).eq(...).maybe_single().execute()``. In the
    installed supabase-py version, ``maybe_single().execute()`` returns
    ``None`` outright (not a response object with ``data=None``) when zero
    rows match — this double reproduces that real behavior.
    """

    def __init__(self, select_result):
        self.select_result = select_result
        self.upserted: list[dict] = []

    def table(self, _name):
        return _FakeTable(self)


async def test_get_or_create_handles_no_matching_row_without_crashing():
    client = _FakeSupabaseClient(select_result=None)
    repo = StudentProfileRepository(client=client)

    profile = await repo.get_or_create("new-student")

    assert profile.student_id == "new-student"
    assert len(client.upserted) == 1  # the new profile was saved


async def test_get_or_create_returns_existing_profile_when_row_found():
    class _Response:
        data = {"student_id": "existing-student"}

    client = _FakeSupabaseClient(select_result=_Response())
    repo = StudentProfileRepository(client=client)

    profile = await repo.get_or_create("existing-student")

    assert profile.student_id == "existing-student"
    assert len(client.upserted) == 0  # no need to create/save
