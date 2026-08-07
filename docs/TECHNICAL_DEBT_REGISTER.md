# Aureon Technical Debt Register

**Purpose:** a living record of decisions made intentionally, for good reasons, that could become real problems later if left unexamined. Not a bug list — everything here is currently *correct* for where the product is. This document exists so those decisions stay conscious choices, revisited on purpose, instead of accidents nobody remembers making.

**Origin:** Sprint 1 (Skill entity). Updated at the end of every future sprint that introduces a similar trade-off.

---

## Future Evolution Review — Sprint 1

### 1. `required_skill_ids` stored as a JSON array, not a true relational edge

- **Current implementation:** `careers.required_skill_ids` is a `jsonb` array of skill id strings. No foreign key back to `skills.id`. `Skill.parent_skill_id` *does* have a real FK — only one side of this sprint's relationships is actually enforced by the database.
- **Why it was correct for Sprint 1:** ~27 careers, ~23 skills. A join table for a relationship this size is pure overhead, and it matches an established, documented convention already in this codebase (`Opportunity`/`CareerWorld` deliberately keep small single-purpose lists flat rather than normalized).
- **Future risk:** No referential integrity — nothing stops a future write from pointing at a skill id that doesn't exist. Combined with item 2 below, this is the core of the "isolated string list wearing a graph costume" risk the whole Skill entity was built to move away from — it's better than free text (typed, validated ids) but it isn't the real thing yet.
- **Earliest sprint to revisit:** When Project's own `target_skill_ids` gets built — building a third jsonb-array edge without addressing this compounds the debt threefold instead of once. Realistically Sprint 3-4.
- **Recommended long-term direction:** A real `career_skills(career_id, skill_id)` join table (or a generalized `entity_skill_edges` table if the pattern needs to serve Career/Project/Opportunity/Mentor uniformly), with FKs and indexes on both columns.
- **Classification: Monitor**

### 2. Full-table reverse lookups

- **Current implementation:** `CareerRepository.list_careers_requiring_skill` fetches every career and filters in Python — not a jsonb containment query, not an indexed lookup.
- **Why it was correct:** Identical to the existing `country` filter's own pattern, already precedent in this codebase before this sprint touched anything. Consistency over inventing a one-off query style for a single new field.
- **Future risk:** Cost scales linearly with catalog size, and repeats identically the moment Company, Mentor, or Opportunity each want their own "which X requires this skill" view.
- **Earliest sprint to revisit:** Tied to item 1 — fixing the join table largely fixes this too.
- **Recommended long-term direction:** Once a join table exists, this becomes one indexed `WHERE skill_id = X` query.
- **Classification: Monitor**

### 3. Cross-domain imports (`skill_view.py` imports `Career`)

- **Current implementation:** `domain/services/skill_view.py` imports `aureon.domain.models.career.Career` directly.
- **Why it was correct:** The relationship is genuinely cross-domain — Skill really does relate to Career. Building an abstraction to avoid one honest, real dependency would be premature.
- **Future risk:** If every future entity pair repeats this un-reflectively (Skill↔Company, Skill↔Project, Company↔Career, ...), `domain/services/` risks becoming a dense web of cross-imports with no clear ownership convention, right as the graph's real density grows to match the architecture doc's own "every entity connects to ≥3 others" goal.
- **Earliest sprint to revisit:** Once 3+ entities cross-reference each other bidirectionally — realistically once both Company and Project exist alongside Skill.
- **Recommended long-term direction:** Codify what's already happening as an explicit rule (e.g. "composition happens in `*_view.py` files only, repositories never cross-import models") rather than leaving it an emergent, unstated pattern.
- **Classification: Monitor**

### 4. Route dependency growth

- **Current implementation:** the Career detail route now depends on four repositories (Career, StudentProfile, Trend, Skill).
- **Why it was correct:** Each dependency was added incrementally and justified on its own merits across separate batches, including this one — no single addition was ever wrong.
- **Future risk:** The architecture doc's own Career UI spec eventually wants Companies, Projects, Opportunities, and Mentors resolved on the same page — this route could reach 8+ sequential dependencies, becoming slow (sequential awaits where lookups could parallelize) and hard to unit test.
- **Earliest sprint to revisit:** When the route crosses roughly 6 repository dependencies — worth a proactive check rather than waiting until it's unmanageable.
- **Recommended long-term direction:** Extract a `CareerDetailComposer` owning the sub-repositories with one clean method exposed to the route; use `asyncio.gather` for independent lookups.
- **Classification: Monitor**

### 5. Alias matching strategy (exact string match only)

- **Current implementation:** `REQUIRED_SKILL_ALIASES` is a plain `dict[str, str]`, built from the exact 88 real strings already in the 27 seeded careers.
- **Why it was correct:** Exhaustive and 100% correct against data that genuinely exists today. Fuzzy matching would solve a problem with no current evidence it exists.
- **Future risk:** Every future career seed needs a human to remember to extend the alias map, or new phrasing variants silently go unlinked — no error, no test failure, just quietly thinner data over time.
- **Earliest sprint to revisit:** The next sprint that adds new Career seed content — could be as early as Sprint 2.
- **Recommended long-term direction:** At minimum, a loud (not silent) seed-time or CI report of unmatched strings. A real fuzzy/normalization pass only if the catalog grows enough to make manual alias upkeep genuinely impractical.
- **Classification: Monitor**

### 6. Data migration strategy (manual, hand-applied SQL)

- **Current implementation:** numbered, forward-only SQL files, applied by hand via the Supabase Dashboard SQL Editor — the same workaround used for every migration this session, because this development machine has no direct Postgres route.
- **Why it was correct:** Matches 26 prior migrations in this exact codebase. Building real migration tooling was never in scope for any sprint, including this one.
- **Future risk:** This is the one item in this whole review that's genuinely not fine for a real product. Manual SQL pasting doesn't survive multiple environments, multiple engineers, or any real release cadence.
- **Earliest sprint to revisit:** Before any real production launch — maps directly to the architecture doc's own Phase 9 (Production Readiness).
- **Recommended long-term direction:** A GitHub Actions step that applies pending migrations automatically on merge to `main`, using a Postgres connection Actions' runners can actually reach (the network limitation is specific to this local machine, not a real infrastructure constraint — the frontend deploy workflow already proves CI automation works in this repo).
- **Classification: Must Change Before Production**

### 7. Scaling characteristics (small-catalog assumptions)

- **Current implementation:** Every design choice this sprint leans on "the catalog is small" (~23-27 rows).
- **Why it was correct:** Verifiably true today.
- **Future risk:** A real-product-track Aureon needs these catalogs to grow substantially to be genuinely useful — every "fine because it's small" decision compounds together, not independently, the moment that happens.
- **Earliest sprint to revisit:** Whenever catalog growth becomes a stated product goal — treat "any entity crossing ~200 rows" as the trigger to revisit every small-scale assumption in one pass, not reactively one entity at a time.
- **Recommended long-term direction:** A single, deliberate scaling review across all catalog entities together, not per-entity firefighting.
- **Classification: Monitor**

### 8. Query patterns (fetch-all-then-filter)

- **Current implementation:** Not unique to Skill — `list_careers`, `list_trends` already do this; Sprint 1 extended the existing pattern rather than introducing a new one.
- **Why it was correct:** Matches 100% of existing precedent. A different query style for just the new Skill code would itself be an inconsistency.
- **Future risk:** Identical to items 1/2/7 — compounds at scale.
- **Earliest sprint to revisit:** Same trigger as item 7.
- **Recommended long-term direction:** A codebase-wide pass converting fetch-all-filter to real indexed queries uniformly, once triggered — not entity-by-entity.
- **Classification: Monitor**

### 9. Testing gaps (backfill script's core logic)

- **Current implementation:** `backfill_career_skill_edges.py`'s alias-resolution logic has zero unit tests — only confirmed to import cleanly.
- **Why it was (mostly) correct:** The script cannot run against live data yet regardless (table doesn't exist), and effort this sprint was better spent on the layers that could be fully verified.
- **Future risk:** A future edit to this script's matching/deduping logic has nothing to catch a silent regression.
- **Earliest sprint to revisit:** The next time this file is touched for any reason.
- **Recommended long-term direction:** Extract the pure resolution logic and unit test it directly — no database required, this is a genuine, low-cost gap to close.
- **Classification: Monitor**

### 10. Future maintainability (pattern duplication risk)

- **Current implementation:** Skill's repository/service/route stack closely mirrors Trend's — the only real precedent to follow, so consistency was easy and correct.
- **Why it was correct:** One clear precedent, faithfully followed.
- **Future risk:** Once Company and Project exist as near-identical third and fourth copies of the same shape, the question changes from "is this consistent with the one precedent" to "should this be a shared generic base instead of four copies of the same pattern" — copy-paste consistency is good until it becomes its own debt (a shape change later means N edits instead of one).
- **Earliest sprint to revisit:** After both Company and Project exist — two data points (Trend, Skill) aren't enough to safely generalize from; premature abstraction is its own risk.
- **Recommended long-term direction:** A deliberate, retrospective evaluation of a shared `CatalogRepository`/`CatalogView` base, only once there's real evidence of the pattern repeating 3+ times.
- **Classification: Monitor**

---

## What We Deliberately Chose Not to Optimize

Every one of these was a conscious trade-off, not an oversight — documented here so it reads that way to whoever looks at this code next.

**JSON arrays instead of join tables.** Avoided a new table, a new migration, and a new query pattern for a relationship touching ~50 total rows. Revisit when a third entity needs its own many-to-many edge into Skill (see item 1).

**Exact alias matching instead of fuzzy matching.** Avoided building matching infrastructure for a problem with zero current evidence — every real string in today's data matches exactly. Revisit the moment new Career content is seeded without a corresponding alias update (see item 5).

**Existing repository/service/route patterns instead of a new generic abstraction.** Avoided guessing at a shared shape from a single precedent. Revisit once Company and Project both exist and the pattern has genuinely repeated three or four times, not before (see item 10).

**Cosmetic UI seam left unresolved** — `RealitySection`'s old plain-text skill list and the new clickable `CareerSkillsSection` both render on a backfilled career's page. Avoided touching a file outside this sprint's explicit scope for a purely cosmetic overlap. Revisit whenever `RealitySection` is next touched for any other reason, or once backfill coverage is broad enough that the plain-text fallback is rarely the only thing showing.

**No FK enforcement on `required_skill_ids`, trusted to application-level discipline instead.** Avoided a database constraint that a jsonb array can't cleanly express without a trigger. Safe today because the backfill script is the only writer and it only ever writes real matched ids. Revisit alongside item 1's join-table work, which would make this enforcement free.

**No repository-level unit test suite with a mocked Supabase client.** Avoided introducing a new testing layer that doesn't exist anywhere else in this codebase — every other repository is proven correct via route-level fake-repo tests instead, and Skill followed that same convention rather than becoming the first exception.

**`evidence_types_that_count` left as free-text strings, not a structured taxonomy.** Avoided building a skill-evidence scoring system that Sprint 1 explicitly excluded from scope. Revisit only if a future sprint genuinely needs to compute skill proficiency from evidence, not before.

**No cap on "careers requiring this skill" list rendering.** Avoided building pagination for a list that's currently at most a handful of items. Revisit if any single skill's requiring-career count grows past what's comfortable to render flat (a dozen or so).

---

## Technical Debt Register

Prioritized, not chronological — read top to bottom as "what to think about first," not "what was found first."

| # | Item | Priority | Product Impact | Engineering Impact | Suggested Sprint | Estimated Difficulty |
|---|---|---|---|---|---|---|
| 1 | Manual, hand-applied SQL migrations — no CI-driven schema deploys | **High** (for production; Low for hackathon) | None directly, but blocks reliable, repeatable releases | High — every future migration depends on a human pasting SQL correctly | Before any real production launch (Phase 9) | Low-Medium (a GitHub Actions step; the frontend deploy workflow already proves this repo can automate this way) |
| 2 | No real relational edges for Skill↔Career (JSON array, no FK, full-scan reverse lookup) | Medium (High once Project/Company add their own edges) | Low today; becomes real (slow pages, silently missing links) as the catalog grows | Medium — touches repository, migration, and DTO layers when fixed | When Project's skill edges are built (~Sprint 3-4) | Medium (one join table + FKs + indexed queries; no UI change needed) |
| 3 | Alias matching is exact-string only, silent on mismatch | Medium | Silently thinner skill-linking data over time — no crash, a quiet quality regression | Low to detect (a report), Medium to fully solve (fuzzy matching) | Next sprint adding Career seed content (~Sprint 2) | Low for detection; Medium for a full fix |
| 4 | Career detail route's growing repository dependency list | Low today, Medium by Sprint 3 | None directly — a performance/readability concern, not a correctness one | Medium — route becomes harder to test and reason about as it grows | When the route reaches ~6 dependencies | Medium (extracting a composer service is a real refactor) |
| 5 | Backfill script has no unit test coverage of its core logic | Low-Medium | None directly | Medium — a silent regression risk the next time the file is touched | Next time this file is touched | Low (pure function, easy to isolate) |
| 6 | No generic base pattern across near-identical catalog entities | Low | None | Low today, Medium if left unaddressed past 3+ entities | After Company and Project both exist | Medium (risk of over-abstracting if done too early) |
| 7 | `RealitySection` / `CareerSkillsSection` cosmetic overlap on backfilled careers | Low | Minor visual redundancy, not a functional bug | Low | Whenever `RealitySection` is next touched for any reason | Low |
| 8 | `tool` skill category thin (2 entries); general catalog depth | Low | Minor — one category feels sparse if browsed directly | None (pure content work) | Opportunistic, alongside any future Skill content pass | Low |

---

*This register is meant to be extended, not replaced — the next sprint that introduces a similar trade-off should add to this document, not start a new one.*

---

## Decision Log

> **Rule:** a decision should only be added here if a future engineer is likely to ask *"Why was this done this way?"* This is not another debt register. The Technical Debt Register above records what we intentionally deferred. This log records why we chose the path we chose — the reasoning, not the code.

### Skill introduced before Company and Project

- **Decision:** Build Skill first among the three missing entities, not Company, not Project, not partial versions of all three at once.
- **Context:** The architecture doc identified Skill, Company, and Project as missing simultaneously. Only one workstream could move at a time.
- **Alternatives considered:** Company first (simpler data, real logos, a quicker visual win); Project first (the most novel capability and the strongest hackathon "wow"); thin parallel slices of all three.
- **Why this decision won:** Company and Project's own data models reference Skill (`target_skill_ids` on Project, skill-matching on future Company work) — building either first would mean building against a moving target. Matches the tracker's own explicit formula: highest value, lowest risk, strongest foundation for what comes next.
- **Consequences:** Company and Project should be faster and safer to build now that the promotion pattern is proven once. The most demoable new capability (Project) is deliberately delayed rather than rushed.
- **Revisit trigger:** None — a one-time sequencing decision, already executed.

### Additive migrations instead of destructive schema changes

- **Decision:** Every schema change adds; nothing existing is altered or dropped, even where a field now looks redundant (`reality.required_skills` stays, unedited, alongside the new `required_skill_ids`).
- **Context:** Mirrors the exact discipline the Passion Incubator cleanup migration already established earlier this codebase's history (rename in place, never drop-and-recreate) — this wasn't a new rule invented for Skill.
- **Alternatives considered:** Replace `reality.required_skills` outright for a cleaner end state; a "deprecate now, remove later" halfway step.
- **Why this decision won:** A destructive change to a live field can't be safely verified from this environment — there's no fast, reliable way to audit every real consumer before deleting something. Additive-only removes that entire risk category for a single sprint's work.
- **Consequences:** Two fields now describe overlapping information until a deliberate, separate future migration retires the old one — an intentional, temporary duplication, not an oversight (see Technical Debt Register #7 for the resulting cosmetic UI seam).
- **Revisit trigger:** Once backfill coverage is comprehensive across the whole Career catalog, a dedicated cleanup migration can retire `reality.required_skills`, the same way migration 0024 retired Passion Incubator's tables.

### JSON arrays chosen over join tables

- **Decision:** `required_skill_ids` is a `jsonb` array on `careers`, not a `career_skills` join table.
- **Context:** At the point this was decided, the real relationship spanned ~27 careers and 23 skills — small and fully known.
- **Alternatives considered:** A proper many-to-many join table with FKs on both sides; an edge stored only on the Skill side instead of Career's.
- **Why this decision won:** This is the identical "don't over-normalize a small, single-purpose list" call this codebase already makes for Opportunity, CareerWorld, and TopicResourceDomain at similar scale — following it kept Skill consistent with its neighbors instead of introducing a one-off relational pattern for a single field.
- **Consequences:** No database-level referential integrity on this edge; the reverse lookup costs a full table scan instead of an indexed query (both tracked in the Technical Debt Register).
- **Revisit trigger:** When a third entity — most likely Project — needs its own many-to-many edge into Skill. Building a third array-based edge independently would compound this debt threefold instead of resolving it once.

### Exact alias matching instead of fuzzy matching

- **Decision:** `REQUIRED_SKILL_ALIASES` is a plain exact-string dictionary, not a fuzzy or normalized matcher.
- **Context:** All 88 real `required_skills` strings already sitting in the 27 seeded careers were fully known and enumerable before any matching code was written.
- **Alternatives considered:** Case/whitespace-insensitive normalization; a similarity-threshold fuzzy matcher; an LLM-based classifier mapping free text to canonical skills.
- **Why this decision won:** Every one of the 88 real strings was hand-verified against real data — fuzzy matching would have solved a problem with no evidence it exists, at the cost of introducing non-determinism into a step whose entire point is trustworthy, auditable linking. This follows the same evidence-honesty discipline running through the rest of the product: don't add inference where a real, exact answer is already available.
- **Consequences:** 100% correct against today's data; will silently under-link any future career whose skill text doesn't exactly match an existing alias.
- **Revisit trigger:** The first time a real seed script adds Career content without a matching alias-map update — at that point, a loud mismatch report is worth building before a fuzzy matcher is.

### Existing repository pattern reused instead of creating a generic abstraction

- **Decision:** `SkillRepository` / `skill_view.py` / `api/v1/skills.py` directly copy `TrendRepository`'s exact shape, rather than extracting a shared generic catalog base first.
- **Context:** At the point Skill was built, exactly one prior precedent existed for "a small, read-only, filterable knowledge-base catalog" (Trend) — Career is close but meaningfully richer, not the same shape.
- **Alternatives considered:** Design a generic `CatalogRepository`/DTO-builder abstraction up front, anticipating Company and Project would need it too.
- **Why this decision won:** One real precedent isn't enough evidence to safely generalize from. An abstraction designed from a single example tends to guess wrong about what's genuinely shared versus coincidental, and would likely need reshaping anyway once more real examples exist. Copying a proven pattern was lower-risk than guessing at a shared one.
- **Consequences:** Three or four near-identical repository/service/route stacks will exist side by side once Company and Project are built, each maintained independently until a real abstraction is deliberately extracted.
- **Revisit trigger:** Once Company and Project both exist alongside Skill and Trend — four real data points is enough to identify what's actually shared versus what only looked shared.

### Sprint completion required a real manual walkthrough before being considered done

- **Decision:** Sprint 1 isn't marked complete until a live walkthrough against real, seeded, backfilled data actually passes — a green test suite and a clean build were treated as necessary, not sufficient.
- **Context:** All backend code, tests, and the frontend build were fully verified in isolation before the required migrations had even reached the live database, due to this environment's direct-Postgres limitation.
- **Alternatives considered:** Treat 773 passing tests plus a clean build as sufficient evidence to close the sprint, since every individual piece was independently verified.
- **Why this decision won:** Isolated verification proves each piece is internally correct — it doesn't prove the pieces are correctly wired together against real data. Applying a looser completion standard to the engineering process than the product itself demands of its own evidence claims would be inconsistent with the whole project's honesty discipline.
- **Consequences:** Sprint 1's formal completion is gated on a manual step (applying two SQL migrations) outside engineering's direct control in this environment.
- **Revisit trigger:** If a CI-driven migration pipeline is ever built (Technical Debt Register #1), this gate becomes automatic. The underlying principle — real verification required before "done" — should never be relaxed, regardless.

### Architecture frozen before implementation began

- **Decision:** `AUREON_DATA_ARCHITECTURE.md` was explicitly declared frozen before any Sprint 1 code was written; the tracker and sprint plans were built as separate documents that reference it rather than extend it.
- **Context:** The architecture doc went through several genuine rounds of deepening (entities → principles/governance → roadmap → definition of excellence) before implementation started.
- **Alternatives considered:** Keep evolving the architecture doc informally alongside implementation, updating it as Sprint 1 revealed new information; skip a formal freeze and start building once the model felt "good enough."
- **Why this decision won:** A design document that keeps moving while code is being written against it stops being a reliable reference — nobody can be sure whether it reflects the current plan or an earlier draft. Freezing it forced a clean separation: the architecture answers "what and why," execution documents answer "how is it actually going," and only the execution layer is expected to change week to week.
- **Consequences:** Real discoveries made during implementation (like the JSON-array/FK trade-offs this sprint) don't get folded back into the frozen doc — they're deliberately logged here or in the Technical Debt Register instead, which is more process overhead but keeps the architecture trustworthy as a fixed reference point.
- **Revisit trigger:** Only if implementation reveals the architecture itself was fundamentally wrong, not merely incomplete — per the sprint execution rule already in place: stop, explain, propose the smallest fix, and wait for approval before proceeding.
