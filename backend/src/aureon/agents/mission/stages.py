from aureon.shared.types import AgentName

#: Real workflow steps, not a generic "Thinking..." placeholder. Each
#: specialist appends only the subset of its own stages it actually
#: executed on a given call into ``AgentOutput.payload["execution_stages"]``
#: — never the full list unconditionally. See
#: ``agents/mission/orchestrator.py``'s ``MissionOrchestrator`` for how a
#: mission's ``stage_log`` aggregates these across a request.
#:
#: V5: reworded to be tool-aware — each stage now corresponds to a real
#: tool call (see each specialist's own ``tools.py``) or a real
#: deterministic step, not just a coarse phase name.
AGENT_EXECUTION_STAGES: dict[str, list[str]] = {
    AgentName.DISCOVERY.value: [
        "Reading Resume",
        "Analyzing Reflection Journal",
        "Extracting Evidence",
        "Updating Career DNA",
        "Building Discovery Report",
    ],
    AgentName.CAREER_INTELLIGENCE.value: [
        "Mission Planned",
        "Searching Sources",
        "Reading Web Pages",
        "Comparing Findings",
        "Cross-Verifying Information",
        "Knowledge Fusion",
        "Preparing Investigation Report",
    ],
    AgentName.DECISION.value: [
        "Reviewing Candidate Careers",
        "Comparing Trade-offs",
        "Delegating Required Analysis",
        "Building Decision Report",
    ],
    AgentName.ROADMAP.value: [
        "Reviewing Current Progress",
        "Planning Milestones",
        "Building Roadmap",
    ],
    AgentName.OPPORTUNITY.value: [
        "Searching Opportunities",
        "Filtering Expired Results",
        "Ranking Opportunities",
    ],
    AgentName.INSTITUTION.value: [
        "Reading Curriculum",
        "Reviewing Research Labs",
        "Comparing Institutions",
        "Building Institution Profile",
    ],
    AgentName.MENTOR.value: [
        "Reading Publications",
        "Comparing Expertise",
        "Matching Career DNA",
        "Preparing Mentor Report",
    ],
    AgentName.GROWTH.value: [
        "Reviewing Previous Reports",
        "Comparing Growth",
        "Identifying Patterns",
        "Preparing Progress Report",
    ],
    #: Phase 2 Foundation — real steps BuildOrchestrator/CareerOrchestratorAgent
    #: actually perform. Deliberately no entries for Network/Portfolio —
    #: they perform no real steps yet (pure registration placeholders).
    AgentName.CAREER_ORCHESTRATOR.value: [
        "Resolving Intent",
        "Selecting Agents",
        "Executing Mission",
        "Merging Outputs",
    ],
}
