import pytest

from aureon.api import deps
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.mentorship import Mentorship
from aureon.main import app

STUDENT_ID = "student_1"


class _FakeExpertRepository:
    def __init__(self, experts: list[Mentor]) -> None:
        self._experts = experts

    async def get_expert(self, expert_id: str):
        return next((e for e in self._experts if e.id == expert_id), None)


class _FakeMentorshipRepository:
    def __init__(self) -> None:
        self._mentorships: dict[str, Mentorship] = {}

    async def create(self, mentorship: Mentorship) -> Mentorship:
        self._mentorships[mentorship.id] = mentorship
        return mentorship

    async def get_by_id(self, mentorship_id: str):
        return self._mentorships.get(mentorship_id)

    async def get_by_token(self, review_token: str):
        return next((m for m in self._mentorships.values() if m.review_token == review_token), None)

    async def list_for_student(self, student_id: str):
        return [m for m in self._mentorships.values() if m.student_id == student_id]

    async def list_for_expert(self, expert_id: str):
        return [m for m in self._mentorships.values() if m.expert_id == expert_id]

    async def update(self, mentorship: Mentorship) -> Mentorship:
        self._mentorships[mentorship.id] = mentorship
        return mentorship


def _expert(**overrides) -> Mentor:
    defaults: dict = dict(
        id="expert_1", name="Test Expert", role_type="industry_professional", field="technology",
        bio="x", learning_style_fit="x", accepts_mentorship=True,
    )
    defaults.update(overrides)
    return Mentor(**defaults)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    experts = [_expert()]
    mentorships_repo = _FakeMentorshipRepository()

    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(experts)
    app.dependency_overrides[deps.get_mentorship_repository] = lambda: mentorships_repo
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_expert_repository, None)
        app.dependency_overrides.pop(deps.get_mentorship_repository, None)
        app.dependency_overrides.pop(deps.get_current_user_id, None)


def test_create_mentorship_request_requires_the_authenticated_student(api_client):
    response = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "Learn about research careers."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["student_id"] == STUDENT_ID
    assert body["expert_id"] == "expert_1"
    assert body["status"] == "requested"
    assert body["review_token"]


def test_create_mentorship_request_rejects_a_different_students_path(api_client):
    response = api_client.post(
        "/v1/students/someone-else/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    assert response.status_code == 403


def test_create_mentorship_request_404_for_unknown_expert(api_client):
    response = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "does_not_exist", "goals": "x"},
    )
    assert response.status_code == 404


def test_mentorship_review_token_access_never_requires_student_auth(api_client):
    """The expert has no login anywhere in this system — the
    review_token alone must be enough to review, accept, and add notes."""
    create_response = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "Learn about research careers."},
    )
    token = create_response.json()["review_token"]

    # Clear student auth entirely — token access must still work.
    app.dependency_overrides.pop(deps.get_current_user_id, None)

    get_response = api_client.get(f"/v1/mentorship-review/{token}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "requested"

    accept_response = api_client.post(f"/v1/mentorship-review/{token}/accept")
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "accepted"

    note_response = api_client.post(
        f"/v1/mentorship-review/{token}/notes", json={"author_role": "expert", "note": "Welcome aboard."}
    )
    assert note_response.status_code == 200
    assert note_response.json()["progress_notes"][0]["note"] == "Welcome aboard."

    complete_response = api_client.post(f"/v1/mentorship-review/{token}/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"


def test_mentorship_review_decline_flow(api_client):
    create_response = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    token = create_response.json()["review_token"]
    app.dependency_overrides.pop(deps.get_current_user_id, None)

    decline_response = api_client.post(f"/v1/mentorship-review/{token}/decline")
    assert decline_response.status_code == 200
    assert decline_response.json()["status"] == "declined"


def test_list_my_mentorships_for_student(api_client):
    api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    response = api_client.get(f"/v1/students/{STUDENT_ID}/mentorships")
    assert response.status_code == 200
    assert len(response.json()["mentorships"]) == 1


def test_create_mentorship_request_blocks_a_duplicate_active_request(api_client):
    first = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    assert first.status_code == 200

    second = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "y"},
    )
    assert second.status_code == 400


def test_create_mentorship_request_allowed_again_after_a_decline(api_client):
    first = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    token = first.json()["review_token"]
    app.dependency_overrides.pop(deps.get_current_user_id, None)
    api_client.post(f"/v1/mentorship-review/{token}/decline")
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID

    second = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "y"},
    )
    assert second.status_code == 200
    assert second.json()["status"] == "requested"


def test_create_mentorship_request_rejects_an_expert_not_accepting_mentorship(api_client):
    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(
        [_expert(id="expert_closed", accepts_mentorship=False)]
    )
    response = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_closed", "goals": "x"},
    )
    assert response.status_code == 400


def test_create_mentorship_request_rejects_when_expert_is_at_capacity(api_client):
    full_expert = _expert(id="expert_full", accepts_mentorship=True, max_students=1)
    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository([full_expert])

    first = api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_full", "goals": "x"},
    )
    token = first.json()["review_token"]
    app.dependency_overrides.pop(deps.get_current_user_id, None)
    api_client.post(f"/v1/mentorship-review/{token}/accept")
    app.dependency_overrides[deps.get_current_user_id] = lambda: "student_2"

    second = api_client.post(
        "/v1/students/student_2/mentorships",
        json={"expert_id": "expert_full", "goals": "y"},
    )
    assert second.status_code == 400


def test_list_my_mentorships_includes_real_expert_identity(api_client):
    api_client.post(
        f"/v1/students/{STUDENT_ID}/mentorships",
        json={"expert_id": "expert_1", "goals": "x"},
    )
    response = api_client.get(f"/v1/students/{STUDENT_ID}/mentorships")
    mentorship = response.json()["mentorships"][0]
    assert mentorship["expert_name"] == "Test Expert"
    assert mentorship["expert_domain"] == "technology"


def test_expert_detail_surfaces_accepts_mentorship_and_current_mentee_count(api_client):
    """Cross-check with expert_connect.py — accepts_mentorship/max_students
    were forward-looking-only until this batch; now they're read."""

    class _FakeCareerRepository:
        async def list_careers(self, **_kwargs):
            return []

    class _FakeCareerEventRepository:
        async def list_career_events(self, **_kwargs):
            return []

    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository()
    app.dependency_overrides[deps.get_career_event_repository] = lambda: _FakeCareerEventRepository()

    response = api_client.get("/v1/experts/expert_1")
    assert response.status_code == 200
    body = response.json()
    assert body["accepts_mentorship"] is True
    assert body["current_mentee_count"] == 0

    app.dependency_overrides.pop(deps.get_career_repository, None)
    app.dependency_overrides.pop(deps.get_career_event_repository, None)
