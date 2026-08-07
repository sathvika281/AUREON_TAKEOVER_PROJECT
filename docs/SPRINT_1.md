# Sprint 1 — Skill Entity Foundation

**Sprint execution document.** Not architecture (see [`AUREON_DATA_ARCHITECTURE.md`](./AUREON_DATA_ARCHITECTURE.md)), not the overall tracker (see [`IMPLEMENTATION_TRACKER.md`](./IMPLEMENTATION_TRACKER.md)) — this is the scoped, execution-level plan for one sprint only. Every future sprint gets its own `docs/SPRINT_N.md` following this exact template.

---

## Sprint Goal

Skill exists as a real, first-class, queryable entity — and Career proves the promotion pattern (free-text list → real linked entity) works end to end, on one entity, before it's repeated anywhere else.

That's the whole sprint. Not "start the Skill/Company/Project work" — specifically and only: Skill exists, and Career demonstrates it.

## Why This Sprint Exists

The architecture doc's audit found Skill doesn't exist anywhere in the codebase today — it's a free-text string duplicated across at least eight different list fields with no way to query across them. Every other entity's promotion (Company on Career/Mentor/Opportunity, required-skill edges on Opportunity, skill edges on Learning Resource) depends on Skill existing first. Per the tracker's recommendation, this is the highest-value, lowest-risk, foundation-building move available: one piece of work unlocks four downstream sprints, and it's purely additive against a live, deployed product.

## User Value Created

Modest and honest, not oversold — this is a foundational sprint, and pretending otherwise would violate the architecture doc's own honesty principles. What a real user sees by the end of this sprint:
- A Career page's "required skills" become real, clickable entities instead of static text.
- A new Skill browse/detail page exists, showing which careers need a skill and how to start building it.

That's it. The larger payoff (Company, Project, Opportunity/Mentor skill-matching) doesn't land until later sprints — this sprint's job is to make those possible, not to deliver them.

## Technical Scope

- New `Skill` domain model: `name`, `category` (technical / domain-knowledge / soft-skill / tool), `description`, `parent_skill_id`, `related_skill_ids`, `evidence_types_that_count`.
- New additive migration: `skills` table.
- New additive migration: `required_skill_ids` on `Career`, added **alongside** the existing `required_skills` string field — not replacing it this sprint.
- Seed script: a real, curated skill taxonomy across all four categories — depth over breadth, per the architecture doc's own explicit warning against thin, wide seeding.
- Backfill: link existing seeded Career rows to real Skill rows via the new edge field.
- Backend: repository, service, and one read route for Skill (list + detail); Career's existing route gains the resolved `required_skill_ids` in its response.
- Frontend: a minimal Skill browse page, a Skill detail page (hero, "where it's used," "how to build it" — per the architecture doc's §3 UI Representation), and a new "Skills" section added to the existing Career detail page, rendering real linked chips instead of the current plain-text list.
- Backend tests for the new model/repository/service/route.
- Full regression pass on existing Career tests and routes.

## Explicit Out-of-Scope Items

- Company entity (Sprint 2+)
- Project entity (Sprint 2+)
- Any Skill promotion on Mentor (`daily_skills`), Opportunity (`required_skills`/`preferred_skills`), Learning Resource, or Trend — Career is the *only* proof-of-concept this sprint
- Removing the old `Career.required_skills` string field — it stays alongside the new edge field until a later, separate, explicit migration
- Skill verification/assessment partner integrations
- Skill-based recommendation or matching algorithms
- Any change to `CareerDNA`/trait scoring — Skill and Career DNA traits are different concepts; this sprint introduces no overlap or confusion between them
- Redesigning any existing screen beyond the one new Skills section on Career

## Things We Will Not Do In This Sprint

This is the section that matters most for keeping Sprint 1 from quietly becoming Sprint 1-4 combined. Each exclusion below has a reason, not just a label — the reason is what should stop the temptation when it comes up mid-sprint.

- **We are not refactoring Student.** It's the highest-value, highest-risk item in the whole roadmap specifically *because* every existing feature reads `StudentProfile` directly today. Touching it in the same sprint as a brand-new entity doubles the blast radius of anything that goes wrong, for no reason — Skill doesn't need Student to change to exist.
- **We are not building Company.** Company is next, not now. It shares a category-badge and logo pattern with Skill's UI that will be tempting to build "while we're in here" — resist it. A half-built Company entity with no seed data helps nobody and blurs this sprint's own Definition of Done.
- **We are not building Project.** Same reasoning — Project explicitly depends on Skill (`target_skill_ids`) existing and stable first. Building it now means building it against a moving target.
- **We are not redesigning the UI.** The new Skill pages use existing tokens and existing component patterns exactly as they are today. If a new visual pattern feels necessary, that's a signal to stop and flag it, not to design one mid-sprint.
- **We are not adding new features.** No skill-progress tracking, no gamification, no new navigation entries beyond what's needed to reach the Skill page. If it's not on the task checklist below, it's not this sprint.
- **We are not improving unrelated code.** Seeing something else in the codebase that could be cleaner while working nearby is not a reason to touch it this sprint. Write it down for later; don't fold it in.

If any of the above starts to feel necessary mid-sprint, that's a signal to stop and re-scope explicitly — as a conscious decision, updated in this document — not to quietly expand the sprint.

## Task Checklist

- [ ] Define `Skill` domain model
- [ ] Additive migration: `skills` table
- [ ] Additive migration: `required_skill_ids` on `Career` (nullable/defaulted, alongside existing field)
- [ ] Seed script: real skill taxonomy, all four categories, real depth
- [ ] Backfill: link existing Career rows to real Skill rows
- [ ] Backend: Skill repository + service + read route (list, detail)
- [ ] Backend: Career route resolves and returns `required_skill_ids` alongside existing fields
- [ ] Backend tests: model, repository, service, route
- [ ] Full backend regression run (existing suite stays green)
- [ ] Frontend: Skill browse page
- [ ] Frontend: Skill detail page (hero / where-it's-used / how-to-build-it)
- [ ] Frontend: new Skills section on the existing Career detail page, real linked chips
- [ ] `tsc` + production build clean
- [ ] Live manual walkthrough (see Demo Checklist)
- [ ] Tracker updated: Sprint 1 marked complete, Sprint 2 scoped

## Acceptance Criteria

- A `Skill` has a name, category, and description, and is fetchable via a real API route.
- A Career detail page shows its required skills as real, clickable entities linking to a real Skill detail page — not plain text.
- A Skill detail page shows which real, seeded careers require it.
- The old `Career.required_skills` string field is untouched and still present in the API response — nothing that reads it today breaks.
- No existing Career, Mentor, Opportunity, or any other route's behavior changes.

## Testing Checklist

- [ ] Backend unit tests for `Skill` model, repository, service pass
- [ ] Backend route tests for the new Skill endpoints pass
- [ ] Backend regression: full existing suite still green, zero new failures
- [ ] Migration applied cleanly against a real database; additive nature confirmed (no existing column dropped or altered)
- [ ] `tsc -b --force` clean
- [ ] `npm run build` clean
- [ ] Manual walkthrough: open a Career page, see real skill chips, click through to a Skill page, click back through to a related Career
- [ ] Manual check: zero console errors on either new page
- [ ] Manual check: an entirely unrelated existing page (e.g. Expert Connect) still works unmodified, confirming no accidental regression outside Career

## Demo Checklist

- [ ] Open a real Career page → Skills section shows real, named skills, not a raw string list
- [ ] Click a skill → lands on a real Skill detail page with real content, not a placeholder
- [ ] Skill detail page shows the real careers requiring it, linking back
- [ ] No dead ends: every new page has a real next step (per the architecture doc's own no-dead-ends rule)
- [ ] No visible seed/test artifacts on any reachable page
- [ ] Cold-load test: refresh mid-navigation, confirm no broken state

## Risks

- **Migration risk:** the `required_skill_ids` edge touches a live, tested, deployed model. Mitigated by strict additive-only migration and a full regression pass before merge.
- **Seed thinness risk:** a Skill catalog that's technically real but too sparse to feel connected would undercut the whole point. Mitigated by prioritizing depth on a smaller, real set over breadth.
- **Scope creep risk:** Company and Project are adjacent and will feel like "just one more small thing." Mitigated by the explicit exclusions above and by treating any temptation to add them as a signal to stop, not proceed.
- **Design inconsistency risk:** new pages introduce a visual pattern that doesn't match the existing system. Mitigated by using only existing tokens/components, no new ones.

## Rollback Strategy

Every piece of this sprint is additive by design, which makes rollback straightforward at every stage:
- The new `skills` table can be dropped with zero impact on any existing table — nothing live depends on it yet.
- `Career.required_skill_ids` is nullable and additive; it can be ignored or dropped without touching `Career.required_skills` or anything else on the model.
- Frontend changes are two new routes plus one new section on an existing page — revertible via a targeted git revert of the specific commits, without affecting any other screen.
- Work is committed in small, independently-revertible increments (model → migration → seed → backend route → frontend) rather than one large commit, so a problem at any single stage can be isolated and rolled back without losing the stages before it.

## Definition of Done

- All Task Checklist items complete.
- All Acceptance Criteria met.
- All Testing Checklist items pass.
- All Demo Checklist items pass on the actual deployed environment, not just locally.
- Zero regressions to any existing feature.
- `IMPLEMENTATION_TRACKER.md` updated: Sprint 1 marked complete with a real completed date, Sprint 2 scoped in detail.
- This document itself is left as-is afterward — a historical record of what Sprint 1 actually was, not edited to match what shipped if scope changed along the way (any real scope change gets logged here explicitly, not silently absorbed).
