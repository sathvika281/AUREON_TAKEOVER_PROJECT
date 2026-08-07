# Sprint 2 — Company Entity Foundation

**Sprint execution document.** Not architecture (see [`AUREON_DATA_ARCHITECTURE.md`](./AUREON_DATA_ARCHITECTURE.md)), not the overall tracker (see [`IMPLEMENTATION_TRACKER.md`](./IMPLEMENTATION_TRACKER.md)) — the scoped, execution-level plan for this sprint only, following the exact template Sprint 1 established.

## Sprint Goal

Company exists as a real, first-class, queryable entity — and Career demonstrates the same promotion pattern Sprint 1 proved for Skill (free-text list → real linked entity), on a second entity, confirming the pattern generalizes rather than being a one-off.

## Why This Sprint Exists

`companies: list[str]` appears independently on `Career`, `CareerWorld`, `Trend`, `Institution`, and as `Mentor.organization` — five uncoordinated free-text fields that could easily disagree about the same company's name. Company is one of the three entities the architecture audit found genuinely missing (alongside Skill, now done, and Project, not yet started). Per the Technical Debt Register's own priority order, Company is next.

## User Value Created

Real, recognizable company logos on Career pages (via the Clearbit Logo API), a browsable Company catalog, and — the main proof-of-concept — the promotion pattern generalizing to a second entity rather than only ever having worked once.

## Technical Scope

- `Company` domain model: `name`, `industry` (shares vocabulary with `Career.industry`), `size_category`, `what_they_do`, `logo_url`, `hiring_focus_areas`, `notable_for`.
- Additive migration: new `companies` table.
- Additive migration: `company_ids` on `Career`, alongside the existing `companies: list[str]` field (untouched).
- Seed script: real, well-known companies, derived from the real `companies` strings already sitting in seeded Career rows — same "build the taxonomy from real existing data" discipline Sprint 1 established for Skill, not invented in parallel.
- Backfill: link existing Career rows to real Company rows via an alias map, same honest fail-open-if-unmatched approach as Sprint 1.
- Backend: `CompanyRepository`, `company_view.py`, `GET /v1/companies` + `GET /v1/companies/{id}` routes; Career's detail route resolves `company_ids` into real `CompanyDTO` objects.
- Frontend: Company browse page, Company detail page, new Companies section on the Career detail page with real logos and a graceful text-only fallback when a logo doesn't resolve.
- Backend tests mirroring Sprint 1's exact coverage shape (model/view composition, route behavior, honesty checks, 404 handling).

## Explicit Out-of-Scope Items

- Project entity
- Student refactoring
- Company promotion on Mentor (`organization`), Trend, Institution, or Opportunity — Career is the only proof-of-concept this sprint, same discipline as Skill-on-Career-only in Sprint 1
- Company↔Skill or Company↔Opportunity relationships (both real in the architecture doc, both deferred)
- Any UI redesign, search improvements, recommendation logic, AI changes, or auth changes
- Any refactoring unrelated to Company

## Things We Will Not Do In This Sprint

- **We are not building Project.** It depends on nothing Company provides, and building it now would repeat Sprint 1's exact "don't build the next entity early" temptation in a new form.
- **We are not refactoring Student.** Unrelated to Company, and still the highest-blast-radius item in the whole roadmap for good reason.
- **We are not promoting Company on Mentor, Trend, or Institution.** Career is the single proof-of-concept, matching Sprint 1's scope discipline exactly — proving the pattern generalizes needs one clean second case, not four simultaneous ones.
- **We are not redesigning the UI.** Company pages use existing tokens and existing component patterns exactly as Skill's did.
- **We are not building a company-verification or self-service claiming flow.** The architecture doc flags this as a real future direction, explicitly not now.

## Task Checklist

- [ ] Define `Company` domain model
- [ ] Additive migration: `companies` table
- [ ] Additive migration: `company_ids` on `Career`
- [ ] Seed script: real companies derived from existing seeded data
- [ ] Backfill: link existing Career rows to real Company rows
- [ ] Backend: Company repository + service + read route
- [ ] Backend: Career route resolves `company_ids`
- [ ] Backend tests
- [ ] Full backend regression run
- [ ] Frontend: Company browse page
- [ ] Frontend: Company detail page (with graceful logo fallback)
- [ ] Frontend: Companies section on Career detail page
- [ ] `tsc` + production build clean
- [ ] Live manual walkthrough
- [ ] Tracker updated, Sprint 2 release summary, commit

## Acceptance Criteria

- A `Company` has a name, industry, and description, fetchable via a real API route.
- A Career detail page shows its hiring companies as real, clickable entities with real logos (or an honest fallback) — not plain text.
- A Company detail page shows which real, seeded careers hire for it.
- The old `Career.companies` string field is untouched and still present in the API response.
- No existing Career, Skill, Mentor, or Opportunity route's behavior changes.

## Testing Checklist

Same shape as Sprint 1: backend unit tests for model/view composition, route tests with fake repositories, full regression run, `tsc`/build clean, live walkthrough with console-error and cold-load checks, confirmation that an unrelated existing page is unaffected.

## Demo Checklist

Open a Career page → real company logos/chips → click through to a real Company detail page → see real careers hiring for it → round-trip link back → no dead ends → no visible seed/test artifacts.

## Risks

- **Logo resolution:** Clearbit's API depends on a real domain being known for each company; some seeded companies may not resolve a logo. Mitigated by a designed text-fallback (never a broken-image icon), decided explicitly in the frontend task rather than assumed to always work.
- **Name-variant matching:** same class of risk as Skill's alias matching (e.g. "Google" vs "Alphabet") — same honest, fail-open, exact-match approach, extended rather than reinvented.
- **Scope creep toward Project or Mentor promotion** — mitigated by the explicit exclusions above.

## Rollback Strategy

Identical shape to Sprint 1: every change is additive (new table, new nullable/defaulted column, two new routes, one new page section), so any stage can be independently reverted without affecting what came before it or anything currently live.

## Definition of Done

All Task Checklist items complete, all Acceptance Criteria met, all Testing/Demo Checklist items pass on the actual deployed environment, zero regressions, tracker updated with a real completion date, Sprint 2 Release Summary written, working tree clean, committed.
