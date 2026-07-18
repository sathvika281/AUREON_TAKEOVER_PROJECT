from datetime import datetime, timezone
from types import SimpleNamespace

from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.career_memory import OpportunityEntry
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.experiment import ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.learning_style import LearningStylePattern
from aureon.domain.models.life_mission import MissionResonance
from aureon.domain.models.interest_signal import RelevantInterest
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentPattern
from aureon.domain.services.decision_workspace_service import (
    ReadinessCheckpoints,
    _aggregate_gaps,
    _build_recommendation,
    build_decision_workspace,
)
from aureon.domain.services.missing_worlds_engine import MissingWorldsAnalysis, WorldExploration

from ._connect_factories import make_expert, make_career_story, make_knowledge_circle, make_mentorship
from ._decision_factories import (
    make_career_candidate,
    make_experiment,
    make_learning_style,
    make_life_mission,
    make_opportunity,
    make_opportunity_recommendation,
)
from ._explore_factories import make_career

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


def _world(**overrides) -> CareerWorld:
    defaults: dict = dict(
        id="world_1", name="Artificial Intelligence", description="x", why_it_matters="x",
        global_importance="x", future_growth="x", related_industries=["technology"],
    )
    defaults.update(overrides)
    return CareerWorld(**defaults)


def _build_full_workspace(profile: StudentProfile, candidates, **overrides):
    career = overrides.pop("career", make_career(id="c1", name="AI Researcher", industry="technology", trait_tags=["curiosity", "analytical_thinking", "leadership"]))
    careers_by_id = {career.id: career}

    missing_worlds_analysis = overrides.pop(
        "missing_worlds_analysis",
        MissingWorldsAnalysis(
            explorations=[
                WorldExploration(world=_world(id="world_unexplored", related_industries=["technology"]), level="unexplored", match_count=0),
                WorldExploration(world=_world(id="world_explored", related_industries=["technology"]), level="explored", match_count=5),
            ],
            recommended_next=[],
        ),
    )
    mission_resonances = overrides.pop(
        "mission_resonances",
        [MissionResonance(mission=make_life_mission(related_tags=["technology", "ai"]), tier="growing", trend="steady", explanation="x", evidence=[])],
    )
    learning_style_patterns = overrides.pop(
        "learning_style_patterns",
        [LearningStylePattern(style=make_learning_style(keywords=["analytical_thinking"]), tier="strong", explanation="x", evidence=[], recommended_experiments=[])],
    )
    relevant_interests = overrides.pop(
        "relevant_interests", [RelevantInterest(topic="AI Researcher", explanation="x", evidence=[])],
    )
    talent_patterns = overrides.pop(
        "talent_patterns", [TalentPattern(talent="analytical_thinking", tier="growing", explanation="x", evidence=[])],
    )
    opportunity_recommendations = overrides.pop(
        "opportunity_recommendations",
        [make_opportunity_recommendation(opportunity=make_opportunity(domain_tags=["technology"], category="internship"))],
    )
    experts = overrides.pop(
        "experts", [make_expert(id="expert_1", career_ids=["c1"], years_experience=10), make_expert(id="expert_2", career_ids=["c1"], years_experience=5)],
    )
    journey_stories_by_career = overrides.pop(
        "journey_stories_by_career", {"c1": [make_career_story(id="story_1", career_id="c1")]},
    )
    knowledge_circles = overrides.pop(
        "knowledge_circles", [make_knowledge_circle(id="circle_1", related_career_industries=["technology"])],
    )
    experiment_catalog = overrides.pop(
        "experiment_catalog", [make_experiment(id="experiment_1", target_traits=["analytical_thinking"])],
    )
    mentorships = overrides.pop("mentorships", [])
    institution_names = overrides.pop("institution_names", ["MIT"])

    return build_decision_workspace(
        profile, candidates, careers_by_id,
        missing_worlds_analysis=missing_worlds_analysis, mission_resonances=mission_resonances,
        learning_style_patterns=learning_style_patterns, relevant_interests=relevant_interests,
        talent_patterns=talent_patterns, opportunity_recommendations=opportunity_recommendations,
        experts=experts, journey_stories_by_career=journey_stories_by_career,
        knowledge_circles=knowledge_circles, experiment_catalog=experiment_catalog, mentorships=mentorships,
        institution_names=institution_names, now=NOW,
    )


def _profile_with_full_evidence() -> StudentProfile:
    profile = StudentProfile(student_id="student_1")
    profile.reflection_journal.append(
        ReflectionEntry(prompt="x", response="I really enjoy AI Researcher work.", answered_at=NOW)
    )
    profile.career_experiments.append(
        ExperimentCompletion(
            id="completion_1", experiment_id="experiment_1", experiment_title="Test Experiment",
            related_world="world_1", target_traits=["analytical_thinking"], completed_at=NOW,
            evidence=ExperimentEvidence(),
        )
    )
    profile.saved_experts.append("expert_1")
    profile.career_exploration_history.append(
        CareerExplorationEvent(id="event_1", career_id="c1", interaction_type="story_viewed", metadata={}, created_at=NOW)
    )
    profile.foundation_memory.opportunities.entries.append(
        OpportunityEntry(
            interaction="viewed", category="internship", ref_id="opportunity_1", title="Test Opportunity", occurred_at=NOW,
        )
    )
    return profile


def test_confidence_band_and_label_map_correctly():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1", confidence=0.8)
    workspace = _build_full_workspace(profile, [candidate])
    card = workspace.cards[0]
    assert card.confidence_label == "Strong"
    assert card.confidence_band == "High Confidence"


def test_hidden_strengths_only_includes_trait_tag_overlap():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    non_matching_talent = TalentPattern(talent="empathy", tier="growing", explanation="x", evidence=[])
    workspace = _build_full_workspace(profile, [candidate], talent_patterns=[non_matching_talent])
    assert workspace.cards[0].hidden_strengths == []


def test_unexplored_worlds_excludes_already_explored():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    workspace = _build_full_workspace(profile, [candidate])
    card = workspace.cards[0]
    assert len(card.unexplored_worlds) == 1
    assert card.unexplored_worlds[0].id == "world_unexplored"


def test_top_experts_sorted_by_years_experience_and_capped():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    experts = [
        make_expert(id=f"expert_{i}", career_ids=["c1"], years_experience=i) for i in range(1, 6)
    ]
    workspace = _build_full_workspace(profile, [candidate], experts=experts)
    top = workspace.cards[0].top_experts
    assert len(top) == 3
    assert [e.years_experience for e in top] == [5, 4, 3]


def test_top_opportunities_capped_at_three_and_filtered_by_domain_tags():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    matching = [
        make_opportunity_recommendation(opportunity=make_opportunity(id=f"opp_{i}", domain_tags=["technology"]))
        for i in range(4)
    ]
    non_matching = make_opportunity_recommendation(opportunity=make_opportunity(id="opp_unrelated", domain_tags=["arts"], category="workshop"))
    workspace = _build_full_workspace(profile, [candidate], opportunity_recommendations=[*matching, non_matching])
    assert len(workspace.cards[0].top_opportunities) == 3


def test_learning_style_pattern_matched_by_keyword_overlap():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    non_matching = [LearningStylePattern(style=make_learning_style(keywords=["unrelated"]), tier="strong", explanation="x", evidence=[], recommended_experiments=[])]
    workspace = _build_full_workspace(profile, [candidate], learning_style_patterns=non_matching)
    assert workspace.cards[0].learning_style_pattern is None


def test_reality_check_reuses_comparison_facts():
    from aureon.agents.specialized.decision.comparison_facts import extract_comparison_facts

    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    career = make_career(id="c1", name="AI Researcher", industry="technology", trait_tags=["curiosity"])
    workspace = _build_full_workspace(profile, [candidate], career=career)
    card = workspace.cards[0]
    facts = extract_comparison_facts(career)
    assert card.reality_check.daily_work == facts["work_style"]
    assert card.reality_check.work_life_balance == facts["work_life_balance"]
    assert card.reality_check.industry_outlook == facts["future_demand"]
    assert card.reality_check.automation_risk == career.future_lens.automation_risk


def test_readiness_and_gaps_are_all_true_and_empty_with_full_evidence():
    profile = _profile_with_full_evidence()
    candidate = make_career_candidate(career_id="c1")
    workspace = _build_full_workspace(profile, [candidate])
    card = workspace.cards[0]
    assert card.readiness.has_reflection is True
    assert card.readiness.has_experiment is True
    assert card.readiness.has_expert_contact is True
    assert card.readiness.has_explored_world is True
    assert card.readiness.has_explored_opportunity is True
    assert card.readiness.percent > 0
    assert card.decision_gaps == []


def test_readiness_and_gaps_are_all_false_and_present_with_empty_profile():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="c1")
    all_unexplored = MissingWorldsAnalysis(
        explorations=[WorldExploration(world=_world(id="world_unexplored", related_industries=["technology"]), level="unexplored", match_count=0)],
        recommended_next=[],
    )
    workspace = _build_full_workspace(profile, [candidate], missing_worlds_analysis=all_unexplored)
    card = workspace.cards[0]
    assert card.readiness.has_reflection is False
    assert card.readiness.has_experiment is False
    assert card.readiness.has_expert_contact is False
    assert card.readiness.has_explored_world is False
    assert card.readiness.percent < 100
    assert len(card.decision_gaps) == 5


def test_reasons_for_and_against_mirror_evidence_graph():
    profile = StudentProfile(student_id="student_1")
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="Loves solving open problems.", source="conversation", related_career="c1", relation="supports")
    )
    profile.evidence_graph.append(
        EvidenceRecord(id="e2", text="Dislikes long research timelines.", source="reflection", related_career="c1", relation="contradicts")
    )
    candidate = make_career_candidate(career_id="c1", uncertainty_reason="Still exploring alternatives.")
    workspace = _build_full_workspace(profile, [candidate])
    card = workspace.cards[0]
    assert card.reasons_for == ["Loves solving open problems."]
    assert "Dislikes long research timelines." in card.reasons_against
    assert "Still exploring alternatives." in card.reasons_against
    assert card.explanation.supporting_by_source == {"Conversations": ["Loves solving open problems."]}
    assert card.explanation.contradicting_by_source == {"Reflection Journal": ["Dislikes long research timelines."]}


def test_recommendation_thresholds():
    high = ReadinessCheckpoints(True, True, True, True, True, True, True)
    assert _build_recommendation("Strong", high.percent, []).verdict == "ready_to_shortlist"

    low = ReadinessCheckpoints(False, False, False, False, False, False, False)
    assert _build_recommendation("Needs More Evidence", low.percent, ["gap"]).verdict == "continue_exploring"

    mid = ReadinessCheckpoints(True, True, True, False, False, False, False)
    assert _build_recommendation("Growing", mid.percent, []).verdict == "hold_for_now"


def test_aggregate_gaps_orders_by_frequency():
    cards = [
        SimpleNamespace(decision_gaps=["A", "B"]),
        SimpleNamespace(decision_gaps=["A"]),
        SimpleNamespace(decision_gaps=["A", "B", "C"]),
    ]
    result = _aggregate_gaps(cards)
    assert result[0] == "A"
    assert result[1] == "B"


def test_workspace_skips_unknown_career_ids_gracefully():
    profile = StudentProfile(student_id="student_1")
    candidate = make_career_candidate(career_id="does_not_exist")
    workspace = _build_full_workspace(profile, [candidate])
    assert workspace.cards == []
    assert workspace.overall_readiness_percent == 0
