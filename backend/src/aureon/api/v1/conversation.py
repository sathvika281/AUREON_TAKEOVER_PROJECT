from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import ConversationServiceDep, get_current_user_id
from aureon.domain.services.profile_view import (
    build_career_dna_dto,
    build_hidden_potential_dtos,
    build_hypothesis_dtos,
    build_notebook_entry_dtos,
    build_understanding_level,
)
from aureon.shared.schemas import (
    ConversationTurnRequest,
    ConversationTurnResponse,
    SuggestedActivityDTO,
)
from aureon.shared.types import AgentName

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("/turn", response_model=ConversationTurnResponse)
async def conversation_turn(
    request: ConversationTurnRequest,
    service: ConversationServiceDep,
    user_id: str = Depends(get_current_user_id),
) -> ConversationTurnResponse:
    """Thin route: parses the request DTO, delegates to
    ``ConversationService``, and shapes the response DTO. No business logic
    lives here — see ``domain/services/conversation_service.py`` for
    orchestration, ``domain/services/profile_view.py`` for DTO mapping, and
    ``agents/orchestrator/graph.py`` for routing.

    ``student_id`` arrives in the request body here (not a path param), so
    this is the one route that can't use the router-level
    ``require_own_profile`` dependency every other file uses — the same
    ownership check is applied inline instead.
    """
    if user_id != request.student_id:
        raise HTTPException(status_code=403, detail="You can only access your own profile.")

    result_state = await service.handle_turn(
        student_id=request.student_id,
        conversation_id=request.conversation_id,
        message=request.message,
    )
    messages = result_state.get("messages", [])
    reply = messages[-1].content if messages else ""
    mode = result_state["mode"]

    profile = result_state.get("student_profile")
    if profile is not None:
        career_dna = build_career_dna_dto(profile)
        hypotheses = build_hypothesis_dtos(profile)
        hidden_potential = build_hidden_potential_dtos(profile)
        notebook_entries = build_notebook_entry_dtos(profile)
        understanding_stage, understanding_narrative = build_understanding_level(profile, mode=mode)
    else:
        career_dna, hypotheses, hidden_potential, notebook_entries = {}, [], [], []
        understanding_stage, understanding_narrative = "Seed", "Nothing yet — every conversation plants a seed."

    discovery_output = result_state.get("agent_outputs", {}).get(AgentName.DISCOVERY.value)
    suggested_activity = None
    if discovery_output is not None:
        raw_activity = discovery_output.payload.get("suggested_activity")
        if raw_activity:
            suggested_activity = SuggestedActivityDTO(**raw_activity)

    return ConversationTurnResponse(
        conversation_id=result_state["conversation_id"],
        reply=reply,
        mode=mode,
        active_agent=result_state.get("active_agent"),
        confidence_score=result_state["confidence_score"],
        understanding_stage=understanding_stage,
        understanding_narrative=understanding_narrative,
        career_dna=career_dna,
        hypotheses=hypotheses,
        hidden_potential=hidden_potential,
        notebook_entries=notebook_entries,
        reflection_prompt=result_state.get("pending_reflection_prompt"),
        suggested_activity=suggested_activity,
    )
