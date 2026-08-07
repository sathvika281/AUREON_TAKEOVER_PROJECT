from fastapi import APIRouter

from aureon.api.v1 import (
    career_events,
    career_experience,
    career_experiments,
    career_exploration,
    career_intelligence,
    careers,
    conversation,
    decision,
    discovery_onboarding,
    documents,
    expert_connect,
    exposure,
    github_intelligence,
    growth,
    hidden_potential_routes,
    history,
    institutions,
    journey_stories,
    knowledge_circles,
    learning_styles,
    life_missions,
    mentors,
    mentorship,
    missing_worlds,
    opportunity_equality,
    parent_connect,
    search_investigation,
    skills,
    students,
    suggestions,
    talent_discovery,
    trends,
    url_investigation,
)

# Versioned routers only. `/health` is intentionally unversioned (mounted
# directly in main.py) since infra health checks shouldn't need to track
# API version bumps.
api_router = APIRouter(prefix="/v1")
api_router.include_router(conversation.router)
api_router.include_router(students.router)
api_router.include_router(discovery_onboarding.router)
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
api_router.include_router(trends.router)
api_router.include_router(exposure.router)
api_router.include_router(opportunity_equality.router)
api_router.include_router(career_experiments.router)
api_router.include_router(talent_discovery.router)
api_router.include_router(hidden_potential_routes.router)
api_router.include_router(missing_worlds.router)
api_router.include_router(skills.router)
api_router.include_router(life_missions.router)
api_router.include_router(learning_styles.router)
api_router.include_router(expert_connect.router)
api_router.include_router(parent_connect.router)
api_router.include_router(parent_connect.student_router)
api_router.include_router(journey_stories.router)
api_router.include_router(journey_stories.student_router)
api_router.include_router(knowledge_circles.router)
api_router.include_router(knowledge_circles.student_router)
api_router.include_router(mentorship.router)
api_router.include_router(mentorship.student_router)
api_router.include_router(suggestions.router)
api_router.include_router(suggestions.student_router)
