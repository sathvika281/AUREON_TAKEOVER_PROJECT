# Aureon 2.0 — Implementation Tracker

This is the execution log, not the architecture. The knowledge model, principles, roadmap phases, and quality bar all live in [`AUREON_DATA_ARCHITECTURE.md`](./AUREON_DATA_ARCHITECTURE.md) and are frozen — this document never restates that content, only tracks real progress against it. Phase numbers below (Phase 1-10) refer directly to that document's §14.

**Last re-baselined:** 2026-08-07, after Sprint 4 (Real Data & Data Quality) completed and was live-verified.

---

## Overall Progress

| # | Phase | Status |
|---|---|---|
| 1 | Knowledge Architecture | ✅ Complete |
| 2 | Database Architecture | 🟢 Substantially complete on the entity list — Skill (Sprint 1), Company (Sprint 2), and Project (Sprint 3) all live-verified; remaining promotions (Mentor, Opportunity edges) not started |
| 3 | Real Data & Data Quality | 🟢 Substantially complete — entity list (23 skills + 31 companies + 20 projects) from Sprints 1-3, plus Sprint 4's full-catalog data-quality pass: fake placeholder URLs found and removed (46 instances), category/vocabulary fields promoted to real enforced types where genuinely justified, 54 real Student Discovery Stories seeded, and a real live data-serving bug found and fixed |
| 4 | Information Architecture | 🟡 Partial — exists for pre-existing entities, not yet extended to the adaptive-journey gating |
| 5 | User Journey & Product Flow | 🟡 Partial — discussed strategically this session, never formalized as real journey maps |
| 6 | Design System | 🟢 Substantially complete — real tokens, motion, and shared components already exist and are actively enforced |
| 7 | Frontend Implementation | 🟡 Partial — large surface area already live (Discover/Explore/Connect/Decide), plus Skill/Company/Project now, but nothing yet for the adaptive shell |
| 8 | Product Polish | 🟡 Partial — done in pockets (e.g. Your Universe's hover explainability), never as a systematic pass |
| 9 | Production Readiness | 🟡 Partial — real deployment, real auth exist; monitoring, full account-lifecycle, and consent flows unaudited |
| 10 | Demo Readiness | 🔴 Not started — correctly, per the roadmap, this shouldn't start until closer to the deadline |

**Summary: 1 of 10 phases fully complete (10%); Phases 2-3 now substantially complete (Skill, Company, and Project all real and live-verified, and the whole existing catalog's data quality — not just the three new entities — has now been genuinely audited and corrected, not merely assumed clean).** The promotion pattern proved itself on Skill and Company; Project proved a second pattern — real, evidence-producing completion — generalizes onto the shared Evidence Graph without duplicating it; Sprint 4 proved the product can survive being tested as a genuine stranger would experience it, catching and fixing a real silent-failure bug that had been live and undetected. Nothing built so far reflects the adaptive-journey restructuring the knowledge model was designed to support.

---

## Phase-by-Phase Status

### Phase 1 — Knowledge Architecture
**Status:** ✅ Complete. `AUREON_DATA_ARCHITECTURE.md` committed and frozen.

### Phase 2 — Database Architecture
**Status:** 🟢 Substantially complete on the entity list. Sprint 1 delivered Skill; Sprint 2 delivered Company — both tables plus their Career-promoted edges (`required_skill_ids`, `company_ids`) live-verified. Sprint 3 delivered Project — its own table, carrying its own outgoing edges (`target_skill_ids`, `related_career_ids`, `related_company_ids`) natively, plus the additive `student_profiles.project_attempts` column and the `EvidenceRecord.related_skill`/`"project"` source extension. The remaining promotions (Mentor, Opportunity) are not started.
**Objective:** Turn the frozen entity model into real schema — starting with the three genuinely new entities (Skill, Company, Project), plus the promotion of existing free-text fields (`required_skills`, `companies`, `projects`) on Career/Mentor/Opportunity to real foreign-key edges.
**Deliverables:** New tables/models for Skill, Company, Project; additive migrations promoting string-list fields to relationship edges on existing entities; an updated ERD.
**Estimated complexity:** Medium — the new tables themselves are simple; the promotion migrations touch several already-live, tested models and need care not to break what's currently working.
**Dependencies:** Phase 1 (satisfied).
**Risks:** Promotion migrations are the main risk — `Career`, `Mentor`, and `Opportunity` are live, tested, seeded, and deployed. Any change here must be additive-only (new edge fields alongside the old string fields, not a destructive replace) until the new fields are proven, per the Governance section's migration rule.
**Definition of Done:** Skill/Company/Project exist as real tables; at least Career has real `required_skill_ids` edges alongside (not instead of) its existing string fields; full backend test suite still green.

### Phase 3 — Real Data & Data Quality
**Status:** 🟢 Substantially complete. Sprint 1 seeded 23 real skills (27/27 careers backfilled); Sprint 2 seeded 31 real companies (21/27 careers backfilled); Sprint 3 seeded 20 real, attemptable projects spanning 20/27 careers — all live-verified with zero dangling references. Sprint 4 then audited the *quality* of the whole catalog (not just the three new entities): found and removed 46 fake `example.com`/`.org` placeholder URLs across Opportunities and Mentors, added permanent regression validation against the same class of mistake, promoted several category/vocabulary fields to real enforced types where live data already justified it, seeded 54 real Student Discovery Stories that existed in the repo but were never applied, and caught a real live bug (an existing migration that had never been run against production) plus a real frontend bug (a failed request silently rendering as an honest empty state) — both fixed and verified.
**Objective:** Seed real, honestly-labeled content for the new entities, and backfill real edges on existing entities.
**Deliverables:** Seed scripts for Skill (a real, curated taxonomy — not exhaustive, but genuine), Company (real, well-known organizations), Project (real, attemptable briefs); a backfill pass linking existing Career/Opportunity rows to the new Skill/Company entities.
**Estimated complexity:** Medium — content-writing heavy rather than technically hard, same shape as every existing seed script in this codebase.
**Dependencies:** Phase 2 schema must exist first.
**Risks:** Scope creep — seeding breadth (hundreds of thin skills) instead of depth (fewer skills, richly and correctly linked) would undercut the whole point of promoting these entities. The architecture doc's own priority order already warns about this.
**Definition of Done:** Every new entity type has enough real, connected rows to make cross-entity browsing feel alive on at least one full path (e.g. one Career → its real Skills → real Projects that build them); zero placeholder/lorem content.

### Phase 4 — Information Architecture
**Status:** 🟡 Partial.
**Objective:** Extend the existing site map to cover Skill/Company/Project pages, and formalize the adaptive-journey (Lost/Explorer/Goal-Oriented) navigation structure that today only exists as strategic discussion, not a real route/visibility map.
**Deliverables:** Page/route entries for the three new entities; a documented navigation-visibility matrix (which nav items show at which stage).
**Estimated complexity:** Low-to-medium — the disclosure-tier decisions are already made per-entity in the architecture doc §2-11; this phase is mostly formalizing routing and the stage-gating rules, not inventing new IA thinking.
**Dependencies:** Phases 2/3 (can't route to pages with no data) for the new entities; independent of those for the adaptive-journey navigation work.
**Risks:** The adaptive-journey gating logic risks becoming vague ("AI decides") instead of the deterministic, signal-driven rule already recommended in this session's earlier strategy conversation — needs to stay concrete.
**Definition of Done:** Every new entity has exactly one canonical route; the stage-gating rule is written down as an explicit, testable function, not left implicit in component logic.

### Phase 5 — User Journey & Product Flow
**Status:** 🟡 Partial.
**Objective:** Turn the three-persona strategic thinking into real, walkable journey maps.
**Deliverables:** One journey map per stage (Lost/Explorer/Goal-Oriented), the specific first-five-seconds entry experience, the return-visit hook.
**Estimated complexity:** Low — this is a design/writing exercise, not an engineering one; most of the raw thinking already happened in this session's product-strategy conversation.
**Dependencies:** Phase 4's IA needs to exist enough to map a journey through it.
**Risks:** Low — the main risk is skipping this and going straight to frontend implementation, which the roadmap explicitly warns produces rework.
**Definition of Done:** Each persona has a real, non-hypothetical path from entry to a meaningful outcome, using only features that exist in the plan.

### Phase 6 — Design System
**Status:** 🟢 Substantially complete.
**Objective:** Extend the existing, already-strong token/component system to cover the new trust-signal patterns the architecture doc calls for (source-note badges, evidence-tier indicators) as shared components rather than ad hoc per-screen implementations.
**Deliverables:** A shared `SourceNote` component, a shared evidence-tier indicator (reusing the existing Emerging/Growing/Strong convention), audited for consistent use across old and new entity pages.
**Estimated complexity:** Low.
**Dependencies:** None blocking — can happen in parallel with anything else.
**Risks:** Low, but real if skipped: without shared components, the new entity pages risk each inventing their own version of "here's the source" styling, reintroducing exactly the inconsistency the architecture doc argues against.
**Definition of Done:** Every entity page's trust signals use the same two or three shared components, not per-page variants.

### Phase 7 — Frontend Implementation
**Status:** 🟡 Partial.
**Objective:** Build real pages for Skill, Company, and Project, and the adaptive-journey shell restructuring.
**Deliverables:** Three new entity pages per their §2-11 UI Representation specs; the stage-gated navigation shell.
**Estimated complexity:** High — this is the largest remaining phase by raw engineering volume.
**Dependencies:** Phases 2, 3, 4, and ideally 6 all need to be real first — this is exactly the phase the roadmap warns against starting early.
**Risks:** Starting this before Phase 2/3 are solid is the single highest-probability way this project loses time, per the roadmap's own explicit warning.
**Definition of Done:** Every new entity page is reachable, renders real data, and satisfies the no-dead-ends rule; existing pages are unaffected (regression-tested).

### Phase 8 — Product Polish
**Status:** 🟡 Partial (pockets only). Sprint 4's Final Release Audit (a fresh-user, no-implementation-knowledge walkthrough) produced a real, concrete, prioritized backlog for whenever this phase starts: a P1/P2 findings list covering loading states, empty-state honesty, 404 handling, catalog discoverability, and completion-state persistence — see the Sprint 4 Release Summary below. Not implemented in Sprint 4 by explicit scope decision (only the one P0 that silently misrepresented a real feature as absent was fixed); this phase should start from that list rather than re-auditing from scratch.
**Objective:** A systematic pass — not another one-off — against the "minute details" checklist already established this session (empty states, loading feedback, copy consistency, chrome consistency).
**Deliverables:** A tracked audit, screen by screen, checked against Definition of Excellence §15.
**Estimated complexity:** Medium, mostly in volume rather than difficulty.
**Dependencies:** Phase 7 substantially complete — polishing unbuilt features wastes the pass.
**Risks:** Being squeezed into the final days instead of scheduled as real time, exactly as the roadmap warns.
**Definition of Done:** Definition of Excellence §15's UX/Design/Maturity checklists pass on every page in scope for the hackathon demo.

### Phase 9 — Production Readiness
**Status:** 🟡 Partial. Sprint 4's Final Release Audit confirmed password reset genuinely does not exist at any layer (no UI link, no `resetPasswordForEmail` call, no profile-page password change) — this phase's own Definition of Done already named "confirmed-working password reset" as a requirement; the gap is now concretely documented rather than assumed.
**Objective:** Audit and close gaps in error handling, auth lifecycle, and consent/privacy flows.
**Deliverables:** Confirmed-working password reset, logout, and data-export flows; basic error monitoring.
**Estimated complexity:** Medium.
**Dependencies:** Independent of the new-entity work — can run in parallel.
**Risks:** Low urgency relative to Phase 10 for the hackathon specifically, but real risk if judges or a real early user hits a broken account flow.
**Definition of Done:** Definition of Excellence §15's Product Maturity checklist passes.

### Phase 10 — Demo Readiness
**Status:** 🔴 Not started — correctly, per the roadmap, this is scheduled deliberately close to the deadline, not now.

---

## Recommendation: highest-priority next task (Sprint 1 — executed, see Sprint Log)

**Build the Skill entity end-to-end — schema, real seed data, and a minimal read-only page — before touching anything else.**

*(This recommendation is now Sprint 1, complete and live-verified below. Left in place as the historical record of the reasoning, per the Decision Log's own "why did we build it this way" principle. Sprint 2's priority gets decided fresh, not assumed from here.)*

This is a deliberately narrow vertical slice through Phases 2 and 3, scoped to one entity, not "finish all of Phase 2." Against the stated formula:

- **Highest user value:** Skill is the connective tissue every other promotion depends on (the architecture doc's own §12 priority order agrees). The moment it exists, Career, Opportunity, Project, and Mentor can all gain real edges — one piece of work unlocks four downstream improvements.
- **Lowest implementation risk:** It's a pure addition. A new `Skill` table and a few new nullable edge columns touch nothing that's currently live, tested, and deployed. Nothing about the working MVP changes until Skill is proven and explicitly wired in — fully consistent with the Governance section's "protect what's deployed" rule.
- **Strong foundation for later work:** Company and Project (the next two priorities) both reference Skill in their own data model. Building Skill first means Company and Project aren't built against a moving target.

Concretely, Sprint 1 (below) scopes this to: the `Skill` model, a real (not exhaustive) seed set across the `technical` / `domain-knowledge` / `soft-skill` / `tool` categories, one additive migration promoting `Career.required_skills` to real `required_skill_ids` edges as proof the promotion pattern works, and a minimal skill browse/detail page. Company, Project, and the remaining edge promotions become their own sprints once this one is done — per the one-workstream-at-a-time rule.

---

## Sprint Log

### Sprint 1 — Skill Entity Foundation
**Goal:** Skill exists as a real, queryable entity with genuine seed data, and one existing entity (Career) demonstrates the promotion pattern end to end.
**Tasks:**
- [x] Define `Skill` domain model (`name`, `category`, `description`, `parent_skill_id`, `related_skill_ids`, `evidence_types_that_count`)
- [x] Additive migration: new `skills` table
- [x] Additive migration: `required_skill_ids` on `Career`, alongside (not replacing) the existing `required_skills` string field
- [x] Seed script: real skill taxonomy, sufficient depth across all four categories
- [x] Backfill: link existing seeded Careers to real Skill rows
- [x] Minimal Skill browse page + Skill detail page (hero, where-it's-used, how-to-build-it sections, per the architecture doc's §3 UI Representation)
- [x] Backend tests for the new model/repository/route
- [x] Full regression pass — existing Career pages/tests unaffected
**Current Status:** ✅ Complete — live-verified end to end.
**Blockers:** None (the two migrations required a manual apply via the Supabase SQL Editor, same environment-specific limitation as every prior migration this project; resolved, not a blocker to close the sprint).
**Dependencies:** None (Phase 1 already complete).
**Completed Date:** 2026-08-07
**Notes:** This sprint intentionally does not touch Mentor, Opportunity, or Company edges yet — those are separate future sprints, kept out of scope here to respect "one workstream at a time." Live verification confirmed: schema live (both migrations applied cleanly, additive, nothing existing altered), 23 skills seeded exactly as designed, 27/27 careers backfilled with zero dangling skill references (real application-level referential integrity holds despite no DB-level FK — matches the intentional trade-off already recorded in the Technical Debt Register), full Playwright walkthrough passed (Career → real skill chips → Skill detail → real requiring careers → round-trip link back), cold-load and hard-refresh both verified directly on the Skill detail route, old `reality.required_skills` field confirmed untouched and still serving, zero regressions across 773 backend tests. No genuinely new technical debt surfaced during verification — every already-documented trade-off held up exactly as anticipated, so the Technical Debt Register is unchanged by this sprint's completion.

### Sprint 1 — Release Summary

**Sprint Goal:** Skill exists as a real, queryable, connected entity — and Career proves the promotion pattern (free-text list → real linked entity) works end to end, before it's repeated anywhere else.

**What Was Implemented:** The `Skill` domain model (4 real categories: technical, domain_knowledge, soft_skill, tool); 23 real, curated skills seeded, derived directly from the real career data already in the catalog, not invented in parallel; Career's `required_skills` promoted to real Skill edges (`required_skill_ids`), additive alongside the untouched original field; the full backend repository/service/route stack for Skill; a Skill browse page, a Skill detail page, and a new Skills section on the existing Career detail page, all fully routed and cross-linked.

**Database Changes:** Migration 0025 (new `skills` table, FK on `parent_skill_id`, unique index on `name`, index on `category`); migration 0026 (new `required_skill_ids` jsonb column on `careers`, additive, defaulted). Both applied live and verified. Nothing existing altered or dropped.

**API Changes:** New `GET /v1/skills` (list, category filter) and `GET /v1/skills/{id}` (detail, includes real requiring careers). `GET /v1/careers/{id}` extended with a `required_skills: Skill[]` field, additive alongside the existing `reality.required_skills` string list.

**Frontend Changes:** New `SkillsScreen`, `SkillDetailScreen`, and `CareerSkillsSection` (on the existing Career page). New routes `/skills` and `/skills/:skillId` — no new top-level nav entry, reached via real links from Career pages, per sprint scope.

**Tests Added:** 10 new/updated backend tests — Skill DTO composition, Skill detail composition (including honest empty-state behavior), 5 route tests (list, category filter, detail, honesty check, 404), 2 Career view tests (skill resolution + default-empty backward compatibility). All passing.

**Regression Status:** 773/773 backend tests passing (763 pre-existing + 10 new) — zero failures, zero regressions. `tsc` clean. Production build clean.

**Known Technical Debt (Intentional):** Fully documented in `TECHNICAL_DEBT_REGISTER.md` — no DB-level FK on `required_skill_ids` (trusted to application-level discipline; live-verified zero dangling references), reverse lookup via full-table scan (fine at current ~27-career scale), exact-string alias matching (100% correct against current data, no fuzzy fallback), manual SQL migration application (the one item flagged as must-change-before-real-production). Nothing new surfaced during live verification — every anticipated trade-off held up exactly as designed.

**Merge Recommendation:** Approved. Additive-only, fully tested, fully live-verified against real seeded data, zero regressions to any existing feature.

**Readiness for Sprint 2:** Ready. The promotion pattern — additive jsonb edge, additive migration, repository/service/route mirroring Trend's existing shape, backfill-from-real-data seeding — is now proven once, live, end to end. Company and Project can follow the same shape with the approach already de-risked.

### Sprint 2 — Company Entity Foundation
**Goal:** Company exists as a real, queryable entity; Career demonstrates the same promotion pattern Sprint 1 proved for Skill, confirming it generalizes to a second entity. Full plan: [`SPRINT_2.md`](./SPRINT_2.md).
**Tasks:** All complete — see `SPRINT_2.md`'s Task Checklist.
**Current Status:** ✅ Complete — live-verified end to end.
**Blockers:** None (same manual SQL Editor step as Sprint 1 for the two migrations — resolved, not a blocker to close the sprint).
**Dependencies:** Sprint 1 (Skill) complete — satisfied.
**Completed Date:** 2026-08-07
**Notes:** Career-only promotion this sprint, same discipline as Sprint 1 (Mentor/Trend/Institution's own `companies` fields deferred, not touched). One real bug caught and fixed during implementation, before touching live data: the seed script initially conflated two different real companies (Cerner/Oracle Health vs. Epic Systems) — caught via cross-checking every alias key against the actual live database rather than trusting a manual read a second time, fixed immediately per the sprint's own "bug → fix now" rule. Live verification confirmed: schema live, 31 companies seeded (24 company / 5 nonprofit / 2 government — an honest reflection of the real seeded data, which includes real governments and NGOs, not only for-profit companies), 21/27 careers backfilled with zero dangling references, full Playwright walkthrough passed (Career → real company chips → Company detail → real hiring careers → round-trip link back, browse page + organization_kind filter both correct), old `companies` field confirmed untouched and still rendering simultaneously with the new section. One genuine, new, non-blocking finding: this sandbox cannot resolve external DNS for the Clearbit logo API at all, so every logo fell back to the designed initials tile — confirmed working exactly as intended, but the real-logo path itself has never been directly observed, only inferred; logged in the Technical Debt Register as a verification gap, not a defect, with a real trigger (next deploy with normal internet access). Zero regressions: 784/784 backend tests passing.

### Sprint 2 — Release Summary

**Sprint Goal:** Company exists as a real, queryable, connected entity — and Career demonstrates the same promotion pattern proven for Skill in Sprint 1, confirming it generalizes to a second entity rather than being a one-off.

**What Was Implemented:** The `Company` domain model (reusing `OrganizationKind` from the existing `Opportunity` model rather than inventing a parallel taxonomy — the real seeded data includes genuine governments and NGOs, not only for-profit companies); 31 real, curated companies seeded, derived directly from the real `companies` text already in the career catalog; Career's `companies` promoted to real Company edges (`company_ids`), additive alongside the untouched original field; the full backend repository/service/route stack for Company; a Company browse page, a Company detail page, and a new Companies section on the existing Career detail page — including a genuinely new small component, `CompanyLogo`, with a designed and live-confirmed initials fallback for when a real logo doesn't resolve.

**Database Changes:** Migration 0027 (new `companies` table, unique index on `name`, index on `industry`); migration 0028 (new `company_ids` jsonb column on `careers`, additive, defaulted). Both applied live and verified. Nothing existing altered or dropped.

**API Changes:** New `GET /v1/companies` (list, `industry`/`organization_kind` filters) and `GET /v1/companies/{id}` (detail, includes real hiring careers). `GET /v1/careers/{id}` extended with a `hiring_companies: Company[]` field, additive alongside the existing `companies` string list.

**Frontend Changes:** New `CompaniesScreen`, `CompanyDetailScreen`, `CompanyLogo` (shared, three real call sites), and `CareerCompaniesSection` on the existing Career page. New routes `/companies` and `/companies/:companyId` — no new top-level nav entry, same scope discipline as Sprint 1.

**Tests Added:** 11 new/updated backend tests — Company DTO composition, Company detail composition (including honest empty-state and non-company-org edge cases), 5 route tests (list, organization_kind filter, detail, honesty check, 404), 2 Career view tests (company resolution + default-empty backward compatibility).

**Regression Status:** 784/784 backend tests passing (773 pre-existing + 11 new) — zero failures, zero regressions. `tsc` clean. Production build clean.

**Known Technical Debt (Intentional):** Fully documented in `TECHNICAL_DEBT_REGISTER.md`, mostly extending Sprint 1's already-tracked items to a second entity (no DB-level FK, full-table reverse lookup, exact-string alias matching) rather than introducing new categories of debt. One genuinely new, real finding: this development sandbox cannot resolve external DNS for the Clearbit logo API, so the real-logo path has never been directly observed — only the fallback has, and it works correctly. Logged with a concrete revisit trigger (first deploy with normal internet access), not a defect.

**Merge Recommendation:** Approved. Additive-only, fully tested, fully live-verified against real seeded data, zero regressions to any existing feature. One real bug (a company mismatch in the seed script) was caught and fixed before it ever touched live data.

**Readiness for Sprint 3:** Ready. The promotion pattern has now proven itself twice on two different entities without needing a new abstraction — real, repeated evidence it generalizes. Project (the next priority per the architecture doc's own ordering) can follow the same shape with even more confidence than Sprint 2 had.

### Sprint 3 — Project Entity Foundation
**Goal:** Project exists as a real entity, and — unlike Skill/Company — produces real, evidence-backed capability signals on completion, extending the shared Evidence Graph with a new `related_skill` dimension rather than duplicating Experiment's evidence system. Full plan: [`SPRINT_3.md`](./SPRINT_3.md).
**Tasks:** All complete — see `SPRINT_3.md`'s Task Checklist.
**Current Status:** ✅ Complete — live-verified end to end.
**Blockers:** None (two manual SQL Editor steps for this sprint, same environment-specific limitation as every prior migration — resolved, not a blocker to close the sprint).
**Dependencies:** Sprint 1 (Skill) and Sprint 2 (Company) complete — satisfied.
**Completed Date:** 2026-08-07
**Notes:** No migration needed on `careers` this sprint — Project carries its own outgoing edges rather than being promoted from an existing Career field, unlike Skill/Company. Learning Resource relationship explicitly and honestly omitted (entity doesn't exist yet). One real gap caught during live verification (not during code review or tests): `StudentProfile.project_attempts` was added to the Python model but no migration added the matching column to the real `student_profiles` table — that table does a column-per-field upsert, not a jsonb-blob write, so every profile save failed with a PostgREST schema-cache error until migration 0030 was applied. This is the *second* time this exact class of gap has occurred (the first was `circle_resource_progress`, fixed by migration 0019) — logged as a reinforced Technical Debt Register item rather than a one-off, since unit tests (which use in-memory fakes) structurally cannot catch it; only live verification can, which is exactly why it's a mandatory gate before any sprint closes. Live verification confirmed: both migrations applied cleanly, 20 projects seeded (cross-checked programmatically against real Skill/Career/Company ids, zero invented references), a real completion via the live API and the live UI both wrote exactly 2 evidence records per target skill (artifact_url + reflection, 3 skills → 6 records) correctly tagged `source="project"`/`related_skill`, an empty completion recorded the attempt but wrote zero evidence (the genuine-engagement gate holds both ways, live), zero World Signal reinforcement (correctly excluded), and the Career detail page's new Projects section correctly resolves the real reverse link. Zero regressions: 802/802 backend tests passing (784 pre-existing + 18 new).

### Sprint 3 — Release Summary

**Sprint Goal:** Project exists as a real, queryable, connected entity — and, unlike Skill/Company, becomes the first entity in this series to produce real, evidence-backed signals about a student's *demonstrated capability* rather than just interest, by extending the shared Evidence Graph with a genuinely new dimension instead of duplicating Experiment's evidence system.

**What Was Implemented:** The `Project` domain model (`difficulty_level` reusing the existing `DifficultyLevel` type rather than a parallel enum, same reuse discipline as Sprint 2's `OrganizationKind`); 20 real, attemptable project briefs seeded, spanning 20 of the 27 seeded careers, each with real `target_skill_ids`/`related_career_ids`/optional `related_company_ids` cross-checked programmatically against the real seed data; `EvidenceRecord` extended with a new nullable `related_skill` field and a new `"project"` source literal, additive and backward-compatible; `ProjectAttemptEvidence` (artifact_url + reflection) built structurally distinct from `ExperimentEvidence` (enjoyment/curiosity/persistence/confidence flags) — Experiment answers "did the student explore this," Project answers "did the student demonstrate this" — while both write through the same shared `record_new_evidence` writer, one evidence ecosystem, not two; `complete_project_attempt()` mirrors `complete_experiment()`'s composition shape but deliberately does *not* reinforce a World Signal (Project has no `related_world`) and applies a stricter genuine-engagement gate — completion alone writes an honest attempt record but zero evidence unless the student provided a real artifact URL or reflection; the full backend repository/service/route stack for Project, including a student-scoped completion route; a Project browse page, a Project detail page with an inline completion form, and a new Projects section on the Career detail page.

**Database Changes:** Migration 0029 (new `projects` table, unique index on `title`, index on `difficulty_level`); migration 0030 (new `project_attempts` jsonb column on `student_profiles`, additive, defaulted — the same class of gap `circle_resource_progress` hit once before). Both applied live and verified. Nothing existing altered or dropped. `EvidenceRecord.related_skill` and the `"project"` source literal are additive, nullable/backward-compatible changes to a shared, multi-consumer model.

**API Changes:** New `GET /v1/projects` (list, `difficulty_level` filter) and `GET /v1/projects/{id}` (detail, real resolved target skills/related careers/related companies). New `POST /v1/students/{student_id}/projects/{project_id}/complete` (student-scoped, `require_own_profile`-gated, mirrors the experiment-completion route's shape). `GET /v1/careers/{id}` extended with a `related_projects: Project[]` field — the reverse-lookup direction, since Project holds the edge rather than Career.

**Frontend Changes:** New `ProjectsScreen`, `ProjectDetailScreen` (with the inline artifact-url/reflection completion form), and `CareerProjectsSection` on the existing Career page. New routes `/projects` and `/projects/:projectId` — no new top-level nav entry, same scope discipline as Sprint 1/2.

**Tests Added:** 18 new backend tests — Project DTO/detail-view composition (including honest empty-state behavior), a dedicated genuine-engagement-gate suite proving evidence is written correctly for real content and withheld for empty/whitespace-only content (plus dedup and non-reinforcement-of-World-Signal checks), full route tests for the catalog and the completion flow (including a live-path proof that an empty completion writes zero evidence through the real HTTP layer), and 2 Career view tests for `related_projects` resolution.

**Regression Status:** 802/802 backend tests passing (784 pre-existing + 18 new) — zero failures, zero regressions. `tsc` clean. Production build clean.

**Known Technical Debt (Intentional and newly found):** Fully documented in `TECHNICAL_DEBT_REGISTER.md` — Project's own edges extend the existing "no DB-level FK, full-table reverse lookup" trade-off (items 1/2) to a third entity, as anticipated; the Career detail route now carries 6 repository dependencies, crossing the threshold item 4 flagged as worth a proactive check. One genuinely new, reinforced finding: `student_profiles`' column-per-field storage shape is invisible to unit tests (which use in-memory fakes) and has now caused the same class of live-verification-only bug twice — logged as its own debt item with a concrete mitigation recommendation, not treated as a one-off mistake.

**Merge Recommendation:** Approved. Additive-only, fully tested, fully live-verified against real seeded data including both directions of the genuine-engagement gate, zero regressions to any existing feature. One real gap (the missing `project_attempts` column) was caught by the mandatory live-verification step and fixed with a dedicated, precedented migration before merge.

**Readiness for Sprint 4:** Ready. Three entities (Skill, Company, Project) now share a proven repository/service/route shape, and Project additionally proves the Evidence Graph can grow a new dimension without forking into a parallel system. Per this session's explicit instruction, Sprint 4 is not scoped or started in this session — it begins fresh, once requested.

### Sprint 4 — Real Data & Data Quality
**Goal:** Make Aureon's existing knowledge ecosystem feel like a real, curated product rather than a database populated for demonstration — audited first, corrected only where genuinely justified, never "improved" by inventing content.
**Tasks:** Kickoff audit (data credibility question) → External References & Data Assets audit + fixes → Data Representation audit + fixes → a fresh-user Final Release Audit → the one P0 finding fixed (migration + real content seeding + a real frontend bug) end to end.
**Current Status:** ✅ Complete — live-verified end to end.
**Blockers:** None (two manual SQL Editor steps this sprint — the `discovery_themes` migration and the `official_link` nullability migration — same environment-specific limitation as every prior sprint; resolved, not a blocker to close the sprint).
**Dependencies:** Sprint 1-3 (Skill, Company, Project) complete — satisfied.
**Completed Date:** 2026-08-07
**Notes:** This sprint had no dedicated planning document (unlike Sprints 1-3's `SPRINT_N.md`) — it was scoped and executed phase-by-phase via direct instruction, each phase gated on a report-before-fix checkpoint. Two real, live bugs were found and fixed, neither of which any prior sprint's test suite could have caught: (1) a real migration (`0021_journey_stories_discovery_themes.sql`) that existed correctly in the repo but was never applied to the live database, silently 500-ing a real, seeded feature; (2) a frontend `.catch(() => {})` that converted that failure (and any future one) into a false "No Stories Found" honest-looking empty state — fixed by making `loading`/`success`/`error` explicit, reusing the existing `EmptyStatePanel`/`ShieldAlert` error-state convention already established in `HistoryScreen.tsx`, with a working Retry action. A near-miss was caught before shipping: `CareerStory.trait_tags` was almost given the same `Literal[TraitName]` type-tightening applied to `Career`/`Mentor`/`Institution`'s same-named field, which would have broken 24 of the 54 real Student Discovery Stories seeded later this same sprint (that field is genuinely a different concept — topic/world alignment, not CareerDNA traits — despite the coincidental name and data-shape match). The Final Release Audit (a genuinely fresh, no-implementation-knowledge account walked through signup → onboarding → every nav section → project completion → deep links → logout) produced a full P0/P1/P2 findings report; only the one P0 (the silently-masked feature failure) was fixed this sprint, by explicit, repeated scope instruction — Forgot Password, Your Universe's blank loading window, generic 404 handling, Project-attempt-state persistence, and catalog nav discoverability are all real, confirmed, but deliberately deferred to the later product/UI pass (Phase 8/9).

### Sprint 4 — Release Summary

**Sprint Goal:** Make Aureon's existing catalog and product surface feel like it was genuinely curated and tested, not just built — auditing before changing anything, fixing only what real evidence justified, and closing the one defect severe enough to make a real, fully-seeded feature invisible to every user.

**What Was Implemented:**
- **External references cleanup:** found and removed 46 fake `example.com`/`.org` placeholder URLs (40 `Opportunity.official_link` values, 6 `Mentor` portfolio/social links across 9 seed files), plus one unverifiable-but-plausible link for a fictional persona (Felix Nguyen's itch.io URL) removed under the same "verified destination > honest absence > fabricated destination" principle. `Opportunity.official_link` loosened from required to optional (`str | None`) since illustrative composite postings genuinely have no real listing to link to; the frontend now renders no "View Details" link at all rather than a link to nowhere.
- **Permanent regression validation:** two new generic tests (`test_seed_data_quality.py`) scanning all 36 real catalog seed sources for reserved/placeholder domains and malformed URL-shaped fields — structural, not hardcoded to the specific records found.
- **Data representation fixes:** `Career.category`, `Mentor.role_type`, and `trait_tags` (Career/Mentor/Institution) promoted from unconstrained `str`/`list[str]` to real `Literal` types, derived from vocabularies that live data already conformed to 100% — closes a class of silent-drift risk the same way the URL validation does, for category fields instead of links. `CareerStory.trait_tags` deliberately excluded after tracing its real, different consumer (see Decision Log).
- **Student Discovery content seeding:** 54 real stories (2 pre-written, previously-unseeded scripts) seeded live, bringing `career_stories` from 150 (all Career Explorer "Human Stories") to 204 (150 + 54 genuinely distinct Student Discovery narratives) — zero fabricated content, all pre-existing and validated before seeding.
- **One real live bug found and fixed:** migration `0021_journey_stories_discovery_themes.sql` existed in the repo but was never applied to the live database — Student Stories 500'd on every request, masked as an honest-looking empty catalog by a frontend bug. Both the missing migration and the masking bug are now fixed.

**Database Changes:** Migration `0021` (finally applied — pre-existing, additive, `career_stories.discovery_themes`); migration `0031` (new, additive — `opportunities.official_link` constraint loosened to nullable). 54 new `career_stories` rows seeded (`story_type='composite_student_discovery'`). 46 live rows corrected (`official_link` nulled on 40 Opportunities; `portfolio_links`/`social_links` cleared on 17 Mentors). Zero destructive changes; the pre-existing 150 Career Explorer stories, 31 companies, and all other catalog data verified untouched throughout.

**API Changes:** None new. `OpportunitySummaryDTO.official_link` loosened to `str | None` (backward-compatible for any consumer already handling a string).

**Frontend Changes:** `OpportunityEqualityScreen.tsx` — conditional "View Details" rendering. `JourneyStoriesScreen.tsx` — explicit `loading`/`success`/`error` states replacing a silent catch, with a working Retry action reusing the existing `EmptyStatePanel` component.

**Tests Added:** 2 new backend tests (`test_no_reserved_example_domains_in_any_seed_data`, `test_url_shaped_fields_are_well_formed_https_urls`), both generic/structural across all 36 real seed sources, plus a coverage-guard test ensuring no future seed script goes unchecked. 11 pre-existing test fixtures fixed (placeholder category/trait values that predated this sprint, caught by the new `Literal` types doing exactly their job).

**Regression Status:** 805/805 backend tests passing throughout every phase of this sprint. `tsc` clean. Production build clean, verified after every change.

**Known Technical Debt (Sprint 4 review):** Fully documented in `TECHNICAL_DEBT_REGISTER.md` — two genuinely new items logged (three unreconciled skill representations with a confirmed 0/33 real vocabulary overlap between Opportunity and the Skill catalog; the silent-failure fix applied to one screen with others unaudited), plus a concrete real-world confirmation added to the already-tracked manual-migration-risk item. Five new Decision Log entries record the real "why" calls made this sprint, including the `CareerStory.trait_tags` near-miss.

**Merge Recommendation:** Approved. Every fix was grounded in a read-before-write audit, verified live, and scoped exactly to demonstrated evidence — no speculative fixes, no manufactured debt, no scope creep into the deliberately-deferred P1/P2 backlog.

**Readiness for Sprint 5:** Ready, whenever scoped. A real, prioritized P1/P2 backlog now exists from the Final Release Audit (Forgot Password, Your Universe's loading state, generic 404 handling, Project-attempt persistence, catalog nav discoverability) for whichever future sprint takes on Phase 8/9 polish work — not started or assumed in Sprint 4, per explicit scope instruction.

### Sprint 5+
Not yet planned in detail — will be scoped once requested, per the one-workstream-at-a-time rule.

---

## How to use this file

- Update **Current Status** and **Completed Date** as work happens — this file should always reflect reality, not intent.
- A sprint only gets marked complete when its listed tasks are done and its (implicit, architecture-doc-referenced) Definition of Done is met.
- New sprints get added under **Sprint Log** as the current one nears completion, not planned far in advance — the roadmap above stays the long-range reference; this section is the near-term execution reality.
- This file is updated continuously through development up to hackathon submission.
