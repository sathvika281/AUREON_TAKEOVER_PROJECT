from datetime import datetime, timedelta, timezone

from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.experiment import ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.life_mission_engine import RECENT_WINDOW_DAYS, analyze_life_missions

NOW = datetime.now(timezone.utc)


def _mission(**overrides) -> LifeMission:
    defaults = dict(
        id="mission_climate", name="Solve Climate Problems", description="d",
        related_tags=["climate", "sustainability"],
    )
    defaults.update(overrides)
    return LifeMission(**defaults)


def test_mission_with_zero_evidence_is_excluded():
    profile = StudentProfile(student_id="s1")
    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances == []


def test_single_evidence_item_yields_still_emerging():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["curiosity"] = TraitSignal(score=0.6, summary="Interested in climate systems.")

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert len(resonances) == 1
    assert resonances[0].tier == "still_emerging"


def test_three_items_across_two_sources_yield_strong():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["curiosity"] = TraitSignal(score=0.6, summary="Climate-focused curiosity.")
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="Talked about climate policy", source="conversation", relation="supports", created_at=NOW)
    )
    profile.reflection_journal.append(
        ReflectionEntry(prompt="p", response="I care about climate change deeply", created_at=NOW, answered_at=NOW)
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances[0].tier == "strong"
    sources = {e.source for e in resonances[0].evidence}
    assert len(sources) >= 2


def test_experiment_completion_counts_as_evidence():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="Analyze a climate problem",
            related_world="Climate", target_traits=["climate"], completed_at=NOW,
            evidence=ExperimentEvidence(curiosity=True),
        )
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert len(resonances) == 1
    assert resonances[0].evidence[0].source == "experiment"


def test_generic_completion_fallback_text_does_not_leak_into_evidence_graph_matching():
    """experiment_result.py writes "Completed '<title>'" into the
    Evidence Graph for every completion, genuine signal or not (real,
    honest evidence for other consumers like Hidden Potential). If a
    mission-relevant word only appears in the experiment's *title*, this
    exact auto-generated string must not itself become a second,
    independent path for a no-signal completion to count as mission
    evidence — closing the same gap _evidence_from_experiments closes,
    on the Evidence Graph side."""
    profile = StudentProfile(student_id="s1")
    profile.evidence_graph.append(
        EvidenceRecord(
            id="e1", text="Completed 'Analyze a climate problem'", source="experiment",
            relation="supports", created_at=NOW,
        )
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances == []


def test_experiment_completion_without_genuine_signal_is_not_evidence():
    """Completion alone must not inflate mission resonance — the PRD's
    explicit requirement. A tag-matching experiment with every flag False
    and a blank reflection reports nothing genuine, so it must not count."""
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="Analyze a climate problem",
            related_world="Climate", target_traits=["climate"], completed_at=NOW,
            evidence=ExperimentEvidence(),
        )
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances == []


def test_experiment_completion_with_only_reflection_still_counts_as_evidence():
    """A genuine written reflection is real engagement even with every
    boolean flag left False — the fix must not require the flags
    specifically, just some real signal."""
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="Analyze a climate problem",
            related_world="Climate", target_traits=["climate"], completed_at=NOW,
            evidence=ExperimentEvidence(reflection="This made me think about my own energy use."),
        )
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert len(resonances) == 1
    assert resonances[0].evidence[0].source == "experiment"


def test_trend_is_emerging_when_recent_outweighs_previous():
    profile = StudentProfile(student_id="s1")
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="climate", source="conversation", relation="supports", created_at=NOW - timedelta(days=5))
    )
    profile.evidence_graph.append(
        EvidenceRecord(id="e2", text="climate", source="conversation", relation="supports", created_at=NOW - timedelta(days=10))
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances[0].trend == "emerging"


def test_trend_is_fading_when_previous_outweighs_recent():
    profile = StudentProfile(student_id="s1")
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="climate", source="conversation", relation="supports", created_at=NOW - timedelta(days=5))
    )
    for i in range(3):
        profile.evidence_graph.append(
            EvidenceRecord(
                id=f"old{i}", text="climate", source="conversation", relation="supports",
                created_at=NOW - timedelta(days=RECENT_WINDOW_DAYS + 10 + i),
            )
        )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances[0].trend == "fading"


def test_trend_is_steady_when_recent_equals_previous():
    profile = StudentProfile(student_id="s1")
    profile.evidence_graph.append(
        EvidenceRecord(id="e1", text="climate", source="conversation", relation="supports", created_at=NOW - timedelta(days=5))
    )
    profile.evidence_graph.append(
        EvidenceRecord(
            id="e2", text="climate", source="conversation", relation="supports",
            created_at=NOW - timedelta(days=RECENT_WINDOW_DAYS + 10),
        )
    )

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances[0].trend == "steady"


def test_every_resonance_explanation_cites_something_real():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["curiosity"] = TraitSignal(score=0.6, summary="Climate-focused curiosity.")

    resonances = analyze_life_missions(profile, [_mission()], now=NOW)

    assert resonances[0].explanation
    assert "%" not in resonances[0].explanation
