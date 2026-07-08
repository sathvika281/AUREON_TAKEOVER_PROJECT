from aureon.domain.models.mentor import Mentor
from aureon.services.supabase.repositories.mentor_repository import MentorRepository


class _FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def select(self, *_a, **_k):
        return self

    def eq(self, *_a, **_k):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        class _Result:
            def __init__(self, data):
                self.data = data
        return _Result(self._rows)


class _FakeTable:
    def __init__(self, rows):
        self._rows = rows

    def select(self, *_a, **_k):
        return _FakeQuery(self._rows)


class _FakeClient:
    def __init__(self, rows=None):
        self._rows = rows or []

    def table(self, name):
        assert name == "mentors"
        return _FakeTable(self._rows)


def _mentor_row(**overrides) -> dict:
    mentor = Mentor(
        id="mentor_1", name="Dr. Test", role_type="professor", field="AI",
        bio="x", trait_tags=["curiosity"], learning_style_fit="x",
    )
    data = mentor.model_dump(mode="json")
    data.update(overrides)
    return data


async def test_list_mentors_returns_parsed_models():
    client = _FakeClient(rows=[_mentor_row()])
    repo = MentorRepository(client=client)

    mentors = await repo.list_mentors()

    assert len(mentors) == 1
    assert mentors[0].id == "mentor_1"
