# Aureon Technical Debt Register

**Purpose:** a living record of decisions made intentionally, for good reasons, that could become real problems later if left unexamined. Not a bug list — everything here is currently *correct* for where the product is. This document exists so those decisions stay conscious choices, revisited on purpose, instead of accidents nobody remembers making.

**Origin:** Sprint 1 (Skill entity). Updated at the end of every future sprint that introduces a similar trade-off.

---

## Future Evolution Review — Sprint 1

### 1. `required_skill_ids` stored as a JSON array, not a true relational edge

- **Current implementation:** `careers.required_skill_ids` is a `jsonb` array of skill id strings. No foreign key back to `skills.id`. `Skill.parent_skill_id` *does* have a real FK — only one side of this sprint's relationships is actually enforced by the database. **Sprint 3 update:** `projects.target_skill_ids`/`related_career_ids`/`related_company_ids` are the same shape — a third (and fourth, and fifth) unenforced jsonb edge, now pointing outward from Project instead of inward to it.
- **Why it was correct for Sprint 1:** ~27 careers, ~23 skills. A join table for a relationship this size is pure overhead, and it matches an established, documented convention already in this codebase (`Opportunity`/`CareerWorld` deliberately keep small single-purpose lists flat rather than normalized). Sprint 3 extended the same reasoning to a ~20-row Project catalog.
- **Future risk:** No referential integrity — nothing stops a future write from pointing at a skill id that doesn't exist. Combined with item 2 below, this is the core of the "isolated string list wearing a graph costume" risk the whole Skill entity was built to move away from — it's better than free text (typed, validated ids) but it isn't the real thing yet. Now three entities (Career, Company, Project) each carry unenforced edges.
- **Earliest sprint to revisit:** Now that Project's own edges exist too, this is the natural trigger the original note anticipated — worth a real look in Sprint 4, before a fourth entity compounds it again.
- **Recommended long-term direction:** A real `career_skills(career_id, skill_id)` join table (or a generalized `entity_skill_edges` table if the pattern needs to serve Career/Project/Opportunity/Mentor uniformly), with FKs and indexes on both columns.
- **Classification: Monitor**

### 2. Full-table reverse lookups

- **Current implementation:** `CareerRepository.list_careers_requiring_skill` fetches every career and filters in Python — not a jsonb containment query, not an indexed lookup. **Sprint 3 update:** `ProjectRepository.list_projects_for_career` does the identical thing in the reverse direction — fetches every project and filters in Python for `career_id in related_career_ids`.
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

- **Current implementation:** the Career detail route now depends on six repositories (Career, StudentProfile, Trend, Skill, Company, Project) — up from four at Sprint 1, five at Sprint 2.
- **Why it was correct:** Each dependency was added incrementally and justified on its own merits across separate batches, including this one — no single addition was ever wrong.
- **Future risk:** The architecture doc's own Career UI spec eventually wants Companies, Projects, Opportunities, and Mentors resolved on the same page — this route could reach 8+ sequential dependencies, becoming slow (sequential awaits where lookups could parallelize) and hard to unit test.
- **Earliest sprint to revisit:** **This threshold is now crossed** (6 dependencies, exactly the trigger this item named) — worth a proactive check at the start of Sprint 4, before a seventh makes the route genuinely unwieldy.
- **Recommended long-term direction:** Extract a `CareerDetailComposer` owning the sub-repositories with one clean method exposed to the route; use `asyncio.gather` for independent lookups.
- **Classification: Monitor → worth prioritizing next sprint**

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

- **Current implementation:** Skill's repository/service/route stack closely mirrors Trend's; Company and now Project both copy the same shape a third and fourth time.
- **Why it was correct:** One clear precedent, faithfully followed each time, including Project's completion-route addition (itself copied from the already-proven `career_experiments.py` shape).
- **Future risk:** **The trigger condition below is now met.** Four near-identical repository/service/route stacks (Trend, Skill, Company, Project) exist side by side — the question genuinely changes from "is this consistent" to "should this be a shared generic base."
- **Earliest sprint to revisit:** Now — four real data points (Trend, Skill, Company, Project) is enough to identify what's actually shared versus what only looked shared. Worth a deliberate look before a fifth entity makes the case even stronger without anyone acting on it.
- **Recommended long-term direction:** A deliberate, retrospective evaluation of a shared `CatalogRepository`/`CatalogView` base, extracting what's genuinely identical across all four (list/get/list_by_ids, DTO composition) while leaving entity-specific filters as-is.
- **Classification: Monitor → ready to act on**

### 11. `student_profiles`' column-per-field storage is invisible to unit tests, and has now caused the same class of bug twice

- **Current implementation:** `StudentProfileRepository.save()` does `client.table("student_profiles").upsert(profile.model_dump(mode="json"))` — every top-level `StudentProfile` field must have a matching real column, not a single jsonb blob column. Every backend unit test uses `FakeStudentProfileRepository` (an in-memory dict), which has no schema at all, so nothing in the test suite can ever catch a missing column.
- **Why it happened again:** `StudentProfile.project_attempts` was added to the Python model in this sprint; the matching `alter table student_profiles add column ... project_attempts` migration was not written until the live-verification walkthrough failed with a real PostgREST schema-cache error. This is the exact same gap `0019_student_profiles_circle_resource_progress.sql` fixed once before, for the exact same reason, in an earlier sprint — meaning the lesson from the first occurrence didn't generalize into a process change, only a one-time fix.
- **Future risk:** Every future additive field on `StudentProfile` (and only `StudentProfile` — this table's storage shape is unique in this codebase) risks the same failure, discovered only at live-verification time rather than at code-review or test time. Two occurrences is a pattern, not a coincidence.
- **Earliest sprint to revisit:** Before the next sprint that adds any new field to `StudentProfile`.
- **Recommended long-term direction:** A cheap, real guard: a small script or test that connects to the live schema (or a startup assertion) and diffs `StudentProfile.model_fields.keys()` against `student_profiles`' real columns, failing loudly if any Python field has no matching column. Doesn't require new tooling, just a script mirroring what `seed_*.py`'s live-data cross-checks already do for id references.
- **Classification: Monitor — but this is the second occurrence, so treat the next as preventable, not surprising**

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

**Real company logos via the Clearbit API, with a designed fallback, deployed without visually confirming the real-logo path in this specific environment.** Sprint 2's Kickoff Review flagged the external-dependency risk in advance and designed the initials-fallback for exactly this reason — which turned out to be the right call, since this development sandbox cannot resolve external DNS for arbitrary hosts at all, and every logo fell back correctly with zero broken images. Avoided treating "the fallback might be needed" as a reason not to ship real logos at all. Revisit trigger: the first deploy to an environment with normal internet access should include a five-minute manual check that real logos actually render there, since that's never been directly observed, only inferred from correct URLs and a correctly-working fallback.

**No skill-evidence-tier display consuming Project's new `related_skill` evidence, even though the data now exists.** Sprint 3 explicitly built the data (real `EvidenceRecord`s tagged by skill) without building a UI to visualize "how much evidence exists for this skill" — a real, natural next feature, deliberately deferred rather than built reactively mid-sprint once the data made it tempting. Revisit once Skill's detail page is next touched for any reason, or when a future sprint wants a genuine reason to revisit Skill's UI.

**No backfill/alias script for Project, unlike Skill and Company.** Not an oversight — Project's edges are seeded directly as real ids on the Project rows themselves (`target_skill_ids`, `related_career_ids`, `related_company_ids`), since Project is a new entity carrying its own outgoing edges rather than a promotion of an existing Career field. There was never a free-text field to alias-match against. See the Decision Log entry below for the full reasoning.

---

## Technical Debt Register

Prioritized, not chronological — read top to bottom as "what to think about first," not "what was found first."

| # | Item | Priority | Product Impact | Engineering Impact | Suggested Sprint | Estimated Difficulty |
|---|---|---|---|---|---|---|
| 1 | Manual, hand-applied SQL migrations — no CI-driven schema deploys | **High** (for production; Low for hackathon) | None directly, but blocks reliable, repeatable releases | High — every future migration depends on a human pasting SQL correctly | Before any real production launch (Phase 9) | Low-Medium (a GitHub Actions step; the frontend deploy workflow already proves this repo can automate this way) |
| 11 | `student_profiles`' column-per-field shape is invisible to unit tests — second real occurrence this project | **Medium-High** (has now caused two live failures) | None if caught before deploy (both times were); real risk of a broken signup/save flow if it ever reaches production undetected | Low to build the guard, but recurring cost every sprint until built | Before the next sprint that adds any `StudentProfile` field | Low (a schema-diff script, no new tooling) |
| 2 | No real relational edges for Skill/Company/Project↔Career (JSON arrays, no FKs, full-scan reverse lookups) | Medium | Low today; becomes real (slow pages, silently missing links) as the catalog grows | Medium — touches repository, migration, and DTO layers when fixed, now for three entities | Sprint 4 — the "third entity" trigger this item named is now met | Medium (one shared join-table pattern + FKs + indexed queries would fix all three at once; no UI change needed) |
| 3 | Alias matching is exact-string only, silent on mismatch | Medium | Silently thinner skill/company-linking data over time — no crash, a quiet quality regression | Low to detect (a report), Medium to fully solve (fuzzy matching) | Next sprint adding Career seed content | Low for detection; Medium for a full fix |
| 4 | Career detail route's growing repository dependency list (now 6, up from 5 after Sprint 2) | **Medium** (threshold now crossed) | None directly — a performance/readability concern, not a correctness one | Medium — route becomes harder to test and reason about as it grows | Sprint 4 — worth a proactive check now that 6 dependencies is reached | Medium (extracting a composer service is a real refactor) |
| 6 | No generic base pattern across near-identical catalog entities (Trend, Skill, Company, Project now share the same shape — four copies) | **Medium** (four data points now exist) | None | Low today, Medium if left unaddressed as a fifth entity arrives | Sprint 4 — four real data points is enough to safely generalize from | Medium (extracting the genuinely shared list/get/list_by_ids/DTO shape) |
| 5 | Backfill/seed scripts have no unit test coverage of their core resolution logic (Skill, Company, and Project's cross-reference validation) | Low-Medium | None directly | Medium — a silent regression risk the next time any of these files is touched | Next time any of these files is touched | Low (pure functions, easy to isolate) |
| 7 | `RealitySection`/`CareerSkillsSection`, `CareerResourcesSection`/`CareerCompaniesSection`, and now the plain-text `projects` list/`CareerProjectsSection` cosmetic overlaps on backfilled careers | Low | Minor visual redundancy, not a functional bug | Low | Whenever any of the old sections is next touched for any reason | Low |
| 8 | `tool` skill category thin (2 entries); general catalog depth for Skill, Company, and Project | Low | Minor — a category or difficulty tier feels sparse if browsed directly | None (pure content work) | Opportunistic, alongside any future content pass | Low |
| 9 | Real company logo rendering has never been visually verified from this development environment | Low | None if the fallback is honestly working (confirmed live); real risk only if logos silently never resolve in production either | Low — the code path is correct either way, this is a verification gap, not a defect | Next time a deploy environment with normal internet access is available for a manual check | Low (a five-minute visual check, not a code change) |

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

### ProjectAttemptEvidence built structurally distinct from ExperimentEvidence, unified only at the writer

- **Decision:** `ProjectAttemptEvidence` is `artifact_url: str | None` + `reflection: str` — it shares no fields with `ExperimentEvidence` (`enjoyment`/`curiosity`/`frustration`/`persistence`/`confidence`/`reflection`). Both still write through the same `record_new_evidence()` function.
- **Context:** Sprint 3's kickoff explicitly required verifying Project evidence is fundamentally different from Experiment evidence before writing any completion code — Experiment answers "did the student explore this," Project answers "did the student demonstrate this."
- **Alternatives considered:** Reuse `ExperimentEvidence` as-is for Project too (fastest to build, but would ask a student "did you enjoy building this?" for a capability claim, and would make Skill evidence indistinguishable from Trait evidence); add a generic `ActivityEvidence` union type covering both.
- **Why this decision won:** The two evidential questions are genuinely different — a feeling isn't a capability claim, and collapsing them would have made the Evidence Graph's `source`/`related_*` fields lie about what kind of claim each record actually represents. A generic union would have solved a problem neither entity actually has yet, at the cost of an abstraction with only two data points to generalize from (this codebase's own established caution — see item 10 above).
- **Consequences:** Two structurally distinct evidence shapes now exist in one codebase, both funneling into the same shared writer and the same `evidence_graph` list — real polymorphism at the storage layer, real type safety at the input layer.
- **Revisit trigger:** If a third, genuinely different "activity" type is ever added (e.g. a Mentor session log) and it turns out to need a third distinct shape too, that's the point to look for a real common denominator across three data points — not before.

### Project completion does not reinforce a World Signal

- **Decision:** `complete_project_attempt()` never touches `profile.discovery_onboarding.world_signals`, unlike `complete_experiment()` which always reinforces the matching World.
- **Context:** `Project` has no `related_world` field — it was deliberately not given one, since a project's connection to Skills/Careers/Companies is the meaningful edge, not a connection to one of the seven onboarding Worlds.
- **Alternatives considered:** Add a `related_world` to `Project` for consistency with Experiment, so completion could reinforce World Signals the same way.
- **Why this decision won:** World Signal reinforcement answers "does this student seem curious about this World" — a question about interest, which is exactly the Experiment-shaped question Sprint 3's design checkpoint said not to duplicate. Forcing a World mapping onto Project would have re-introduced the interest/capability conflation the whole sprint was built to avoid, just one level up the model.
- **Consequences:** Project and Experiment now reinforce genuinely different parts of a student's profile (Skills vs. Worlds/Traits) — the Evidence Graph gets richer along a new axis instead of two mechanisms competing to update the same one.
- **Revisit trigger:** Only if a future product decision explicitly wants "building X made me more interested in the Y World" as a real, evidenced claim — at that point it's a new, deliberate feature, not a default extension of completion.

### Project's genuine-engagement gate is stricter than Experiment's

- **Decision:** `complete_experiment()` always writes at least one evidence string (falling back to `f"Completed '{title}'"` when no flags/reflection are reported); `complete_project_attempt()` writes zero evidence when neither `artifact_url` nor `reflection` is real.
- **Context:** Both gates exist to keep "completion alone" from being treated as evidence — but Experiment's fallback string still counts as *something* (a real completion event, even undescribed), while Project's gate withholds entirely.
- **Alternatives considered:** Mirror Experiment's fallback exactly, writing `"Attempted 'title'"` even on an empty submission, for consistency between the two completion flows.
- **Why this decision won:** Experiment evidence supports a *trait*, where "the student did the activity at all" is itself a weak-but-real signal about exploration. Project evidence supports a *skill capability claim*, where "the student clicked a button" proves nothing about whether they can do the thing — a fallback string here would be exactly the "completion alone is not evidence" failure mode Sprint 3 was built to avoid, just relocated into the fallback branch instead of removed.
- **Consequences:** A student can mark a project attempted with zero real content (the attempt itself is still honestly recorded — it happened), but it contributes nothing to their Skill evidence. Verified live both ways during Sprint 3's manual walkthrough.
- **Revisit trigger:** None expected — this asymmetry is the intended, considered behavior, not a placeholder.

### No backfill/alias script for Project, unlike Skill and Company

- **Decision:** Project's `target_skill_ids`/`related_career_ids`/`related_company_ids` are written directly as real ids in `seed_projects.py`, with no `REQUIRED_SKILL_ALIASES`-style dictionary and no separate `backfill_project_*_edges.py` script.
- **Context:** Skill and Company were *promotions* — an existing free-text field on Career (`reality.required_skills`, `companies`) already held real strings that needed matching to canonical ids. Project is not a promotion; it's a new entity with no prior free-text form to reconcile.
- **Alternatives considered:** Build the alias/backfill pair anyway, for structural consistency with Sprint 1/2's pattern.
- **Why this decision won:** An alias map exists to bridge *already-existing* uncontrolled text to controlled ids. Project never had uncontrolled text — its edges were authored directly as real ids from the start, cross-checked programmatically against the real Skill/Career/Company id lists (catching zero invented references) rather than needing a matching step at all. Building the alias/backfill machinery anyway would have been process cosplay, not a real need.
- **Consequences:** Project's seeding is one script instead of two, and carries no "unmatched alias" risk the way Skill/Company's backfills do (Debt Register item 3/5) — a genuine, structural reduction in risk, not just less code.
- **Revisit trigger:** Only if a future entity is, like Skill/Company, promoted from an existing free-text field — at that point the alias/backfill pattern is the right one to reach for again, not this sprint's direct-seed approach.
