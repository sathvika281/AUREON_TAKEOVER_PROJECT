import pytest

from aureon.api import deps
from aureon.domain.models.career import CareerStory
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.domain._connect_factories import make_career_story, make_expert
from tests.domain._explore_factories import make_career
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


class _FakeJourneyStoryRepository:
    def __init__(self, stories: list[CareerStory]) -> None:
        self._stories = stories

    async def search_stories(
        self, *, q=None, career_id=None, industry=None, career_switch=None, story_type=None,
        discovery_theme=None, limit=100, offset=0,
    ):
        results = self._stories
        if career_id:
            results = [s for s in results if s.career_id == career_id]
        if industry:
            results = [s for s in results if s.industry == industry]
        if career_switch is not None:
            results = [s for s in results if s.career_switch == career_switch]
        if story_type:
            results = [s for s in results if s.story_type == story_type]
        if discovery_theme:
            results = [s for s in results if discovery_theme in s.discovery_themes]
        total = len(results)
        return results[offset : offset + limit], total

    async def get_story(self, story_id: str):
        return next((s for s in self._stories if s.id == story_id), None)

    async def list_filter_values(self, *, story_type=None):
        scoped = [s for s in self._stories if story_type is None or s.story_type == story_type]
        industries = sorted({s.industry for s in scoped if s.industry})
        career_ids = sorted({s.career_id for s in scoped if s.career_id})
        discovery_themes = sorted({t for s in scoped for t in s.discovery_themes})
        return industries, career_ids, discovery_themes


class _FakeCareerRepository:
    def __init__(self, careers) -> None:
        self._careers = careers

    async def get_career(self, career_id: str):
        return next((c for c in self._careers if c.id == career_id), None)

    async def list_careers(self, **_kwargs):
        return self._careers


class _FakeExpertRepository:
    def __init__(self, experts) -> None:
        self._experts = experts

    async def get_expert(self, expert_id: str):
        return next((e for e in self._experts if e.id == expert_id), None)


class _FakeLifeMissionRepository:
    async def get_mission(self, mission_id: str):
        return None


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    careers = [make_career(id="c1", name="Software Engineer", industry="technology")]
    experts = [make_expert(id="expert_1", name="Dr. Real Expert", profession="Researcher")]
    stories = [
        make_career_story(id="story_1", career_id="c1", industry="technology", career_switch=False),
        make_career_story(
            id="story_2", career_id="c1", industry="technology", career_switch=True,
            story_type="publicly_documented", source_reference="A real, checkable source.",
            linked_expert_id="expert_1",
        ),
        make_career_story(
            id="story_3", career_id="c1", industry="technology", career_switch=True,
            story_type="composite_student_discovery", discovery_themes=["found_my_passion"],
            trait_tags=["curious", "systems-thinking"],
        ),
        # A professional-only industry — proves list_filter_values genuinely
        # scopes by story_type rather than passing by fixture coincidence.
        # career_switch=True keeps it out of story_1's exact-count assertions
        # above, which target story_type="composite", career_switch=False.
        make_career_story(
            id="story_4", career_id="c1", industry="finance", story_type="composite", career_switch=True,
        ),
    ]
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})

    app.dependency_overrides[deps.get_journey_story_repository] = lambda: _FakeJourneyStoryRepository(stories)
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository(careers)
    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(experts)
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: _FakeLifeMissionRepository()
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    try:
        yield TestClient(app), fake_profiles
    finally:
        for dep in (
            deps.get_journey_story_repository, deps.get_career_repository, deps.get_expert_repository,
            deps.get_life_mission_repository, deps.get_student_profile_repository, deps.get_current_user_id,
        ):
            app.dependency_overrides.pop(dep, None)


def test_search_journey_stories_defaults_to_student_discovery_only(api_client):
    """The standalone screen's open, no-auth directory now defaults to
    student-discovery content — professional stories (story_1/story_2)
    stay off it by default."""
    client, _ = api_client
    response = client.get("/v1/journey-stories")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["stories"][0]["id"] == "story_3"
    assert body["stories"][0]["story_type"] == "composite_student_discovery"


def test_search_journey_stories_explicit_story_type_overrides_default(api_client):
    """Backward-compatible: tooling can still ask for professional stories
    explicitly."""
    client, _ = api_client
    response = client.get("/v1/journey-stories", params={"story_type": "composite", "career_switch": False})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["stories"][0]["id"] == "story_1"


def test_search_journey_stories_filters_by_career_switch_within_explicit_type(api_client):
    client, _ = api_client
    response = client.get(
        "/v1/journey-stories", params={"story_type": "publicly_documented", "career_switch": True}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["stories"][0]["id"] == "story_2"


def test_search_journey_stories_filters_by_discovery_theme(api_client):
    client, _ = api_client
    response = client.get("/v1/journey-stories", params={"discovery_theme": "found_my_passion"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["stories"][0]["id"] == "story_3"


def test_get_journey_story_resolves_career_name_and_linked_expert(api_client):
    client, _ = api_client
    response = client.get("/v1/journey-stories/story_2")
    assert response.status_code == 200
    body = response.json()
    assert body["career_name"] == "Software Engineer"
    assert body["story_type"] == "publicly_documented"
    assert body["source_reference"] == "A real, checkable source."
    assert body["linked_expert"]["name"] == "Dr. Real Expert"


def test_get_journey_story_404_for_unknown_story(api_client):
    client, _ = api_client
    response = client.get("/v1/journey-stories/does_not_exist")
    assert response.status_code == 404


def test_get_journey_story_filters_returns_distinct_industries_careers_and_themes(api_client):
    client, _ = api_client
    response = client.get("/v1/journey-stories/filters")
    assert response.status_code == 200
    body = response.json()
    assert "technology" in body["industries"]
    assert body["careers"][0]["name"] == "Software Engineer"
    assert body["discovery_themes"] == ["found_my_passion"]


def test_get_journey_story_filters_never_offers_a_professional_only_option(api_client):
    """"finance" only appears on story_4 (story_type="composite") — a
    student-discovery filter must never offer it, since selecting it
    would return zero results on the screen that actually shows it."""
    client, _ = api_client
    response = client.get("/v1/journey-stories/filters")
    assert response.status_code == 200
    assert "finance" not in response.json()["industries"]


def test_relevant_stories_requires_the_authenticated_student(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/someone-else/journey-stories/relevant")
    assert response.status_code == 403


def test_relevant_stories_returns_empty_without_real_world_signals(api_client):
    """Never fabricate a "you may relate to this" claim with zero real
    signal to back it."""
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/journey-stories/relevant")
    assert response.status_code == 200
    assert response.json()["stories"] == []


def test_reflect_on_journey_story_persists_to_reflection_journal(api_client):
    client, fake_profiles = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/journey-stories/story_3/reflect",
        json={"prompt": "Did anything in this story feel familiar?", "response": "Yes, the uncertainty part."},
    )
    assert response.status_code == 200
    assert response.json()["recorded"] is True

    saved = fake_profiles.saved[-1]
    assert len(saved.reflection_journal) == 1
    entry = saved.reflection_journal[0]
    assert entry.prompt == "Did anything in this story feel familiar?"
    assert entry.response == "Yes, the uncertainty part."
    # Reading/reflecting on a story never touches these directly.
    assert saved.evidence_graph == []
    assert saved.career_exploration_history == []


def test_reflect_on_journey_story_404_for_unknown_story(api_client):
    client, _ = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/journey-stories/does-not-exist/reflect",
        json={"prompt": "x", "response": "y"},
    )
    assert response.status_code == 404


def test_reflect_on_journey_story_requires_the_authenticated_student(api_client):
    client, _ = api_client
    response = client.post(
        "/v1/students/someone-else/journey-stories/story_3/reflect",
        json={"prompt": "x", "response": "y"},
    )
    assert response.status_code == 403
