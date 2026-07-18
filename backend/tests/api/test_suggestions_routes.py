import pytest

from aureon.api import deps
from aureon.core.config import get_settings
from aureon.domain.models.suggestion import Suggestion
from aureon.domain.services.suggestion_service import submit_suggestion
from aureon.main import app

STUDENT_ID = "student_1"
OTHER_STUDENT_ID = "student_2"
REVIEWER_SECRET = "test-reviewer-secret"


class _FakeSuggestionRepository:
    def __init__(self) -> None:
        self._suggestions: dict[str, Suggestion] = {}

    async def create(self, suggestion: Suggestion) -> Suggestion:
        self._suggestions[suggestion.id] = suggestion
        return suggestion

    async def get_by_id(self, suggestion_id: str):
        return self._suggestions.get(suggestion_id)

    async def list_for_student(self, student_id: str):
        return [s for s in self._suggestions.values() if s.student_id == student_id]

    async def list_all(self, *, status=None, category=None, search=None, limit=50, offset=0):
        results = list(self._suggestions.values())
        if status:
            results = [s for s in results if s.status == status]
        if category:
            results = [s for s in results if s.category == category]
        if search:
            needle = search.lower()
            results = [s for s in results if needle in s.title.lower() or needle in s.description.lower()]
        return results[offset : offset + limit]

    async def update(self, suggestion: Suggestion) -> Suggestion:
        self._suggestions[suggestion.id] = suggestion
        return suggestion


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    repo = _FakeSuggestionRepository()

    def _settings_with_reviewer_secret():
        settings = get_settings()
        return settings.model_copy(update={"suggestion_reviewer_secret": REVIEWER_SECRET})

    app.dependency_overrides[deps.get_suggestion_repository] = lambda: repo
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[get_settings] = _settings_with_reviewer_secret
    try:
        yield TestClient(app), repo
    finally:
        app.dependency_overrides.pop(deps.get_suggestion_repository, None)
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(get_settings, None)


def _create_payload(**overrides) -> dict:
    payload = dict(
        category="career",
        title="Wildlife Photographer",
        description="I couldn't find this career in the catalog.",
    )
    payload.update(overrides)
    return payload


def test_student_creates_a_suggestion(api_client):
    client, _ = api_client
    response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["student_id"] == STUDENT_ID
    assert body["status"] == "pending"
    assert body["category"] == "career"
    assert body["id"]


def test_create_suggestion_carries_context_fields(api_client):
    client, _ = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/suggestions",
        json=_create_payload(
            category="correction",
            context_type="opportunity",
            context_id="opportunity_1",
            context_metadata={"page_or_feature": "Opportunity Equality"},
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["context_type"] == "opportunity"
    assert body["context_id"] == "opportunity_1"
    assert body["context_metadata"] == {"page_or_feature": "Opportunity Equality"}


def test_create_suggestion_rejects_a_different_students_path(api_client):
    client, _ = api_client
    response = client.post(f"/v1/students/{OTHER_STUDENT_ID}/suggestions", json=_create_payload())
    assert response.status_code == 403


def test_create_suggestion_rejects_an_invalid_category(api_client):
    client, _ = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload(category="not_a_real_category")
    )
    assert response.status_code == 422


def test_create_suggestion_requires_authentication(api_client):
    client, _ = api_client
    app.dependency_overrides.pop(deps.get_current_user_id, None)
    response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    assert response.status_code == 401


def test_student_lists_only_their_own_suggestions(api_client):
    client, repo = api_client
    other = submit_suggestion(
        student_id=OTHER_STUDENT_ID, category="general_feedback", title="x", description="x"
    )
    repo._suggestions[other.id] = other

    client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    response = client.get(f"/v1/students/{STUDENT_ID}/suggestions")
    assert response.status_code == 200
    results = response.json()["suggestions"]
    assert len(results) == 1
    assert results[0]["student_id"] == STUDENT_ID


def test_student_cannot_access_another_students_suggestion_detail(api_client):
    client, _ = api_client
    create_response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    suggestion_id = create_response.json()["id"]

    response = client.get(f"/v1/students/{OTHER_STUDENT_ID}/suggestions/{suggestion_id}")
    assert response.status_code == 403


def test_student_gets_404_for_someone_elses_suggestion_id(api_client):
    client, repo = api_client
    other = submit_suggestion(
        student_id=OTHER_STUDENT_ID, category="general_feedback", title="x", description="x"
    )
    repo._suggestions[other.id] = other

    response = client.get(f"/v1/students/{STUDENT_ID}/suggestions/{other.id}")
    assert response.status_code == 404


def test_reviewer_endpoints_reject_missing_secret(api_client):
    client, _ = api_client
    response = client.get("/v1/suggestions")
    assert response.status_code == 403


def test_reviewer_endpoints_reject_wrong_secret(api_client):
    client, _ = api_client
    response = client.get("/v1/suggestions", headers={"X-Aureon-Reviewer-Secret": "wrong"})
    assert response.status_code == 403


def test_a_valid_student_token_alone_does_not_grant_reviewer_access(api_client):
    """A normal student must NOT be able to approve or modify review
    status — only holding the reviewer secret does, never student auth."""
    client, _ = api_client
    create_response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    suggestion_id = create_response.json()["id"]

    response = client.patch(
        f"/v1/suggestions/{suggestion_id}/status", json={"status": "approved"}
    )
    assert response.status_code == 403


def test_reviewer_lists_filters_and_searches_with_correct_secret(api_client):
    client, _ = api_client
    client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload(category="career"))
    client.post(
        f"/v1/students/{STUDENT_ID}/suggestions",
        json=_create_payload(category="resource", title="A Podcast", description="Great show."),
    )
    headers = {"X-Aureon-Reviewer-Secret": REVIEWER_SECRET}

    all_response = client.get("/v1/suggestions", headers=headers)
    assert all_response.status_code == 200
    assert len(all_response.json()["suggestions"]) == 2

    filtered = client.get("/v1/suggestions", params={"category": "resource"}, headers=headers)
    assert len(filtered.json()["suggestions"]) == 1
    assert filtered.json()["suggestions"][0]["title"] == "A Podcast"

    searched = client.get("/v1/suggestions", params={"q": "wildlife"}, headers=headers)
    assert len(searched.json()["suggestions"]) == 1

    paginated = client.get("/v1/suggestions", params={"limit": 1, "offset": 0}, headers=headers)
    assert len(paginated.json()["suggestions"]) == 1


def test_reviewer_updates_status_and_notes_with_correct_secret(api_client):
    client, _ = api_client
    create_response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    suggestion_id = create_response.json()["id"]
    headers = {"X-Aureon-Reviewer-Secret": REVIEWER_SECRET}

    response = client.patch(
        f"/v1/suggestions/{suggestion_id}/status",
        json={"status": "under_review", "review_notes": "Looking into this."},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "under_review"
    assert body["review_notes"] == "Looking into this."
    assert body["reviewed_at"] is not None

    student_view = client.get(f"/v1/students/{STUDENT_ID}/suggestions/{suggestion_id}")
    assert student_view.json()["status"] == "under_review"


def test_reviewer_update_status_rejects_invalid_status(api_client):
    client, _ = api_client
    create_response = client.post(f"/v1/students/{STUDENT_ID}/suggestions", json=_create_payload())
    suggestion_id = create_response.json()["id"]
    headers = {"X-Aureon-Reviewer-Secret": REVIEWER_SECRET}

    response = client.patch(
        f"/v1/suggestions/{suggestion_id}/status", json={"status": "not_a_real_status"}, headers=headers
    )
    assert response.status_code == 422


def test_reviewer_get_detail_404_for_unknown_id(api_client):
    client, _ = api_client
    headers = {"X-Aureon-Reviewer-Secret": REVIEWER_SECRET}
    response = client.get("/v1/suggestions/does-not-exist", headers=headers)
    assert response.status_code == 404
