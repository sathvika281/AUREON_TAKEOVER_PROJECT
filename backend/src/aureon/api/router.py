from fastapi import APIRouter

from aureon.api.v1 import (
    career_events,
    career_experience,
    career_exploration,
    career_intelligence,
    careers,
    conversation,
    decision,
    documents,
    github_intelligence,
    growth,
    history,
    institutions,
    mentors,
    search_investigation,
    students,
    url_investigation,
)

# Versioned routers only. `/health` is intentionally unversioned (mounted
# directly in main.py) since infra health checks shouldn't need to track
# API version bumps.
api_router = APIRouter(prefix="/v1")
api_router.include_router(conversation.router)
api_router.include_router(students.router)
api_router.include_router(career_intelligence.router)
api_router.include_router(careers.router)
api_router.include_router(career_exploration.router)
api_router.include_router(decision.router)
api_router.include_router(mentors.router)
api_router.include_router(institutions.router)
api_router.include_router(growth.router)
api_router.include_router(url_investigation.router)
api_router.include_router(documents.router)
api_router.include_router(github_intelligence.router)
api_router.include_router(search_investigation.router)
api_router.include_router(history.router)
api_router.include_router(career_events.router)
api_router.include_router(career_experience.router)
