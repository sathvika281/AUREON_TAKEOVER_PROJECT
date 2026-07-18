from aureon.agents.orchestrator.checkpointer import get_checkpointer
from aureon.domain.models.career_memory import CareerMemory, EvidenceArtifact, EvidenceMemory
from aureon.domain.models.student_profile import StudentProfile


def test_checkpointer_round_trips_a_profile_with_non_default_foundation_memory():
    profile = StudentProfile(
        student_id="s1",
        foundation_memory=CareerMemory(
            evidence=EvidenceMemory(
                artifacts=[EvidenceArtifact(kind="project", ref_id="proj_1", title="Robotics Arm")]
            )
        ),
    )

    serde = get_checkpointer().serde
    dumped = serde.dumps_typed(profile)
    restored = serde.loads_typed(dumped)

    assert restored.foundation_memory.evidence.artifacts[0].ref_id == "proj_1"
