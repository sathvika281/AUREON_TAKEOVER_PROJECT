# Aureon — Architecture

This document describes Aureon's architecture as it actually exists in the
repository today: how a request flows from the browser to a real answer,
how the agentic orchestration works, and the boundaries between layers.
It supersedes the phase-by-phase account in earlier drafts of this file —
those are preserved in [`IMPLEMENTATION_TRACKER.md`](./IMPLEMENTATION_TRACKER.md)
as the execution history; this document only describes current reality.

## Monorepo layout

```
Aureon/
├── frontend/   React 18 · TypeScript · Vite · Tailwind CSS · React Router 7
├── backend/    Python · FastAPI · LangGraph · Pydantic v2
├── backend/db/migrations/   31 hand-authored, forward-only SQL files
└── docs/       this document + PRODUCT_FLOW / AGENTIC_ARCHITECTURE /
                KNOWLEDGE_GRAPH / EVIDENCE_ENGINE / SECURITY / DECISIONS
```

## Clean architecture boundaries

- **`api/`** (36 route modules under `api/v1/`) parses requests and calls
  `domain/services/*` only — it contains no business logic and never
  imports agents or repositories directly.
- **`domain/`** holds framework-agnostic Pydantic models and services. It
  depends on `agents/` and `services/`, but nothing depends on it upward
  except `api/`.
- **`agents/`** (the multi-agent system) depends on `services/llm` and
  `services/supabase` for infrastructure, never the reverse.
- **`services/llm`** and **`services/supabase`** know nothing about agents
  or domain models — pure, swappable infrastructure.
- **`core/config.py`** is the only place that reads environment variables;
  everything else receives a `Settings` object via dependency injection.

## Request flow

### Conversational turn (Discovery, Career Intelligence, and any
planner-routed agent)

```
React (Vite/TS)
    │  POST /v1/conversation/turn
    ▼
FastAPI api/v1/conversation.py        (thin route — no business logic)
    │
    ▼
domain/services/conversation_service.py   (loads StudentProfile + Conversation)
    ▼
agents/orchestrator/graph.py   (LangGraph StateGraph)
    │
    ├─ turn_start_node    resets per-turn fields
    ├─ planner_node        Groq tool-call decides the next agent (or END)
    ├─ confidence_gate     deterministic override — blocks recommendation-
    │                      stage agents below the confidence floor
    └─ <agent>.run(state)  the routed specialized agent, then back to planner
    │                      (capped at HOP_CAP = 3 planner passes per turn)
    ▼
services/llm (Groq)  +  services/supabase (repositories)
    ▼
response DTO ──▶ frontend
```

See [`AGENTIC_ARCHITECTURE.md`](./AGENTIC_ARCHITECTURE.md) for the full
orchestration design, the real agent registry, and the confidence
safeguards.

### Direct, non-conversational reads

Most of the product is not a chat interface. Career Explorer, the
Knowledge Base (Skills/Companies/Projects), Decision Lab, Expert Connect,
and every other browse/detail screen call plain REST routes that read
directly from repositories — no LangGraph, no LLM call, no planner. The
conversational path exists specifically for Your Universe's identity
discovery and for the handful of "analyze my fit" actions (Career
Intelligence, Opportunity) that reuse the same underlying reasoning
functions as their conversational counterparts rather than duplicating
them.

```
GET  /v1/careers[?category=&industry=&country=&q=]   CareerRepository — no LLM, no gating
GET  /v1/careers/{id}[?student_id=]                    CareerRepository — personalizes story ordering
POST /v1/students/{id}/career-candidates/analyze       analyze_careers() — the direct trigger
GET  /v1/students/{id}/career-candidates               reads persisted candidates only
GET  /v1/students/{id}/discovery-profile                restores the Discovery Notebook, no replay
GET  /v1/students/{id}/progressive-discovery             onboarding + World Signal state
```

## Backend layers, top to bottom

| Layer | What it owns |
|---|---|
| `api/v1/*.py` | Request/response parsing, auth dependency wiring (`require_own_profile`) |
| `domain/services/*` | Business logic: evidence recording, confidence ceilings, DTO composition |
| `domain/models/*` | Pydantic models — `StudentProfile`, `Career`, `Skill`, `Company`, `Project`, `EvidenceRecord`, `CareerCandidate`, `CareerHypothesis`, `DiscoveryOnboarding`, and more |
| `agents/` | The LangGraph orchestrator + 12 specialized agents (see `AGENTIC_ARCHITECTURE.md`) |
| `services/llm` | Provider-agnostic `LLMClient` protocol; `GroqClient` is the only implemented adapter |
| `services/supabase` | Repository pattern — one repository class per entity, wrapping `supabase-py`'s sync client in `run_in_threadpool` |

## Data storage shape

Two deliberate shapes, chosen per access pattern, both real:

- **jsonb-per-identity blob** (`student_profiles`): read/written whole as
  one Pydantic-modeled object per request — `career_dna`, `evidence_graph`,
  `career_hypotheses`, `discovery_onboarding`, `project_attempts`,
  `career_candidates`, and more all live as columns/jsonb fields on this
  one table, keyed by `student_id` (the real, authenticated Supabase
  `auth.uid()`).
- **Normalized rows** (`careers`, `skills`, `companies`, `projects`,
  `trends`, `mentors`, `institutions`, `career_stories`, `knowledge_circles`,
  `conversations`/`turns`): real columns, real indexes, queried and
  filtered directly. Cross-entity edges (`required_skill_ids`,
  `company_ids`, `target_skill_ids`, `related_career_ids`, ...) are typed
  `jsonb` id arrays, not foreign-key-enforced join tables — a deliberate,
  documented trade-off at the current catalog scale (see
  [`TECHNICAL_DEBT_REGISTER.md`](./TECHNICAL_DEBT_REGISTER.md)).

RLS is intentionally off — the backend authenticates with Supabase's
service-role key and enforces per-student scoping itself in application
code (`require_own_profile`), not at the Postgres row level. See
[`SECURITY.md`](./SECURITY.md) for the full authorization model.

Migrations are 31 hand-authored, forward-only SQL files under
`backend/db/migrations/`, applied manually via the Supabase SQL Editor —
no migration-runner tool is adopted yet (tracked as the top item in the
Technical Debt Register).

## Frontend

`App.tsx` gates the whole authenticated app behind `ProtectedRoute` (valid
Supabase session) and `OnboardingGate` (onboarding completed), then
mounts one provider per feature area (`DiscoveryProvider`,
`CareerIntelligenceProvider`, `DecisionProvider`, `HistoryProvider`, and
others) around the routed screens. Each provider fetches its own
persisted state once on mount and performs no client-side derivation —
every computed field (Career DNA trait scores, hypothesis status,
Hidden Potential patterns, understanding-level labels) is computed
server-side and simply rendered, which is what lets the product survive a
hard refresh or a new device without losing state.

Navigation (`features/navigation/journeyConfig.ts`) is the single source
of truth for both the sidebar and route registration, organized into five
stage groups: the four guided, evidence-gated stages (**Discover, Explore,
Connect, Decide**) plus a fifth, deliberately ungated **Knowledge Base**
(Skills/Companies/Projects) reachable at any time. A module's `locked`
flag drives whether it renders its real screen or a `LockedModule`
placeholder that explains *why* a stage isn't available yet — never
"Coming Soon."

Design system: `Surface`/`Badge`/`Button`/`Input`/`PageHeader`/
`EmptyStatePanel`/`FilterPill` (`design-system/components/`), a shared
`cn()` (clsx + tailwind-merge), and the Observatory palette defined in
`tailwind.config.ts` — one true interactive accent color, two scarce
semantic colors (gold for achievement, success for status), everything
else confined to near-invisible atmospheric glow. See the palette table
in the root [`README.md`](../README.md).

## Configuration

`pydantic-settings`-based `Settings` (`core/config.py`) — environment,
Supabase credentials, LLM provider/model, `min_recommendation_confidence`
(default `0.6`), CORS origins, log level/format. `.env.example` documents
every key; see [`SECURITY.md`](./SECURITY.md) for what must never be
committed.

## Deployment

- **Frontend**: static build (`npm run build:gh-pages`) deployed to
  GitHub Pages.
- **Backend**: Render (`render.yaml`), `uvicorn aureon.main:app`, secrets
  injected via the Render dashboard, never committed.
- **Database/Auth**: Supabase (PostgreSQL + Supabase Auth).

Sprints 1-5 are live in this configuration today. Sprints 6-11
(account self-service, state-integrity, and design-system consolidation
work) are complete, tested, and committed locally, with release handled
as a separate, deliberate step.

## Verification

- Backend: `pytest` — 811 tests passing at the time of writing, covering
  agent self-registration, orchestrator graph compilation, the confidence
  gate, every domain service, repository/DTO composition, and route-level
  behavior, all via `FakeLLMClient`/fake-Supabase-client test doubles — no
  network calls in the suite.
- Live verification: every feature area has been driven end-to-end
  against the real Groq + Supabase stack via headless-Chromium (Playwright)
  walkthroughs, using ephemeral test accounts created and deleted per
  session — not just unit-tested in isolation.
