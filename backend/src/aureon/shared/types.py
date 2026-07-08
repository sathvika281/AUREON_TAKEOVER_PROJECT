from enum import StrEnum


class AgentName(StrEnum):
    """Canonical agent identifiers. Adding a future agent (e.g. Research,
    Scholarship, Resume, Interview, Portfolio, Internship, Market Trends)
    means adding one member here plus one module under
    agents/specialized/ — the orchestrator graph and registry require no
    changes since they build themselves from AgentRegistry.describe_all()."""

    DISCOVERY = "discovery"
    CAREER_INTELLIGENCE = "career_intelligence"
    DECISION = "decision"
    SKILL_GAP = "skill_gap"
    ROADMAP = "roadmap"
    MENTOR = "mentor"
    INSTITUTION = "institution"
    GROWTH = "growth"
    OPPORTUNITY = "opportunity"


class Mode(StrEnum):
    """Exploration Mode vs Recommendation Mode, per the product philosophy:
    the system must not recommend careers until it has enough confidence
    about the student. See agents/confidence_gate.py for the deterministic
    enforcement of that rule."""

    EXPLORATION = "exploration"
    RECOMMENDATION = "recommendation"
