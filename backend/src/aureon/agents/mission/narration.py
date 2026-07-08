from aureon.agents.mission.mission import Mission


def _display_name(agent_name: str) -> str:
    return f"{agent_name.replace('_', ' ').title()} Agent"


def narrate_mission(mission: Mission) -> list[str]:
    """Turns a Mission's already-real ``stage_log`` and ``delegations``
    into human-readable lines — pure function, no side effects, not wired
    into any route or screen (this phase is backend observability only).

    Ordering: every stage the primary agent recorded is attributed to it
    first, then each delegation (in the order it happened) is narrated as
    a clear handoff — matching the worked example in the spec
    ("Decision Agent -> Delegating institution analysis... -> Institution
    Agent working... -> Institution Profile received -> Decision Agent
    continues reasoning"). This doesn't attempt fine-grained
    interleaving of exactly which stage happened before/after which
    delegation — ``Mission.stage_log`` doesn't tag entries with an agent,
    so this is an honest, real reconstruction from what's actually
    tracked, not a fabricated timeline.
    """
    primary_display = _display_name(mission.primary_agent)
    lines = [f"{primary_display} — {stage}" for stage in mission.stage_log]

    for delegation in mission.delegations:
        from_display = _display_name(delegation.from_agent)
        to_display = _display_name(delegation.to_agent)
        lines.append(f"{from_display} — Delegating {delegation.capability.value} to {to_display} ({delegation.reason})")
        lines.append(f"{to_display} working…")
        lines.append(f"{to_display.replace(' Agent', '')} Profile received")
        lines.append(f"{from_display} continues reasoning")

    return lines
