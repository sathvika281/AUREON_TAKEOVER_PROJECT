from aureon.domain.models.institution import Institution
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository


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
    def __init__(self, institutions_rows=None, labs_rows=None, orgs_rows=None, programs_rows=None):
        self._tables = {
            "institutions": institutions_rows or [],
            "research_labs": labs_rows or [],
            "student_organizations": orgs_rows or [],
            "academic_programs": programs_rows or [],
        }

    def table(self, name):
        return _FakeTable(self._tables[name])


def _institution_row(**overrides) -> dict:
    inst = Institution(
        id="inst_1", name="Test University", country="Testland", city="Test City",
        research_culture="x", innovation_ecosystem="x", industry_collaboration="x",
        placements="x", learning_environment="x", trait_tags=["curiosity"],
    )
    data = inst.model_dump(mode="json")
    data.update(overrides)
    return data


async def test_list_institutions_returns_parsed_models():
    client = _FakeClient(institutions_rows=[_institution_row()])
    repo = InstitutionRepository(client=client)

    institutions = await repo.list_institutions()

    assert len(institutions) == 1
    assert institutions[0].id == "inst_1"


async def test_list_research_labs_for_institution():
    lab_row = {"id": "lab_1", "institution_id": "inst_1", "name": "Test Lab", "focus_area": "x", "description": "x"}
    client = _FakeClient(labs_rows=[lab_row])
    repo = InstitutionRepository(client=client)

    labs = await repo.list_research_labs("inst_1")

    assert len(labs) == 1
    assert labs[0].name == "Test Lab"
