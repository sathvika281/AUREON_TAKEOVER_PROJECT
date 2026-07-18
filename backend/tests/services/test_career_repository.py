from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.services.supabase.repositories.career_repository import CareerRepository

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)


class _FakeQuery:
    def __init__(self, rows, calls=None):
        self._rows = rows
        self.calls = calls if calls is not None else []

    def select(self, *_a, **_k):
        return self

    def eq(self, *_a, **_k):
        self.calls.append(("eq", _a, _k))
        return self

    def in_(self, *_a, **_k):
        self.calls.append(("in_", _a, _k))
        return self

    def ilike(self, *_a, **_k):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        class _Result:
            def __init__(self, data):
                self.data = data

        # maybe_single() on zero rows returns None outright in this
        # supabase-py version; simulate the single-row case as first match.
        if self._rows and len(self._rows) == 1 and isinstance(self._rows, list):
            pass
        return _Result(self._rows)


class _FakeTable:
    def __init__(self, rows):
        self._rows = rows
        self.calls: list = []

    def select(self, *_a, **_k):
        return _FakeQuery(self._rows, calls=self.calls)


class _FakeClient:
    def __init__(self, careers_rows=None, stories_rows=None):
        self._careers_rows = careers_rows or []
        self._stories_rows = stories_rows or []
        self.tables: dict = {}

    def table(self, name):
        if name == "careers":
            self.tables[name] = _FakeTable(self._careers_rows)
        elif name == "career_stories":
            self.tables[name] = _FakeTable(self._stories_rows)
        else:
            raise AssertionError(f"unexpected table {name}")
        return self.tables[name]


def _career_row(**overrides) -> dict:
    career = Career(
        id="physician_general", name="Physician", category="traditional", industry="healthcare",
        one_liner="x", reality=_REALITY, future_lens=_FUTURE,
    )
    data = career.model_dump(mode="json")
    data.update(overrides)
    return data


async def test_list_careers_returns_parsed_models():
    client = _FakeClient(careers_rows=[_career_row()])
    repo = CareerRepository(client=client)

    careers = await repo.list_careers()

    assert len(careers) == 1
    assert careers[0].id == "physician_general"


async def test_list_careers_filters_by_country_client_side():
    client = _FakeClient(
        careers_rows=[
            _career_row(id="global_one", countries=[]),
            _career_row(id="india_only", countries=["India"]),
            _career_row(id="japan_only", countries=["Japan"]),
        ]
    )
    repo = CareerRepository(client=client)

    careers = await repo.list_careers(country="India")

    ids = {c.id for c in careers}
    assert ids == {"global_one", "india_only"}


async def test_list_stories_for_career_returns_parsed_models():
    story_row = {
        "id": "story_1", "career_id": "physician_general", "person_label": "Doctor, 5 years",
        "background": "x", "journey": "x", "challenges": "x", "turning_points": "x",
        "advice": "x", "lessons_learned": "x", "trait_tags": [],
    }
    client = _FakeClient(stories_rows=[story_row])
    repo = CareerRepository(client=client)

    stories = await repo.list_stories_for_career("physician_general")

    assert len(stories) == 1
    assert stories[0].person_label == "Doctor, 5 years"


async def test_list_stories_for_career_scopes_to_professional_story_types():
    """Expert Connect / Journey Stories purpose split — "Human Stories"
    must never silently pick up composite_student_discovery rows."""
    story_row = {
        "id": "story_1", "career_id": "physician_general", "person_label": "Doctor, 5 years",
        "background": "x", "journey": "x", "challenges": "x", "turning_points": "x",
        "advice": "x", "lessons_learned": "x", "trait_tags": [],
    }
    client = _FakeClient(stories_rows=[story_row])
    repo = CareerRepository(client=client)

    await repo.list_stories_for_career("physician_general")

    calls = client.tables["career_stories"].calls
    in_calls = [c for c in calls if c[0] == "in_"]
    assert len(in_calls) == 1
    _, args, _kwargs = in_calls[0]
    assert args[0] == "story_type"
    assert set(args[1]) == {"composite", "publicly_documented"}
