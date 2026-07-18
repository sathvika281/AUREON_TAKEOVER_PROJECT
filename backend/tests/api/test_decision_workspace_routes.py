import pytest

from aureon.api import deps
from aureon.api.v1 import decision as decision_route
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.domain._connect_factories import make_expert
from tests.domain._decision_factories import make_career_candidate
from tests.domain._explore_factories import make_career
from tests.fakes import FakeLLMClient, FakeStudentProfileRepository, tool_call_response

STUDENT_ID = "student_1"


class _FakeCareerRepository:
    def __init__(self, careers) -> None:
        self._careers = careers

    async def list_careers(self, **_kwargs):
        return self._careers

    async def get_career(self, career_id: str):
        return next((c for c in self._careers if c.id == career_id), None)


class _FakeInstitutionRepository:
    async def list_institutions(self, **_kwargs):
        return []


class _FakeCareerWorldRepository:
    async def list_worlds(self):
        return []

    async def get_world(self, world_id: str):
        return None


class _FakeLifeMissionRepository:
    async def list_missions(self):
        return []

    async def get_mission(self, mission_id: str):
        return None


class _FakeLearningStyleRepository:
    async def list_styles(self):
        return []


class _FakeExperimentRepository:
    async def list_experiments(self):
        return []


class _FakeExpertRepository:
    def __init__(self, experts) -> None:
        self._experts = experts

    async def search_experts(self, *, limit=100, offset=0, **_kwargs):
        return self._experts[offset : offset + limit], len(self._experts)

    async def get_expert(self, expert_id: str):
        return next((e for e in self._experts if e.id == expert_id), None)


class _FakeJourneyStoryRepository:
    async def search_stories(self, *, career_id=None, limit=100, **_kwargs):
        return [], 0


class _FakeKnowledgeCircleRepository:
    async def list_circles(self, **_kwargs):
        return []


class _FakeMentorshipRepository:
    async def list_for_student(self, student_id: str):
        return []


async def _fake_fetch_all_safely():
    return []


@pytest.fixture
def api_client(monkeypatch):
    from fastapi.testclient import TestClient

    careers = [make_career(id="c1", name="AI Researcher", industry="technology", trait_tags=["curiosity"])]
    experts = [make_expert(id="expert_1", career_ids=["c1"])]
    profile = StudentProfile(student_id=STUDENT_ID)
    profile.career_candidates.append(make_career_candidate(career_id="c1", career_name="AI Researcher"))
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: profile})

    monkeypatch.setattr(decision_route, "fetch_all_safely", _fake_fetch_all_safely)

    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository(careers)
    app.dependency_overrides[deps.get_institution_repository] = lambda: _FakeInstitutionRepository()
    app.dependency_overrides[deps.get_career_world_repository] = lambda: _FakeCareerWorldRepository()
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: _FakeLifeMissionRepository()
    app.dependency_overrides[deps.get_learning_style_repository] = lambda: _FakeLearningStyleRepository()
    app.dependency_overrides[deps.get_experiment_repository] = lambda: _FakeExperimentRepository()
    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(experts)
    app.dependency_overrides[deps.get_journey_story_repository] = lambda: _FakeJourneyStoryRepository()
    app.dependency_overrides[deps.get_knowledge_circle_repository] = lambda: _FakeKnowledgeCircleRepository()
    app.dependency_overrides[deps.get_mentorship_repository] = lambda: _FakeMentorshipRepository()
    try:
        yield TestClient(app), fake_profiles
    finally:
        for dep in (
            deps.get_current_user_id, deps.get_student_profile_repository, deps.get_career_repository,
            deps.get_institution_repository, deps.get_career_world_repository, deps.get_life_mission_repository,
            deps.get_learning_style_repository, deps.get_experiment_repository,
            deps.get_expert_repository, deps.get_journey_story_repository, deps.get_knowledge_circle_repository,
            deps.get_mentorship_repository,
        ):
            app.dependency_overrides.pop(dep, None)


def test_get_decision_workspace_returns_a_card_per_active_candidate(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/decision-workspace")
    assert response.status_code == 200
    body = response.json()
    assert len(body["cards"]) == 1
    card = body["cards"][0]
    assert card["career_id"] == "c1"
    assert card["career_name"] == "AI Researcher"
    assert card["confidence_band"] in {"High Confidence", "Medium Confidence", "Early Exploration"}
    assert "readiness" in card
    assert "reality_check" in card
    assert "recommendation" in card
    assert "overall_readiness_percent" in body
    assert "stage_progress" in body


def test_get_decision_workspace_filters_by_career_ids_query_param(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/decision-workspace", params={"career_ids": "does_not_exist"})
    assert response.status_code == 200
    assert response.json()["cards"] == []


def test_get_decision_workspace_requires_the_authenticated_student(api_client):
    client, _ = api_client
    response = client.get("/v1/students/someone-else/decision-workspace")
    assert response.status_code == 403


def test_career_comparisons_include_the_six_extra_dimensions(api_client, monkeypatch):
    client, _ = api_client
    second_career = make_career(id="c2", name="Data Scientist", industry="technology", trait_tags=["analytical_thinking"])
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository(
        [make_career(id="c1", name="AI Researcher", industry="technology", trait_tags=["curiosity"]), second_career]
    )

    profile = StudentProfile(student_id=STUDENT_ID)
    profile.career_candidates.append(make_career_candidate(career_id="c1", career_name="AI Researcher"))
    profile.career_candidates.append(make_career_candidate(id="candidate_2", career_id="c2", career_name="Data Scientist"))
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: FakeStudentProfileRepository({STUDENT_ID: profile})

    fake_llm = FakeLLMClient([
        tool_call_response(
            "record_career_comparison",
            {
                "reply_to_student": "Here's how these compare.",
                "dimension_reasoning": [],
                "summary_reason": "Both lean on your analytical strengths, in different settings.",
                "missing_evidence": [],
            },
        )
    ])
    monkeypatch.setattr(decision_route, "get_llm_client", lambda: fake_llm)

    response = client.post(
        f"/v1/students/{STUDENT_ID}/career-comparisons", json={"career_ids": ["c1", "c2"]},
    )
    assert response.status_code == 200
    comparisons = response.json()["comparisons"]
    assert len(comparisons) == 1
    dimension_keys = {d["dimension"] for d in comparisons[0]["dimensions"]}
    for extra in (
        "leadership_emphasis", "opportunity_availability", "interest_alignment",
        "career_dna_alignment", "learning_style_alignment", "mission_alignment",
    ):
        assert extra in dimension_keys
