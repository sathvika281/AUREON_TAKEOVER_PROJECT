from pydantic import ValidationError

from fastapi import APIRouter, Depends, HTTPException, Query

from aureon.api.deps import get_suggestion_repository, require_own_profile, require_reviewer_secret
from aureon.domain.services.suggestion_service import submit_suggestion, update_status
from aureon.services.supabase.repositories.suggestion_repository import SuggestionRepository
from aureon.shared.schemas import (
    CreateSuggestionRequest,
    SuggestionDTO,
    SuggestionsResponse,
    UpdateSuggestionStatusRequest,
)

# Student-scoped — submitting/listing your own suggestions genuinely
# needs the caller to be the authenticated student.
student_router = APIRouter(
    prefix="/students", tags=["suggestions"], dependencies=[Depends(require_own_profile)]
)

# Reviewer-scoped — there is no admin/staff role anywhere in this system,
# so this is gated by a static configured secret instead
# (`require_reviewer_secret`), not student auth. A valid student session
# grants zero access here.
router = APIRouter(
    prefix="/suggestions", tags=["suggestions"], dependencies=[Depends(require_reviewer_secret)]
)


def _suggestion_dto(suggestion) -> SuggestionDTO:
    return SuggestionDTO(
        id=suggestion.id,
        student_id=suggestion.student_id,
        category=suggestion.category,
        title=suggestion.title,
        description=suggestion.description,
        source_url=suggestion.source_url,
        context_type=suggestion.context_type,
        context_id=suggestion.context_id,
        context_metadata=suggestion.context_metadata,
        status=suggestion.status,
        review_notes=suggestion.review_notes,
        reviewed_at=suggestion.reviewed_at,
        created_at=suggestion.created_at,
        updated_at=suggestion.updated_at,
    )


@student_router.post("/{student_id}/suggestions", response_model=SuggestionDTO)
async def create_suggestion(
    student_id: str,
    body: CreateSuggestionRequest,
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionDTO:
    try:
        suggestion = submit_suggestion(
            student_id=student_id,
            category=body.category,
            title=body.title,
            description=body.description,
            source_url=body.source_url,
            context_type=body.context_type,
            context_id=body.context_id,
            context_metadata=body.context_metadata,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    saved = await suggestions.create(suggestion)
    return _suggestion_dto(saved)


@student_router.get("/{student_id}/suggestions", response_model=SuggestionsResponse)
async def list_my_suggestions(
    student_id: str,
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionsResponse:
    results = await suggestions.list_for_student(student_id)
    return SuggestionsResponse(suggestions=[_suggestion_dto(s) for s in results])


@student_router.get("/{student_id}/suggestions/{suggestion_id}", response_model=SuggestionDTO)
async def get_my_suggestion(
    student_id: str,
    suggestion_id: str,
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionDTO:
    suggestion = await suggestions.get_by_id(suggestion_id)
    if suggestion is None or suggestion.student_id != student_id:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return _suggestion_dto(suggestion)


@router.get("", response_model=SuggestionsResponse)
async def list_suggestions_for_review(
    status: str | None = Query(None),
    category: str | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionsResponse:
    results = await suggestions.list_all(
        status=status, category=category, search=q, limit=limit, offset=offset
    )
    return SuggestionsResponse(suggestions=[_suggestion_dto(s) for s in results])


@router.get("/{suggestion_id}", response_model=SuggestionDTO)
async def get_suggestion_for_review(
    suggestion_id: str,
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionDTO:
    suggestion = await suggestions.get_by_id(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return _suggestion_dto(suggestion)


@router.patch("/{suggestion_id}/status", response_model=SuggestionDTO)
async def update_suggestion_status(
    suggestion_id: str,
    body: UpdateSuggestionStatusRequest,
    suggestions: SuggestionRepository = Depends(get_suggestion_repository),
) -> SuggestionDTO:
    suggestion = await suggestions.get_by_id(suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    try:
        updated = update_status(suggestion, status=body.status, review_notes=body.review_notes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    saved = await suggestions.update(updated)
    return _suggestion_dto(saved)
