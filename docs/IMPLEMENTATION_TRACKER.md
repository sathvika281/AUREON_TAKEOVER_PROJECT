# Aureon 2.0 — Implementation Tracker

This is the execution log, not the architecture. The knowledge model, principles, roadmap phases, and quality bar all live in [`AUREON_DATA_ARCHITECTURE.md`](./AUREON_DATA_ARCHITECTURE.md) and are frozen — this document never restates that content, only tracks real progress against it. Phase numbers below (Phase 1-10) refer directly to that document's §14.

**Last re-baselined:** 2026-08-07, after Sprint 1 (Skill Entity Foundation) completed and was live-verified.

---

## Overall Progress

| # | Phase | Status |
|---|---|---|
| 1 | Knowledge Architecture | ✅ Complete |
| 2 | Database Architecture | 🟡 Partial — Skill (Sprint 1) and Company (Sprint 2) entities + their Career edges live-verified; Project and the remaining promotions (Mentor, Opportunity) not started |
| 3 | Real Data & Data Quality | 🟡 Partial — 23 real skills + 31 real companies seeded, real Career backfills live-verified for both; Project data not started |
| 4 | Information Architecture | 🟡 Partial — exists for pre-existing entities, not yet extended to Skill/Company/Project or the adaptive-journey gating |
| 5 | User Journey & Product Flow | 🟡 Partial — discussed strategically this session, never formalized as real journey maps |
| 6 | Design System | 🟢 Substantially complete — real tokens, motion, and shared components already exist and are actively enforced |
| 7 | Frontend Implementation | 🟡 Partial — large surface area already live (Discover/Explore/Connect/Decide), but nothing yet for the new entities or the adaptive shell |
| 8 | Product Polish | 🟡 Partial — done in pockets (e.g. Your Universe's hover explainability), never as a systematic pass |
| 9 | Production Readiness | 🟡 Partial — real deployment, real auth exist; monitoring, full account-lifecycle, and consent flows unaudited |
| 10 | Demo Readiness | 🔴 Not started — correctly, per the roadmap, this shouldn't start until closer to the deadline |

**Summary: 1 of 10 phases fully complete (10%); Phases 2-3 now two-thirds underway on the entity list (Skill and Company both real, live-verified; Project remains).** The promotion pattern has now proven itself twice, on two different entities, without needing a new abstraction — real evidence it generalizes rather than a one-off. Nothing built so far reflects the adaptive-journey restructuring the knowledge model was designed to support.

---

## Phase-by-Phase Status

### Phase 1 — Knowledge Architecture
**Status:** ✅ Complete. `AUREON_DATA_ARCHITECTURE.md` committed and frozen.

### Phase 2 — Database Architecture
**Status:** 🟡 Partial. Sprint 1 delivered Skill; Sprint 2 delivered Company — both tables plus their Career-promoted edges (`required_skill_ids`, `company_ids`) live-verified. Project and the remaining promotions (Mentor, Opportunity) are not started.
**Objective:** Turn the frozen entity model into real schema — starting with the three genuinely new entities (Skill, Company, Project), plus the promotion of existing free-text fields (`required_skills`, `companies`, `projects`) on Career/Mentor/Opportunity to real foreign-key edges.
**Deliverables:** New tables/models for Skill, Company, Project; additive migrations promoting string-list fields to relationship edges on existing entities; an updated ERD.
**Estimated complexity:** Medium — the new tables themselves are simple; the promotion migrations touch several already-live, tested models and need care not to break what's currently working.
**Dependencies:** Phase 1 (satisfied).
**Risks:** Promotion migrations are the main risk — `Career`, `Mentor`, and `Opportunity` are live, tested, seeded, and deployed. Any change here must be additive-only (new edge fields alongside the old string fields, not a destructive replace) until the new fields are proven, per the Governance section's migration rule.
**Definition of Done:** Skill/Company/Project exist as real tables; at least Career has real `required_skill_ids` edges alongside (not instead of) its existing string fields; full backend test suite still green.

### Phase 3 — Real Data & Data Quality
**Status:** 🟡 Partial. Sprint 1 seeded 23 real skills (27/27 careers backfilled); Sprint 2 seeded 31 real companies (21/27 careers backfilled) — both live-verified with zero dangling references. Project data not started.
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
**Status:** 🟡 Partial (pockets only).
**Objective:** A systematic pass — not another one-off — against the "minute details" checklist already established this session (empty states, loading feedback, copy consistency, chrome consistency).
**Deliverables:** A tracked audit, screen by screen, checked against Definition of Excellence §15.
**Estimated complexity:** Medium, mostly in volume rather than difficulty.
**Dependencies:** Phase 7 substantially complete — polishing unbuilt features wastes the pass.
**Risks:** Being squeezed into the final days instead of scheduled as real time, exactly as the roadmap warns.
**Definition of Done:** Definition of Excellence §15's UX/Design/Maturity checklists pass on every page in scope for the hackathon demo.

### Phase 9 — Production Readiness
**Status:** 🟡 Partial.
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

### Sprint 3+
Not yet planned in detail — will be scoped once Sprint 3 is chosen, per the one-workstream-at-a-time rule.

---

## How to use this file

- Update **Current Status** and **Completed Date** as work happens — this file should always reflect reality, not intent.
- A sprint only gets marked complete when its listed tasks are done and its (implicit, architecture-doc-referenced) Definition of Done is met.
- New sprints get added under **Sprint Log** as the current one nears completion, not planned far in advance — the roadmap above stays the long-range reference; this section is the near-term execution reality.
- This file is updated continuously through development up to hackathon submission.
