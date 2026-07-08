# Aureon — Architecture

Aureon is an AI-native, multi-agent Career Intelligence Platform. This
document describes the architecture: how requests flow, how the agentic
orchestration works, and the design decisions behind it.

Three phases are reflected here:
1. **Scaffold** — folder structure, clean-architecture layers, the
   LangGraph orchestrator skeleton, provider-agnostic LLM/Supabase
   infrastructure.
2. **Phase 1 — Discover Yourself** — the Discovery Agent's conversation
   loop, Why Engine, Exploration Mode, Reflection Journal, Career DNA,
   Evidence Graph, Discovery Notebook, Career Hypothesis Engine (with a
   real lifecycle), Hidden Potential, and Understanding Level are all
   real, server-persisted, and live-verified against Groq and Supabase.
3. **Phase 2 — Explore Careers** — a real Career Intelligence Agent
   reasons over Phase 1's outputs against a structured Career Knowledge
   Base (Supabase tables, not prompt text) to produce evidence-grounded
   Career Candidates, surfaced through Career Intelligence, Global Career
   Discovery, Career Reality, Future Lens, and Human Stories.

The remaining 6 specialized agents (Decision, Skill Gap, Roadmap, Mentor,
Institution, Growth) remain honest no-op stubs, reachable by the
orchestrator but not yet implemented — later phases.

## Product philosophy

Aureon is not a quiz app. It gradually discovers a student through
accumulated evidence rather than assumptions, and it must not recommend
careers until it has enough confidence about the student — Exploration
Mode continues instead. Recommendations get more accurate over time
rather than being generated immediately from one interaction. "Never
Assume. Always Discover." Phase 2 extends this to career matching: every
career surfaced is a *candidate* grounded in real evidence, never a
recommendation, and never a raw confidence number — only qualitative
Evidence Strength labels (Strong / Growing / Needs More Evidence).

## Monorepo layout

```
Aureon/
├── backend/    Python / FastAPI / LangGraph
├── frontend/   React / Vite / TypeScript / Tailwind
├── docs/       this file
└── docker-compose.yml
```

## Agent ownership map

| Feature | Owner | Collaborates with | StudentProfile fields touched |
|---|---|---|---|
| Discovery Journey (conversation loop) | Discovery Agent | Orchestrator planner (routing only) | `career_dna`, `confidence_score`, `confidence_history` |
| Why Engine | Discovery Agent (a reasoning technique inside its single LLM call, not a separate node) | — | feeds evidence quality upstream |
| Exploration Mode | Discovery Agent | — | `notebook_entries` (mission suggestions cite a specific gap via `reason`) |
| Reflection Journal | Discovery Agent | `ReflectionEvidenceSource` | `reflection_journal` |
| Career DNA | Discovery Agent | — | `career_dna`, `evidence_graph` |
| Evidence Graph | Discovery Agent (traits/hypotheses) + Career Intelligence Agent (careers) | — | `evidence_graph` — single source of truth for all evidence, cross-referenced by `related_trait` / `related_hypothesis` / `related_career` |
| Discovery Notebook | Discovery Agent + Career Intelligence Agent | — | `notebook_entries` — observations + belief revisions, server-persisted |
| Career Hypothesis Engine | Discovery Agent | — | `career_hypotheses` (full lifecycle: investigating → growing → strong → validated, or discarded) |
| Hidden Potential | computed at the API layer (`agents/specialized/discovery/hidden_potential.py`), not a separate agent call | — | derived from `career_dna` + `evidence_graph`, not persisted |
| Understanding Level | computed at the API layer (`agents/specialized/discovery/understanding_level.py`) | — | derived, not persisted |
| Career Intelligence | Career Intelligence Agent | Reads Discovery's `career_dna`/`evidence_graph`/`career_hypotheses`/`notebook_entries` | `career_candidates`, `evidence_graph` (`related_career`), `notebook_entries` |
| Global Career Discovery / Career Reality / Future Lens / Human Stories | Career Intelligence Agent's Knowledge Base (data, not a reasoning call) | — | none — reads the `careers`/`career_stories` tables directly |

## Request flow

### Conversational turn (Discovery, and Career Intelligence when planner-routed)

```
React (Vite/TS)
    │  POST /v1/conversation/turn
    ▼
FastAPI api/v1/conversation.py            (thin route — no business logic)
    │
    ▼
domain/services/conversation_service.py   (coordinates repositories + orchestrator)
    │  loads StudentProfile (long-term)     │  loads/creates Conversation (session-scoped)
    │  resume-vs-new: checks graph.aget_state() so a continuing thread gets only the
    │  incremental message update, not a full state rebuild (see below)
    ▼
agents/orchestrator/graph.py  (LangGraph StateGraph)
    │
    ├─ turn_start_node      resets per-turn fields (agent_outputs, hop_count, ...)
    ├─ planner_node          LLM decides next agent (or END) from AgentRegistry.describe_all()
    ├─ confidence_gate       deterministic override: blocks recommendation-stage agents
    │                        below MIN_RECOMMENDATION_CONFIDENCE, regardless of the LLM
    └─ <agent>.run(state)    the routed specialized agent node, then back to planner
    │                        (capped by hop_count — see "Runaway-hop protection")
    ▼
services/llm (Groq)  +  services/supabase (repositories)
    │
    ▼
response DTO ──▶ frontend (reply + career_dna + hypotheses + notebook + hidden_potential + ...)
```

### Direct, non-conversational reads (Phase 2's primary UI trigger)

Career Intelligence's main interface is a button ("Analyze My Fit"), not
a chat message — "conversation optional" per the product spec. These
routes bypass the LangGraph planner entirely, since they aren't
conversational turn-taking, but call the *same* underlying reasoning
function (`analyze_careers()`) the conversational path uses:

```
POST /v1/students/{id}/career-candidates/analyze  ──▶ analyze_careers() ──▶ upsert_candidates()
GET  /v1/students/{id}/career-candidates          ──▶ reads persisted StudentProfile only
GET  /v1/careers[?category=&industry=&country=&q=] ──▶ CareerRepository (no LLM, no gating)
GET  /v1/careers/{career_id}[?student_id=]         ──▶ CareerRepository (no LLM)
```

## Clean architecture boundaries

- `api/` parses requests and calls `domain/services/*` only — it never
  imports agents or repositories directly, and contains no business logic.
- `domain/` holds framework-agnostic models and services; it depends on
  `agents/` and `services/` but nothing depends on it upward except `api/`.
- `agents/` (the multi-agent system) depends on `services/llm` and
  `services/supabase` for infrastructure, never the reverse.
- `services/llm` and `services/supabase` know nothing about agents or
  domain models — pure infrastructure, swappable independently.
- `core/config.py` is the only place that reads environment variables;
  everything else receives `Settings` via dependency injection.
- One exception, deliberate: agents that need infrastructure the graph
  builder doesn't inject (e.g. `CareerIntelligenceAgent` needing the
  Career Knowledge Base) instantiate their repository directly
  (`CareerRepository()`) rather than threading a new dependency through
  every agent's `run()` signature — mirrors how `confidence_gate.py`
  calls `get_settings()` directly. Scoped to the one agent that needs it,
  not a general pattern change.

## The agentic orchestrator

There is no hardcoded pipeline. The orchestrator is a LangGraph
`StateGraph` (`agents/orchestrator/graph.py`) built entirely from
`AgentRegistry.describe_all()`. Its loop is: **turn_start → planner →
confidence gate → routed agent → back to planner**, until the planner
(or the gate, or the hop cap) routes to `END`.

- **`planner_node`** is the single agentic routing point: an LLM call
  (Groq tool-calling, forced via `tool_choice="required"`, parsed into a
  `PlannerDecision`) decides which agent runs next, reading live from the
  registry — never a hardcoded routing table. Hallucinated agent names
  are rejected defensively (fall back to ending the turn).
- **`route_from_planner`** is a purely mechanical LangGraph edge function:
  it reads `state["active_agent"]` (already decided upstream) and returns
  it, or `END`.

### Runaway-hop protection

The orchestrator can legitimately loop `agent → planner → agent` more
than once within a single user turn (e.g. Discovery then Mentor) — this
is genuinely agentic, not a bug. But it must stay bounded: `hop_count`
(reset to 0 each turn by `turn_start_node`) increments every planner
pass, capped at `HOP_CAP = 3`. Once reached, `planner_node` skips the LLM
call entirely and ends the turn gracefully — the agent(s) that already
ran this turn already produced a reply. **Lesson learned building this**:
an early version of the planner's prompt referenced the whole-session
`agent_history` instead of *this turn's* activity (`agent_outputs`
keys), which made the planner think every turn was "still in progress"
and re-invoke Discovery up to the hop cap on every single message. Fixed
by grounding the prompt in `state["agent_outputs"]` (turn-scoped) and
whether the latest message is already an `AIMessage`.

### Confidence: deterministic gate + deterministic ceiling

The product principle "must not recommend on low confidence" is enforced
as **deterministic code** in two places, not just an LLM instruction:

1. **The gate** (`agents/confidence_gate.py`): if the planner's chosen
   agent is recommendation-stage (`is_recommendation_stage=True` —
   Career Intelligence, Decision, Roadmap) and `confidence_score` is
   below `settings.min_recommendation_confidence` (default `0.6`), the
   route is overridden back to Discovery regardless of the LLM's
   decision. **Mentor is deliberately not gated** — human handoff must
   stay reachable at any confidence level. This gate only applies to the
   *conversational* path to Career Intelligence — the direct analyze
   route applies its own, separate, lower evidence floor (see below),
   since it's a different, exploration-oriented use case.
2. **The ceiling** (`agents/specialized/discovery/confidence.py`): the
   Discovery Agent's LLM proposes a confidence score each turn, but the
   *effective* score is `min(llm_suggested, deterministic_ceiling(evidence_count))`.
   The ceiling grows linearly with accumulated evidence
   (`EVIDENCE_COUNT_FOR_FULL_CONFIDENCE = 8`), so confidence cannot be
   talked up by the LLM after only a few exchanges.
3. **Reused for Career Candidates** (`agents/specialized/career_intelligence/confidence.py`):
   the same deterministic-ceiling philosophy, applied to candidate
   confidence — zero supporting evidence caps near 0.2 regardless of the
   LLM's stated number, contradicting evidence lowers it further. The
   float itself is **never shown to the student** — only a qualitative
   `evidence_strength_label()` (Strong / Growing / Needs More Evidence).

### Agent registry — the extensibility mechanism

`AgentRegistry` + `BaseAgent.__init_subclass__` auto-registration is what
lets a new agent be added without touching the orchestrator or any
existing agent. Every agent's `run(self, state, *, llm)` receives an
injected `LLMClient` (mirroring how `planner_node` receives one).

**Adding a future agent (Decision, Skill Gap, Roadmap, Mentor,
Institution, Growth are already registered as stubs; further agents like
Research, Scholarship, Resume, Interview, ...) requires exactly two
changes:** a new/updated module under `agents/specialized/<name>/agent.py`,
and (for a brand-new agent) one import line in `agents/specialized/__init__.py`.

### Discovery Agent — real implementation

One structured LLM call per turn (Groq tool-calling via a
`DiscoveryTurnOutput` tool schema — `agents/specialized/discovery/schemas.py`)
captures the reply, extracted evidence, Career DNA updates, Why Engine
probing, a reflection prompt, hypothesis updates, a suggested activity,
and confidence atomically. `agents/specialized/discovery/prompts.py`
builds the system prompt (philosophy, Why Engine rules, Career DNA trait
vocabulary, Hypothesis Engine framing, and an explicit **Reasoning
Discipline** section — no repeated questions, no circling back to a
resolved why-topic, every claim must trace to something the student
actually said, confidence calibration, never phrase a hypothesis as a
recommendation) plus a live summary of the student's current DNA/
hypotheses/evidence/why-probe history.

- **Why Engine**: the LLM is told never to accept a surface-level answer
  and to probe "why" — but depth is capped deterministically at 2 per
  topic (`WHY_PROBE_DEPTH_CAP` in `agent.py`), overriding the LLM's own
  `probe.is_probing` flag if it tries to exceed the cap. Tracked in
  `AureonState.why_probe_state: dict[str, int]`.
- **Exploration Mode**: when evidence is thin, the LLM may propose a
  `suggested_activity`, grounded in a specific `missing_evidence` gap or
  weak hypothesis — its `reason` field must name that gap explicitly,
  never a generic "to learn more about yourself."
- **Reflection Journal**: `AureonState.pending_reflection_prompt` carries
  a just-asked reflection question across the turn boundary; when the
  student's next message answers it, `DiscoveryAgent.run` records a
  `ReflectionEntry` on the profile and clears the pending prompt.
- **Career DNA / Evidence Graph**: `CareerDNA.apply_update()` merges each
  trait update in place (clamped to [0,1]); every update that actually
  changes a trait's score/summary (deduped against the unchanged case,
  since the LLM sometimes re-states an identical reading) becomes one
  `EvidenceRecord` (`related_trait` set) plus one `NotebookEntry`
  (`kind="observation"`) — both server-persisted.
- **Hypothesis Engine + lifecycle**: `CareerHypothesis.status` is one of
  `investigating` / `growing` / `strong` / `validated` / `discarded`,
  computed **deterministically** from confidence + mode
  (`hypothesis_lifecycle.py::compute_status`) — never LLM-self-reported,
  since asserting your own confidence tier would be exactly the kind of
  unearned certainty this product refuses to allow. A hypothesis absent
  from a turn's output is marked `discarded` (kept, not deleted, so its
  history survives) rather than silently vanishing. Every status change
  or confidence shift ≥0.15 writes a `NotebookEntry` (`kind="belief_revision"`)
  with a structured previous-state → new-evidence → updated-belief →
  reason story. Supporting/contradicting evidence is **not** stored on
  the hypothesis itself — computed by filtering `evidence_graph` for
  `related_hypothesis` when a DTO is built (`domain/services/profile_view.py`),
  so there is exactly one place evidence lives.
- **Hidden Potential** (`hidden_potential.py`): a deterministic
  co-occurrence heuristic (two traits both ≥0.5) computed fresh at the
  API-response layer from `career_dna` + `evidence_graph` — no extra LLM
  call, not persisted (fully derivable from already-persisted data).
- **Understanding Level** (`understanding_level.py`): the Discovery
  Journey's stage label + narrative, also computed fresh at the
  API-response layer from the same already-persisted fields.

### Career Intelligence Agent — real implementation (Phase 2)

`agents/specialized/career_intelligence/` reasons about which real
careers from the Career Knowledge Base fit a student, grounded in their
Career DNA, Evidence Graph, and hypotheses — explicitly **not**
recommendation, keyword matching, or vector similarity:

- **`reasoning.py::analyze_careers()`** is the single reasoning entry
  point, called by both `CareerIntelligenceAgent.run()` (conversational,
  planner-routed) and the direct analyze API route — one implementation,
  not two. It builds a compact prompt: the student's evidence-backed
  profile summary plus one line per Career Knowledge Base entry
  (id/name/category/one-liner/trait_tags), and calls the LLM via the same
  tool-calling pattern as Discovery (`CAREER_INTELLIGENCE_TOOL` +
  `tool_choice="required"`).
- **`prompts.py`** carries the same reasoning-discipline posture as
  Discovery: ground every match in real evidence, always populate
  contradicting/missing evidence, set `insufficient_evidence` honestly
  rather than fabricating candidates when Career DNA is too thin, never
  phrase a candidate as "you should become X."
- **`confidence.py`** — the deterministic ceiling described above, plus
  `evidence_strength_label()`.
- **`candidates.py::upsert_candidates()`** — the single place a turn's
  `CareerCandidateUpdate`s become persisted `CareerCandidate`s +
  `EvidenceRecord`s (`related_career`) + `NotebookEntry`s, shared by both
  callers. Mirrors the hypothesis lifecycle: a candidate absent from a
  later analysis is marked `status="discarded"` (kept, not deleted) with
  a `transition_reason`, not silently dropped — this runs even when a
  later analysis returns zero candidates, since a genuinely-empty result
  must still discard previously-active ones rather than leaving them
  stale forever.
- **`domain/services/evidence_recording.py::record_new_evidence()`** — a
  shared Evidence Graph writer used by *both* the Discovery Agent
  (hypothesis evidence) and Career Intelligence (candidate evidence).
  Originally two structurally-identical copies (`_record_new_evidence` in
  `discovery/agent.py` and `_record_career_evidence` in
  `career_intelligence/candidates.py`), unified during the post-Phase-2
  architectural audit — one dedup/append implementation, parameterized by
  which cross-reference field (`related_hypothesis` / `related_career`)
  applies.

### Career Knowledge Base — data, not prompt text

`careers` and `career_stories` are normalized Supabase tables (not
jsonb-per-student blobs) — see "Supabase integration" below for why.
`CareerRepository` (`services/supabase/repositories/career_repository.py`)
is the only place that queries them: `list_careers(filters)`,
`get_career(id)`, `list_stories_for_career(id)`. Career Reality, Future
Lens, and Human Stories are **not** separate agents or reasoning calls —
they're structured fields on a `Career`/`CareerStory` row
(`domain/models/career.py`), surfaced by a plain read API
(`api/v1/careers.py`). Human Stories are authored as illustrative
composite personas (labeled by role/experience, e.g. "Data Scientist, 6
years experience"), not fabricated named real individuals, and are
tagged for relevance to a student's strong (score ≥0.5) Career DNA
traits via simple tag overlap — not embeddings, matching the
"not vector similarity" philosophy.

The current seed (`scripts/seed_careers.py`, run once via
`python -m aureon.scripts.seed_careers`) is a deliberately modest
starting set — 27 careers across all 8 requested categories, 15 stories —
proving the architecture with real breadth, not claiming full
career-universe coverage. The LLM reasons over the *entire* current seed
in one prompt call each analysis (small enough to fit comfortably); if
the Knowledge Base grows well beyond this size, a retrieval/pre-filter
step would be needed before that full-list approach stops scaling — a
known, deliberate limit, not solved prematurely.

### EvidenceSource — used for real now

`ConversationEvidenceSource` and `ReflectionEvidenceSource`
(`agents/specialized/discovery/evidence/`) don't call the LLM
themselves — they read the `DiscoveryTurnOutput` already produced this
turn (from `state["agent_outputs"]["discovery"]`) and format it as
`ExplorationEvent`s. This keeps the registry pattern genuinely pluggable
without each source redundantly re-deriving what the one atomic
reasoning call already produced.

### Shared state (`agents/state.py`)

`AureonState` carries: `why_probe_state: dict[str, int]`,
`pending_reflection_prompt: str | None`, `hop_count: int` — all
turn-scoped or Why-Engine-scoped, reset/managed by `turn_start_node` and
the Discovery Agent respectively. Career Intelligence introduced no new
`AureonState` fields — it reads/writes `state["student_profile"]` (owned
jointly with Discovery, via the profile's own `career_candidates` field)
and writes only its own `state["agent_outputs"]["career_intelligence"]`
entry, per the existing per-agent-output-ownership convention.

## Memory design — long-term student profile

Two persistence tiers:

- **`Conversation`/`Turn`** (session-scoped): the raw transcript, in
  `conversations`/`turns` tables via `ConversationRepository`.
- **`StudentProfile`** (person-scoped, cross-session): interests,
  strengths, values, goals, persona, `confidence_history`,
  `exploration_history`, `career_history`, `learning_progress`,
  `mentor_interactions`, `career_dna: CareerDNA`,
  `career_hypotheses: list[CareerHypothesis]`,
  `reflection_journal: list[ReflectionEntry]`,
  `notebook_entries: list[NotebookEntry]`,
  `evidence_graph: list[EvidenceRecord]`, and (Phase 2)
  `career_candidates: list[CareerCandidate]` — in the `student_profiles`
  table (jsonb columns for the nested structures) via
  `StudentProfileRepository`, keyed by `student_id`.

The Evidence Graph is the single source of truth for evidence: trait,
hypothesis, and career candidate evidence lists are all computed by
filtering `evidence_graph` (by `related_trait` / `related_hypothesis` /
`related_career`) when a DTO is built, never stored redundantly in
multiple places. The Discovery Notebook similarly unifies two logical
entry shapes (`observation`, `belief_revision`) in one `NotebookEntry`
model rather than two parallel systems.

### Cross-turn continuity

The scaffold's `conversation_service.py` originally built a brand-new
`new_state(...)` on *every* turn, which — because most `AureonState`
fields have no LangGraph reducer — silently reset the checkpointer's
persisted state back to defaults each time. **Fixed**: only a brand-new
conversation gets the full `new_state(...)`; a continuing thread sends
just `{"messages": [...], "student_profile": ...}` and lets
`graph.aget_state(config)` supply everything else from the checkpoint
(falling back to a fresh state if no checkpoint is found, e.g. after a
server restart with the in-memory checkpointer).

### Checkpoint serialization

`agents/orchestrator/checkpointer.py`'s `MemorySaver` is configured with
an explicit `JsonPlusSerializer(allowed_msgpack_modules=[...])` allowlist
covering every custom Pydantic model that can appear nested in state:
`StudentProfile`, `CareerDNA`, `TraitSignal`, `CareerHypothesis`,
`ReflectionEntry`, `MentorHandoff`, `AgentOutput`, `NotebookEntry`,
`EvidenceRecord`, `CareerCandidate`, and the profile's history
sub-models. Any new Pydantic model that ends up nested in `AureonState`
must be added here or checkpoint (de)serialization eventually breaks.

## Human-in-the-loop

`domain/models/mentor_handoff.py` models a single handoff. The Mentor
Agent remains a stub this phase but is already wired as not
recommendation-stage, so it's reachable regardless of confidence.

## LLM provider abstraction

`services/llm/base.py`'s `LLMClient` protocol includes `tool_choice`,
letting the planner, Discovery Agent, and Career Intelligence Agent all
force a structured tool-call response rather than parsing free text.
`GroqClient` omits `tools`/`tool_choice` from the request entirely when
not provided rather than passing an explicit `None`, since some backends
reject a literal JSON `null` for these parameters.

## Supabase integration

Repository pattern throughout: `api/deps.py` wires `Annotated[X,
Depends(get_x_repository)]` DI aliases; each repository wraps
`supabase-py`'s sync client in `run_in_threadpool`.

Two distinct storage shapes, chosen deliberately per access pattern:
- **jsonb-per-identity blob** (`student_profiles`): always read/written
  whole as one Pydantic-modeled object, never queried piecemeal by SQL —
  jsonb keeps this simple without premature normalization.
- **Normalized rows** (`conversations`/`turns`, and Phase 2's
  `careers`/`career_stories`): need to be searched, filtered, or joined
  (turns by `conversation_id`; careers by category/industry/country,
  career → stories), so real columns + indexes are the correct shape.
  Rich nested detail that's still read/written whole per row (a career's
  `reality`/`future_lens`) stays jsonb *within* the normalized row —
  normalization and jsonb aren't mutually exclusive, applied at whatever
  granularity actually needs to be queried.

RLS is intentionally off — the backend uses Supabase's secret
(service-role-equivalent) key, which bypasses RLS by design.

**Bug found and fixed during live verification (Phase 1)**:
`maybe_single().execute()` returns `None` outright (not a response
object with `.data = None`) when zero rows match, in the installed
`supabase-py` version. Fixed with an explicit `None` check across all
repositories; regression-tested with a fake Supabase client double that
reproduces the exact chained-builder response shape.

Migrations (hand-authored SQL, run once via the Supabase SQL Editor — no
formal migration tool adopted yet):
- `db/migrations/0001_discovery_module.sql` — `conversations`, `turns`, `student_profiles`.
- `db/migrations/0002_phase1_completion.sql` — additive `notebook_entries`, `evidence_graph` columns.
- `db/migrations/0003_phase2_career_intelligence.sql` — `careers`, `career_stories` tables (+ indexes on `category`/`industry`/`career_id`), additive `career_candidates` column.

## API surface

- `POST /v1/conversation/turn` — request: `student_id`, optional
  `conversation_id`, `message`. Response: `mode`, `active_agent`,
  `confidence_score`, `understanding_stage`, `understanding_narrative`,
  `career_dna`, `hypotheses` (active only), `hidden_potential`,
  `notebook_entries`, `reflection_prompt`, `suggested_activity`.
- `GET /v1/students/{student_id}/discovery-profile` — restores the full
  Discovery Notebook (`career_dna`, `hypotheses`, `hidden_potential`,
  `notebook_entries`, `evidence_graph`, `reflection_journal`,
  `confidence_score`, understanding level) for a returning student
  without replaying the conversation.
- `POST /v1/students/{student_id}/career-candidates/analyze` — the
  primary Career Intelligence trigger; not conversational turn-taking.
  Enforces its own low evidence floor (`MIN_TRAITS_FOR_ANALYSIS = 2`,
  distinct from the 0.6 recommendation-confidence gate) before invoking
  `analyze_careers()`.
- `GET /v1/students/{student_id}/career-candidates` — reads persisted
  candidates only, no LLM call — survives refresh/new device.
- `GET /v1/careers[?category=&industry=&country=&q=]` — Global Career
  Discovery's open browse/search; no evidence gating.
- `GET /v1/careers/{career_id}[?student_id=]` — Career Reality + Future
  Lens + Human Stories for one career; personalizes story ordering when
  `student_id` is given.

## Frontend

`frontend/src/features/discovery/DiscoveryContext.tsx` is the shared
provider for Discovery's conversational state (messages, Career DNA,
hypotheses, notebook entries, hidden potential, understanding level,
confidence, reflection journal) — it fetches the persisted profile on
mount (`GET .../discovery-profile`) and drives turns via
`POST /conversation/turn`. It performs **no client-side diffing or
derivation** — every observation, belief revision, hidden-potential
pattern, and understanding-level label is computed server-side and just
rendered, which is what lets the Discovery Notebook survive a refresh or
a new device. A per-browser `student_id`
(`shared/config/studentId.ts`, `localStorage`-backed) stands in for real
auth, which still doesn't exist.

`features/career-intelligence/CareerIntelligenceContext.tsx` is a
sibling provider (same shape, added alongside `DiscoveryProvider` in
`App.tsx`) for Career Intelligence's candidates + on-demand
`analyzeCareers()` action. Global Career Discovery and Career Details are
stateless reads (`GET /v1/careers`, `GET /v1/careers/{id}`) handled with
local `useEffect` in their own screen components — no context needed for
read-only catalog browsing.

Design system (`design-system/components/`): `Surface` (the core
card/panel primitive — `tone` neutral/raised, `padding` none/sm/md/lg),
`Badge`, `Button`, plus shared `cn()` (clsx + tailwind-merge) and
`motion.ts` tokens (`EASE_CALM`, fade/breathe presets). Palette:
`void`/`surface`/`ink` (background/panel/text), `starlight` (warm amber —
"the discovered self," used for the student's own data) and `signal`
(cool violet — "AI presence," used for Aureon-generated/reasoning
content). Every screen across both phases builds on these same
primitives and color vocabulary rather than introducing new ad-hoc
styling — Phase 2's evidence-first card ordering (Supporting →
Contradicting → Missing → Evidence Strength) intentionally matches
Phase 1's `HypothesisCard` pattern.

Journey Navigation (`features/navigation/journeyConfig.ts`) is the single
source of truth for both the persistent sidebar and route registration —
a module's `locked: boolean` flag drives whether it renders its real
screen or the shared `LockedModule` (which explains *why* a stage isn't
available yet, never "Coming Soon"). Phase 2 unlocked all 3 "Explore
Careers" slots without adding new nav entries: `career-reality` fans into
a browse list + detail pair (Global Career Discovery + Career Details,
with Reality/Human Stories as sections of the same detail screen), and
`future-lens` is an aggregate timeline comparison across the student's
current candidates — deliberately reusing existing IA slots rather than
growing the nav.

Live-verified via headless-Chromium (Playwright) walkthroughs each phase:
real multi-turn conversations and, for Phase 2, a real Groq-backed
analyze call, confirmed against the live backend/Groq/Supabase stack with
zero console errors. No persistent frontend test framework is installed
(no Vitest/RTL) — this is a deliberate, disclosed scope decision, not a
gap being hidden; verification scripts are temporary and removed after
each pass.

## Configuration

`pydantic-settings`-based `Settings` (`core/config.py`) — `environment`,
Supabase credentials, LLM provider/model, `min_recommendation_confidence`,
CORS origins, log level/format. `.env.example` documents every key.

## Logging

`structlog` layered on stdlib logging (`core/logging.py`), configured
once at startup. JSON rendering for staging/production, colored console
for local.

## Deferred / open decisions

| Decision | Current state | Revisit when |
|---|---|---|
| LangGraph checkpointer | `MemorySaver` (in-process, lost on restart); `conversation_id` doubles as the `thread_id` | Persistence-hardening module — swap to `PostgresSaver` pointed at the Supabase connection string |
| Migrations tooling | Hand-authored SQL run manually via Supabase SQL Editor (`db/migrations/0001-0003`); Supabase CLI vs Alembic still undecided | When schema changes become frequent enough to need repeatable tooling |
| Auth | None; `student_id` is a client-generated, unauthenticated `localStorage` value | Before any non-local deployment |
| CI/CD | None (`.github/` not created) | When the team needs automated checks on PRs |
| Career Knowledge Base retrieval | Full seed list (27 careers) fits in one prompt call — no pre-filter/embedding layer | If the Knowledge Base grows well beyond a size that fits comfortably in one prompt |
| Frontend test framework | None (Vitest/RTL not installed); verification uses temporary Playwright scripts, removed after each pass | If regression risk in the frontend grows enough to justify a permanent suite |
| Planner routing eagerness | The planner sometimes hops to a second agent (e.g. Mentor) even when not clearly needed — harmless today since those agents are no-ops, but costs an extra LLM call | When those agents get real logic and eagerness has a real-cost or UX consequence |

## Verification

- Backend: `pytest` (75 tests) — health check, all 8 agents self-register
  with correct `is_recommendation_stage` flags, orchestrator graph
  compiles with every node, confidence gate blocks/allows correctly, LLM
  factory returns the configured adapter, Discovery Agent's full Career
  DNA/hypothesis-lifecycle/evidence-graph/notebook/reflection/why-probe
  logic, Hidden Potential and Understanding Level derivation, Career
  Intelligence Agent's candidate reasoning/confidence-capping/discard
  lifecycle, the shared evidence-recording helper, Career Knowledge Base
  repository and DTO-building logic, planner routing + hop cap,
  `turn_start_node` reset behavior, and conversation-service
  resume-vs-new branching — all via `FakeLLMClient`/fake-Supabase-client
  test doubles, no network calls in the suite.
- Live verification (real Groq + real Supabase), each phase: multi-turn
  Discovery conversations and a Career Intelligence analyze call driven
  both directly against the API (`curl`) and through the actual browser
  UI (headless Chromium), confirming coherent replies, correctly-cited
  Career DNA/evidence updates, evolving hypotheses and career candidates
  with real evidence, confidence bounded by deterministic ceilings, and
  persistence surviving a server restart via Supabase.
