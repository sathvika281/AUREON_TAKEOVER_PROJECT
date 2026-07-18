import pytest

from aureon.api import deps
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.parent_connect import ParentCareerGuide, ParentQuestion
from aureon.domain.models.shared_session import SharedSession, SharedSessionNote
from aureon.main import app
from tests.domain._explore_factories import make_career

STUDENT_ID = "student_1"


class _FakeCareerRepository:
    def __init__(self, careers) -> None:
        self._careers = careers

    async def get_career(self, career_id: str):
        return next((c for c in self._careers if c.id == career_id), None)


class _FakeExpertRepository:
    def __init__(self, experts: list[Mentor]) -> None:
        self._experts = experts

    async def search_experts(self, *, limit=100, offset=0, **_kwargs):
        return self._experts[offset : offset + limit], len(self._experts)

    async def get_expert(self, expert_id: str):
        return next((e for e in self._experts if e.id == expert_id), None)


class _FakeParentConnectRepository:
    def __init__(self, guides: list[ParentCareerGuide], questions: list[ParentQuestion]) -> None:
        self._guides = guides
        self._questions = questions

    async def get_guide(self, career_id: str, *, language: str = "en"):
        match = next((g for g in self._guides if g.career_id == career_id and g.language == language), None)
        if match is None and language != "en":
            match = next((g for g in self._guides if g.career_id == career_id and g.language == "en"), None)
        return match

    async def list_questions(self, *, category=None, career_id=None, language: str = "en"):
        results = [q for q in self._questions if q.language == language]
        if not results and language != "en":
            results = [q for q in self._questions if q.language == "en"]
        if category:
            results = [q for q in results if q.category == category]
        if career_id:
            results = [q for q in results if q.career_id == career_id]
        return results


class _FakeSharedSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, SharedSession] = {}
        self._notes: dict[str, list[SharedSessionNote]] = {}

    async def create_session(self, session: SharedSession) -> SharedSession:
        self._sessions[session.id] = session
        self._notes[session.id] = []
        return session

    async def get_by_token(self, access_token: str):
        return next((s for s in self._sessions.values() if s.access_token == access_token), None)

    async def get_by_id(self, session_id: str):
        return self._sessions.get(session_id)

    async def list_for_student(self, student_id: str):
        return [s for s in self._sessions.values() if s.student_id == student_id]

    async def update_session(self, session: SharedSession) -> SharedSession:
        self._sessions[session.id] = session
        return session

    async def add_note(self, note: SharedSessionNote) -> SharedSessionNote:
        self._notes.setdefault(note.session_id, []).append(note)
        return note

    async def list_notes(self, session_id: str):
        return self._notes.get(session_id, [])


def _expert(**overrides) -> Mentor:
    defaults: dict = dict(
        id="expert_1", name="Test Expert", role_type="industry_professional", field="technology",
        bio="x", learning_style_fit="x", career_ids=["c1"], advice_for_parents="Real, honest advice.",
    )
    defaults.update(overrides)
    return Mentor(**defaults)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    careers = [make_career(id="c1", name="Software Engineer")]
    experts = [_expert()]
    guides = [
        ParentCareerGuide(id="guide_1", career_id="c1", earning_reality="Real earning narrative.", career_stability="x", work_life_balance="x", growth_opportunities="x", global_demand="x"),
        ParentCareerGuide(id="guide_1_hi", career_id="c1", earning_reality="असली कमाई का विवरण।", career_stability="x", work_life_balance="x", growth_opportunities="x", global_demand="x", language="hi"),
    ]
    questions = [
        ParentQuestion(id="q1", category="salary", career_id=None, question="Is this stable?", expert_response="Yes."),
        ParentQuestion(id="q1_hi", category="salary", career_id=None, question="क्या यह स्थिर है?", expert_response="हाँ।", language="hi"),
    ]
    sessions_repo = _FakeSharedSessionRepository()

    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository(careers)
    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(experts)
    app.dependency_overrides[deps.get_parent_connect_repository] = lambda: _FakeParentConnectRepository(guides, questions)
    app.dependency_overrides[deps.get_shared_session_repository] = lambda: sessions_repo
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_career_repository, None)
        app.dependency_overrides.pop(deps.get_expert_repository, None)
        app.dependency_overrides.pop(deps.get_parent_connect_repository, None)
        app.dependency_overrides.pop(deps.get_shared_session_repository, None)
        app.dependency_overrides.pop(deps.get_current_user_id, None)


def test_get_parent_career_view_is_open_no_auth_required(api_client):
    response = api_client.get("/v1/careers/c1/parent-view")
    assert response.status_code == 200
    body = response.json()
    assert body["career_name"] == "Software Engineer"
    assert body["earning_reality"] == "Real earning narrative."
    assert body["expert_advice"][0]["expert_id"] == "expert_1"


def test_get_parent_career_view_404_for_unknown_career(api_client):
    response = api_client.get("/v1/careers/does_not_exist/parent-view")
    assert response.status_code == 404


def test_list_parent_questions_is_open_and_filterable(api_client):
    response = api_client.get("/v1/parent-questions", params={"category": "salary"})
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 1


def test_parent_career_view_defaults_to_english(api_client):
    response = api_client.get("/v1/careers/c1/parent-view")
    assert response.json()["earning_reality"] == "Real earning narrative."


def test_parent_career_view_returns_real_translated_content_for_hindi(api_client):
    response = api_client.get("/v1/careers/c1/parent-view", params={"language": "hi"})
    assert response.json()["earning_reality"] == "असली कमाई का विवरण।"


def test_parent_career_view_falls_back_to_english_when_a_language_has_no_row(api_client):
    response = api_client.get("/v1/careers/c1/parent-view", params={"language": "te"})
    assert response.json()["earning_reality"] == "Real earning narrative."


def test_list_parent_questions_returns_real_translated_content_for_hindi(api_client):
    response = api_client.get("/v1/parent-questions", params={"language": "hi"})
    questions = response.json()["questions"]
    assert len(questions) == 1
    assert questions[0]["question"] == "क्या यह स्थिर है?"


def test_create_shared_session_requires_the_authenticated_student(api_client):
    response = api_client.post(
        f"/v1/students/{STUDENT_ID}/shared-sessions",
        json={"mentor_id": "expert_1", "career_id": "c1", "topic": "Exploring software engineering"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["student_id"] == STUDENT_ID
    assert body["mentor_id"] == "expert_1"
    assert body["access_token"]


def test_create_shared_session_rejects_a_different_students_path(api_client):
    response = api_client.post(
        "/v1/students/someone-else/shared-sessions",
        json={"mentor_id": "expert_1", "career_id": "c1", "topic": "x"},
    )
    assert response.status_code == 403


def test_shared_session_token_access_never_requires_student_auth(api_client):
    """The second participant (parent/guardian/etc.) has no student login —
    the access_token alone must be enough to reach the session."""
    create_response = api_client.post(
        f"/v1/students/{STUDENT_ID}/shared-sessions",
        json={"mentor_id": "expert_1", "career_id": "c1", "topic": "x"},
    )
    token = create_response.json()["access_token"]

    # Clear student auth entirely — token access must still work.
    app.dependency_overrides.pop(deps.get_current_user_id, None)

    get_response = api_client.get(f"/v1/shared-sessions/{token}")
    assert get_response.status_code == 200
    assert get_response.json()["notes"] == []

    join_response = api_client.post(f"/v1/shared-sessions/{token}/join", json={"participant_label": "Mom"})
    assert join_response.status_code == 200
    assert join_response.json()["participant_label"] == "Mom"

    note_response = api_client.post(
        f"/v1/shared-sessions/{token}/notes", json={"author_role": "participant", "note": "A real note."}
    )
    assert note_response.status_code == 200
    assert note_response.json()["notes"][0]["note"] == "A real note."


def test_list_shared_sessions_for_student(api_client):
    api_client.post(
        f"/v1/students/{STUDENT_ID}/shared-sessions",
        json={"mentor_id": "expert_1", "career_id": "c1", "topic": "x"},
    )
    response = api_client.get(f"/v1/students/{STUDENT_ID}/shared-sessions")
    assert response.status_code == 200
    assert len(response.json()["sessions"]) == 1
