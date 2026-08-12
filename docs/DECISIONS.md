# Aureon — Decisions

A curated record of the engineering and product decisions most likely to
prompt "why was this built this way?" — not a complete change log. The
full, granular decision history (every entity-promotion trade-off, every
migration choice) lives in
[`TECHNICAL_DEBT_REGISTER.md`](./TECHNICAL_DEBT_REGISTER.md); this
document is the judge-facing subset.

---

### Why agentic orchestration, not a single chatbot wrapper

**Decision:** Route every conversational turn through a real LangGraph
`StateGraph` with a live agent registry, rather than one general-purpose
system prompt handling every kind of request.

**Why:** A single prompt asked to be a career counselor, a decision
analyst, and a mentor-matcher at once either produces generic answers or
becomes an unmaintainable prompt. Specialized agents let each domain
(Discovery's evidence-gathering discipline, Career Intelligence's
evidence-grounding rules, Decision's comparison logic) carry its own
prompt, its own tool schema, and its own tests — and the planner routes
between them per turn based on what's actually needed, not a fixed script.

**Consequence:** 12 real, independently-registered agents exist today, 7
of them genuinely LLM-reasoning-live — see
[`AGENTIC_ARCHITECTURE.md`](./AGENTIC_ARCHITECTURE.md) for the honest
breakdown of which.

---

### Why the guided journey is separate from the Knowledge Base

**Decision:** Discover/Explore/Connect/Decide are evidence-gated and
personalized; Skills/Companies/Projects live in their own, always-open
"Knowledge Base" navigation group with no gating at all.

**Why:** These answer structurally different questions. The four guided
stages each answer "what fits *me*" — a personalized progression that
makes sense to gate on accumulated evidence. The Knowledge Base answers
"what exists" — a plain reference question a student should be able to
ask at any time, onboarded or not. Folding Skills/Companies/Projects into
Explore would have misrepresented them as part of the personalized
progression when they're not.

---

### Why Project evidence requires genuine engagement, and Career quiz
### recommendations don't count as evidence

**Decision:** Completing a Project writes real evidence only if the
student submitted a real artifact URL or a genuine reflection — an empty
completion is honestly recorded as an attempt, but contributes nothing to
the Evidence Graph.

**Why:** "The student clicked a button" is not evidence of capability.
Treating bare completion as a skill signal would have been exactly the
kind of unearned certainty the whole product exists to refuse — the same
principle that keeps a career "candidate" from ever being shown as a
flat recommendation without cited supporting/contradicting evidence.

---

### Why confidence is bounded in code, not just requested in a prompt

**Decision:** A deterministic ceiling (`min(llm_suggested, deterministic_ceiling(evidence_count))`)
caps how confident the Discovery Agent and Career Intelligence Agent can
report, growing only as real evidence accumulates — and a separate,
non-LLM `confidence_gate` blocks the orchestrator from ever routing to a
recommendation-stage agent while confidence is too low, regardless of
what the planner LLM decides.

**Why:** An LLM instructed "don't recommend prematurely" can still be
talked into it by a persistent or ambiguous conversation. A structural,
code-level ceiling can't be prompted around — it's the single clearest
expression of "recommendations follow evidence, never the reverse."

---

### Why fabricated external references were removed rather than left in place

**Decision:** A dedicated audit found and removed 46 fake
`example.com`/`.org` placeholder URLs across Opportunities and Mentors,
loosened `Opportunity.official_link` to optional rather than pointing it
at a fake destination, and added a permanent regression test scanning all
seed sources for the same class of mistake.

**Why:** A link to nowhere is worse than no link — it looks like
verification the product never actually did. Once real destinations
aren't available, the honest choice is visibly absent, not a link that
just happens to 404.

---

### Why honest empty/error states are preferred over generic "no data" screens

**Decision:** Loading, success, genuine-empty, and error are always
tracked as distinct states — never collapsed into one silent `.catch(() =>
[])` that renders identically to "there's genuinely nothing here."

**Why:** A real, live bug was caught by this discipline directly: a
missing database migration caused a fully-seeded feature (Student
Stories) to 500 on every request — and an earlier, looser error-handling
pattern was silently converting that failure into an honest-*looking*
"No Stories Found" empty state. A student (or a judge) has no way to tell
"nothing exists yet" from "something is broken" unless the product itself
makes that distinction explicit.

---

### Why deferred/lazy data loading was introduced

**Decision:** Only a small set of "immediate" providers (the ones Mission
Control's first paint actually needs) fetch at app mount; per-investigation-
type collections and other secondary data load lazily, once, on first
access to the screen that actually needs them.

**Why:** Fetching everything at mount meant the first paint waited on data
most sessions never touched. Splitting "needed immediately" from "needed
eventually" cuts real, measurable initial request volume without changing
what any screen ultimately shows once visited.

---

### Why some onboarding fields remain internal rather than being exposed as editable profile fields

**Decision:** Age, location, and preferred language — all collected
during onboarding — are not exposed anywhere as editable Profile fields,
even though the underlying architecture could technically support adding
them.

**Why:** A direct audit found these three fields have **zero consumers**
anywhere in the codebase today — not in personalization, not in any
agent's reasoning, not surfaced back through any existing API read path.
Making them editable would mean building new backend read/write surface
for fields nothing currently uses — exactly the kind of unjustified
scope the product's own principle warns against: *"smaller, truthful data
flow is better than adding fields merely because they exist."* `stage`
and `current_situation`, by contrast, genuinely are consumed (feeding
`academic_level`-based opportunity scoring and uncertainty-signal
detection respectively) and were left exactly as they are — internal,
write-once inputs to real reasoning, not user-facing editable state.

---

### Why the name-continuity fix reused an existing mechanism instead of adding a second name store

**Decision:** When onboarding's `name` field was found not to sync into
the Supabase `user_metadata.name` value Profile and Mission Control both
actually display, the fix was one line — passing `name` through the
already-existing `completeOnboarding()`/`updateUser()` call — not a new
backend field or a second source of truth for "the student's name."

**Why:** The backend's own `discovery_onboarding.name` field is never
read by anything (frontend or backend) — it's a write-only snapshot.
Building a second, reconciled name representation would have solved a
problem that a one-line reuse of the existing, already-correct mechanism
already solved.

---

### Why Passion Incubator was retired rather than kept as a fourth Discover module

**Decision:** Passion Incubator (a curiosity-lifecycle classifier) was
removed from the product; the surviving parts of its stack that other
features genuinely depended on (a shared topic/interest-signal engine used
by Decision Lab, a shared resource catalog used by Knowledge Circles) were
renamed and kept, not deleted, via an additive database migration
(`0024_remove_passion_incubator.sql`) that preserved every real row.

**Why:** Aureon already understands evolving student interest through
Career DNA, World Signals, the Evidence Graph, and Reflection Memory — a
standalone feature that only relabeled that same signal into lifecycle
buckets ("curious," "reinforced," ...) was redundant overlap, not a
distinct capability. Removing it required a real dependency audit first
(two other features had live, load-bearing dependencies on parts of its
stack) — the migration renamed rather than dropped, preserving 22 seeded
resource rows and every real Knowledge Circle link with zero data loss.

---

### Why manual SQL migrations instead of a migration tool, for now

**Decision:** All 31 schema changes are hand-authored, forward-only SQL
files, applied by hand via the Supabase Dashboard SQL Editor.

**Why:** No CI/CD pipeline with direct Postgres access exists in this
development environment yet. This is explicitly flagged as the one item
in the Technical Debt Register classified "Must Change Before
Production" — not presented as a solved problem, and not a decision
expected to hold indefinitely.
