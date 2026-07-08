from fastapi import APIRouter, Depends

from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.registry import AgentRegistry
from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    ProgressDimensionDTO,
    ProgressPriorityDTO,
    ProgressReportResponse,
    ProgressTimelineWindowDTO,
)
from aureon.shared.types import AgentName

router = APIRouter(prefix="/students", tags=["growth"], dependencies=[Depends(require_own_profile)])


@router.post("/{student_id}/progress-report/analyze", response_model=ProgressReportResponse)
async def analyze_progress_route(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ProgressReportResponse:
    """Progress Intelligence — evidence-driven growth analysis, never a
    completion percentage. Not persisted: recomputed fresh from
    StudentProfile's existing data every time it's requested, same
    pure-read philosophy as decision-timeline plus one LLM reasoning
    call. Manual trigger (POST, not an auto-fetching GET) to match every
    other analyze-on-demand feature in the product."""
    profile = await profiles.get_or_create(student_id)
    llm = get_llm_client()

    # Growth is both the primary and only specialist involved here — no
    # delegation needed, since Progress Intelligence is entirely its own
    # capability (Memory Recall + Planning). The Mission Orchestrator
    # still tracks the lifecycle (created -> executing -> completed) and
    # the agent's real execution stages, same as every other mission.
    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="progress_intelligence_analysis", primary_agent=AgentName.GROWTH.value,
    )
    MissionOrchestrator.begin_execution(mission)
    growth_agent = AgentRegistry.get(AgentName.GROWTH.value)
    report = await growth_agent.build_report(profile, llm=llm, mission=mission)
    MissionOrchestrator.complete(mission)

    return ProgressReportResponse(
        overall_narrative=report.overall_narrative,
        dimensions=[
            ProgressDimensionDTO(
                key=d.key, label=d.label, direction=d.direction,
                evidence_summary=d.evidence_summary, reasoning=d.reasoning,
            )
            for d in report.dimensions
        ],
        growing_strengths=report.growing_strengths,
        areas_slowing_down=report.areas_slowing_down,
        recent_improvements=report.recent_improvements,
        timeline=[
            ProgressTimelineWindowDTO(label=w.label, description=w.description, event_count=w.event_count)
            for w in report.timeline
        ],
        next_priorities=[
            ProgressPriorityDTO(rank=p.rank, action=p.action, evidence=p.evidence)
            for p in report.next_priorities
        ],
        insufficient_evidence=report.insufficient_evidence,
        insufficient_evidence_reason=report.insufficient_evidence_reason,
        generated_at=report.generated_at,
        mission=mission_snapshot_to_dto(build_mission_snapshot(mission)),
        artifacts_updated=[] if report.insufficient_evidence else ["Progress Report Updated"],
    )
