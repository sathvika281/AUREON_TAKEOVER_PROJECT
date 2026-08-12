# Aureon — Agentic Architecture

This document describes Aureon's actual multi-agent system: what's real,
what's a working scaffold, and what's an honest placeholder — verified
directly against `agents/orchestrator/graph.py`, `agents/registry.py`, and
every file under `agents/specialized/`, not described from a design intent.

See [`docs/diagrams/agent-orchestration.svg`](./diagrams/agent-orchestration.svg)
for the visual version.

## There is no hardcoded pipeline

The orchestrator is a real LangGraph `StateGraph`
(`agents/orchestrator/graph.py`), built entirely from
`AgentRegistry.describe_all()`. Every agent self-registers via
`BaseAgent.__init_subclass__` — adding a new agent to the system requires
exactly one new module under `agents/specialized/<name>/agent.py` and one
import line; `build_graph()` itself never changes.

The loop, once per user turn:

```
turn_start_node → planner_node → confidence_gate → <routed agent> → planner_node → ...
```

until the planner (or the gate, or a hop cap) routes to `END`.

- **`planner_node`** is the single agentic routing decision: a Groq
  tool-call (`tool_choice="required"`, parsed into a `PlannerDecision`)
  chosen live from the agent registry — never a hardcoded routing table.
  A hallucinated agent name is rejected defensively, falling back to
  ending the turn rather than crashing.
- **`confidence_gate`** is a deterministic override, not an LLM
  suggestion: if the planner's chosen agent is recommendation-stage
  (`is_recommendation_stage=True`) and the student's `confidence_score` is
  below `settings.min_recommendation_confidence` (default `0.6`), the
  route is forced back to Discovery regardless of what the LLM decided.
  Mentor is deliberately *not* gated — human handoff should never be
  artificially delayed by a confidence threshold.
- **Hop protection:** the orchestrator can legitimately loop more than
  once within a single turn (e.g. Discovery then Mentor) — this is
  genuinely agentic, not a bug — but `hop_count` is capped at `3`. Once
  reached, the planner skips its LLM call entirely and ends the turn.

## The 12 registered agents — an honest inventory

Confirmed by direct inspection of every file under `agents/specialized/`
(12 directories) for real `llm.complete(...)` calls versus a no-op
`run()` passthrough:

| Agent | Status | What it actually does |
|---|---|---|
| **Discovery** | 🟢 LLM-reasoning-live | Evidence-gathering conversation, Career DNA extraction, hypothesis formation/lifecycle, Why Engine, Reflection Journal |
| **Career Intelligence** | 🟢 LLM-reasoning-live | Reasons over the real Career Knowledge Base against Career DNA/Evidence Graph; the same `analyze_careers()` powers both the conversational path and the direct "Analyze My Fit" route |
| **Decision** | 🟢 LLM-reasoning-live | Decision Workspace composition, Career Comparison, Future Simulation reasoning |
| **Mentor** | 🟢 LLM-reasoning-live | Real expert matching; deliberately excluded from confidence gating |
| **Institution** | 🟢 LLM-reasoning-live | Real institution matching against Career DNA trait alignment |
| **Growth** | 🟢 LLM-reasoning-live | Longitudinal progress / interest-evolution reasoning |
| **Opportunity** | 🟢 LLM-reasoning-live | Transparent, multi-factor opportunity fit scoring |
| **Skill Gap** | 🟡 Working scaffold | Registered with a real description; its `run()` is an honest no-op passthrough — its own module docstring states the analysis logic lives elsewhere, not yet wired into this graph node |
| **Roadmap** | 🟡 Working scaffold | Registered, no live reasoning in the conversational graph yet |
| **Career Orchestrator** | 🔵 Deterministic coordinator | Real logic (`plan_execution()` resolves an objective into an ordered agent list via a registry), but no LLM call — its own `run()` is an honest passthrough for the conversational graph, since its real trigger is a separate Build Orchestrator path, not chat |
| **Network** | ⚪ Registered placeholder | Explicit docstring: "No real workflow yet" — a future facade over Mentor/Institution matching |
| **Portfolio** | ⚪ Registered placeholder | Same status as Network — reserved for future GitHub/document-based evidence extraction |

**7 of 12 are genuinely LLM-reasoning-live via Groq today.** This table is
deliberately precise rather than rounded up — an agent registered in the
graph is not the same claim as an agent that reasons.

## Where context is retrieved

- **Career Knowledge Base** (`careers`, `skills`, `companies`, `projects`,
  `trends` — real Supabase tables): the LLM reasons over the *entire*
  current seed in one prompt call per analysis (27 careers is small enough
  to fit comfortably) — not vector similarity, not embeddings. A known,
  disclosed scaling limit, not solved prematurely.
- **StudentProfile**: loaded once per conversation turn by
  `domain/services/conversation_service.py`, threaded through
  `AureonState["student_profile"]`.

## How student state affects reasoning

Every specialized agent's prompt is built from the student's own
already-persisted evidence — Career DNA scores, prior hypotheses,
evidence-graph entries, World Signals — never from a generic profile
template. The Discovery Agent's system prompt explicitly enforces a
**Reasoning Discipline**: no repeated questions, no re-litigating a
resolved "why" topic, every claim must trace to something the student
actually said.

## Confidence and uncertainty — bounded in code, not just prompted

This is the platform's clearest structural safeguard, and it's real,
tested code, not a prompt instruction alone:

1. **The gate** (`agents/confidence_gate.py`) — described above.
2. **The ceiling** (`agents/specialized/discovery/confidence.py`): the
   Discovery Agent's LLM proposes a confidence score each turn, but the
   *effective* score is `min(llm_suggested, deterministic_ceiling(evidence_count))`.
   The ceiling grows linearly with accumulated evidence, so confidence
   cannot be talked up by the LLM after only a few exchanges.
3. **Reused for Career Candidates** (`agents/specialized/career_intelligence/confidence.py`):
   the same ceiling philosophy — zero supporting evidence caps confidence
   near 0.2 regardless of what the LLM states, and the raw float is
   **never shown to the student**, only a qualitative label (Strong /
   Growing / Needs More Evidence).

## Memory design

Two persistence tiers:

- **`Conversation`/`Turn`** (session-scoped): the raw transcript.
- **`StudentProfile`** (person-scoped, cross-session): `career_dna`,
  `evidence_graph`, `career_hypotheses`, `career_candidates`,
  `notebook_entries`, `reflection_journal`, `decision_memory`,
  `discovery_onboarding` (World Signals, Uncertainty Signals),
  `project_attempts`, and `foundation_memory` (Career Memory's identity
  model — e.g. `academic_level`, derived from onboarding's `stage`
  answer and genuinely consumed by Opportunity's scoring logic).

The Evidence Graph is the single source of truth for evidence — trait,
hypothesis, and career-candidate evidence lists are all computed by
filtering `evidence_graph` when a response DTO is built, never stored
redundantly in more than one place.

## A lesson learned, kept for anyone touching this code next

An early version of the planner's prompt referenced the whole-session
`agent_history` instead of the *current turn's* activity, which made the
planner think every turn was "still in progress" and re-invoke Discovery
up to the hop cap on every single message. Fixed by grounding the prompt
in `state["agent_outputs"]` (turn-scoped) instead. Kept here because it's
exactly the class of subtle agentic-loop bug worth a future engineer
knowing about before they touch `planner_node` again.
