# Phase 2 Foundation — Architecture

This document explains how the Phase 2 foundation works without requiring readers to inspect the code. It is authored progressively — Milestone A wrote the first two sections below; Milestones B/C/D each appended their own section as that subsystem was built.

## Component diagram

```
BuildOrchestrator ──► MissionOrchestrator, AgentRegistry, objective_registry, EventBus
EventBus            ──► (nothing but its own Event/EventType)
foundation bootstrap ──► EventBus + career_memory.service + universe_evolution   (the ONLY file depending on all three)
career_memory.service ──► domain.models.career_memory, domain.models.student_profile
universe_evolution    ──► events.types only
journey_guidance       ──► domain.models.progress_report, domain.models.career_memory
```

No cycles. `EventBus` is the most decoupled piece — it never knows `career_memory` or `universe_evolution` exist; `services/foundation/events/handlers.py` is the one bootstrap file that wires subscribers, mirroring how `agents/specialized/__init__.py` is the one place that wires new agents.

`BuildOrchestrator` (`agents/foundation/build_orchestrator.py`) lives under `agents/` because its job is coordinating *agents* via the `Mission` substrate (same neighborhood as `agents/mission/`). Career Memory, the Event Bus, Universe Evolution, and Journey Guidance live under `services/foundation/` — Shared Services that agents consume but never own.

## Request flow — one `handle_request` call, end to end

1. Caller provides `student_id`, `objective` (e.g. `"mentor_match_analysis"`), and an `LLMClient`.
2. `BuildOrchestrator` loads the student's `StudentProfile` via `StudentProfileRepository`.
3. `CareerOrchestratorAgent.plan_execution(objective=..., profile=...)` resolves the registered `ExecutionPlan` for that objective (`agents/foundation/objective_registry.py`) — raises `ValueError` for an unregistered objective.
4. `MissionOrchestrator.create_mission(...)` starts a `Mission` with the plan's `primary_agent`.
5. Any resources the plan's steps need (e.g. the real mentor/institution list) are loaded once via `plan.load_resources()`.
6. For each `ExecutionStep`: if the step's agent *is* the primary agent, its `build_call` runs directly (no delegation — mirrors how Growth's real route already works today); otherwise `MissionOrchestrator.delegate(...)` runs it, enforcing capability ownership. A step that raises is caught, recorded in `failed_agents`, and does not stop the remaining steps.
7. `MissionOrchestrator.complete(mission)` (or the mission is left `FAILED` if every step failed).
8. `BuildOrchestrator` computes `evidence` (real per-output-type field pulls), `confidence`/`confidence_basis` (deterministic ceiling from real counts, no LLM call), `conflicts` (a real, currently-always-empty extension point), and `reasoning` (one deterministic templated sentence).
9. (Milestone C onward) the objective is looked up in the event registry; if mapped, an `Event` is published through the `EventBus`, whose subscribers record Career Memory changes and evaluate a `UniverseEvent`.
10. (Milestone D onward) for objectives that produce a `ProgressReport`, `JourneyGuidanceEngine.guide(...)` computes one recommendation.
11. A single `BuildOrchestratorResponse` is returned, carrying everything above.

## Build Orchestrator lifecycle

`objective` (string) → `ExecutionPlan` (registered recipe) → `Mission` (ephemeral coordination record, created/executed/completed via the pre-existing `MissionOrchestrator`) → merged `BuildOrchestratorResponse` (confidence, evidence, reasoning, plus memory/event/universe/guidance fields wired in later milestones). No route calls this yet in this foundation — it exists as a tested, working service layer for a future API route to call.

## Career Memory flow

`StudentProfile.foundation_memory: CareerMemory` is the persisted home for the five domains (Identity/Evidence/Opportunities/Connections/Growth). `services/foundation/career_memory/service.py`'s plain functions are the only way anything reads or writes it:

- `record_evidence_artifact` / `record_opportunity_entry` / `record_growth_skill` / `record_growth_mission` / `record_interview_practice` each append one real record to their domain.
- `get_identity` surfaces only `preferred_industries` (the one identity field with no existing home) — everything else identity-related is read live from `StudentProfile`'s own top-level fields.
- `get_connections` is **fully derived** — it never stores anything itself, only computes real `Connection`s from `StudentProfile.mentor_matches` (active only) and `mentor_interactions` on every call.
- `get_career_memory_snapshot` is the one combined read every future consumer uses.

## Event flow

`services/foundation/events/types.py` defines `EventType` (`PROJECT_COMPLETED`, `SUGGESTED_ACTIVITY_COMPLETED`, `INTERNSHIP_ADDED`, `NEW_CERTIFICATE`, `RESEARCH_PAPER_ADDED`, `MENTOR_CONNECTED`, `PORTFOLIO_UPDATED`, `INTERVIEW_FINISHED`, `SKILL_VERIFIED`, `CAREER_READINESS_INCREASED`) and the `Event` envelope. `services/foundation/events/bus.py`'s `EventBus` is in-process pub/sub — `publish(event)` calls every subscriber for that event type in registration order, isolating any subscriber that raises so one failure never blocks the rest or fails the publish call itself.

`services/foundation/events/objective_event_registry.py` maps a Build Orchestrator objective to an `EventType`, starting genuinely empty — none of today's 3 real objectives honestly correspond to one of these events (every event belongs to a not-yet-built Phase 2 feature). A future feature registers its own mapping from its own module.

`services/foundation/events/handlers.py`'s `register_default_subscribers` wires this foundation's two subscribers to every `EventType`:
1. **Career Memory recording** — reads the already-loaded, already-saved `StudentProfile` straight from `event.payload["profile"]` (in-process pub/sub, so passing the live object is correct — no separate repository re-fetch, no stale-reference risk) and returns a description of Career Memory's current non-empty domains.
2. **Universe Evolution** — calls `UniverseEvolutionEngine().evaluate(event)`, which maps a handful of `EventType`s to a semantic `UniverseEventType` (`SATELLITE_ADDED`, `STAR_APPEARED`, `CONSTELLATION_EXPANDED`, `GUIDING_STAR_BRIGHTENED`, `DARK_MATTER_BECAME_STAR`, `SUN_ROSE`, `MOON_BRIGHTENED`) and returns `None` for anything unmapped — purely semantic, no coordinates/colors/animation; a future, separate frontend phase decides how each `UniverseEventType` actually renders.

`BuildOrchestrator.handle_request` looks up the objective's registered `EventType` after the mission completes and the profile is saved; if one exists, it publishes an `Event` (carrying the profile in its payload) and merges the two subscribers' results into `response.memory_changes` and `response.universe_event`. This replaced Milestone B's temporary direct `career_memory.service` call — see the Architectural Decisions Log for why.

## Journey Guidance flow

`services/foundation/journey_guidance.py`'s `JourneyGuidanceEngine.guide(*, progress_report, career_memory)` is a thin, real reuse of `ProgressReport.next_priorities` (already computed deterministically by Growth's `evidence_summary.py`, with an LLM narrative layered on top) — Stage 1 does not build a cross-Career-Memory-domain override table, since nothing else in this foundation produces real signal through Build Orchestrator yet (Network/Portfolio are inert placeholders). It returns `None` whenever the report is missing or itself `insufficient_evidence`, never a fabricated recommendation.

The one real classification step: `_classify_action` maps Growth's own free-text top-priority `action` string to a `JourneyActionType` via a keyword heuristic (mirrors the frontend's `MissionCard.tsx` category-label pattern) — falling back honestly to `COMPLETE_TODAYS_MISSION` when no keyword matches, rather than guessing.

`BuildOrchestrator.handle_request` looks for any `ProgressReport` among the mission's artifacts (not gated by objective name — dispatches on the real artifact type, same pattern as `_extract_evidence`) and, if found, calls `JourneyGuidanceEngine().guide(...)`, setting `response.journey_guidance`.

This is the flagship end-to-end path exercised by `tests/agents/foundation/test_build_orchestrator.py::test_handle_request_progress_intelligence_analysis_full_pipeline` — real intent resolution, real mission execution, real confidence/evidence/reasoning, and (when Growth's real output has a top priority) real Journey Guidance, all from genuinely seeded evidence, no synthetic objectives involved.
