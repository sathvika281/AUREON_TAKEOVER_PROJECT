# Sprint 3 — Project Entity Foundation

**Sprint execution document.** Not architecture, not the tracker — the scoped, execution-level plan for this sprint, following the Sprint 1/2 template.

## Sprint Goal

Project exists as a real, first-class entity — and, unlike Skill and Company, it's the first entity in this series to produce real, evidence-backed signals about a student's *capabilities* (not just interests), extending the shared Evidence Graph with a genuinely new dimension (`related_skill`) rather than duplicating Experiment's existing evidence system.

## Why This Sprint Exists

Project is the third of the architecture doc's three missing entities. Its defining trait, per §4, is that it's distinct from Experiment: Experiment answers "did the student explore this," Project answers "did the student demonstrate this." See the Design Checkpoint above for the full reasoning — this sprint exists specifically to build that demonstration-evidence path, not just another browsable catalog.

## User Value Created

A real project catalog connected to Skills, Careers, and (where genuinely applicable) Companies — and, new this sprint, a real way for a student to mark a project attempted and have that genuinely count as evidence toward a specific skill, visible as confirmation on completion.

## Technical Scope

- `Project` domain model: `title`, `brief`, `difficulty_level`, `estimated_hours`, `target_skill_ids`, `related_career_ids`, `related_company_ids` (optional, only where genuinely applicable), `submission_type`. No `starter_resources` — Learning Resource doesn't exist yet, honestly omitted rather than faked.
- Additive migration: new `projects` table. **No migration needed on `careers`** — unlike Skill/Company, Project carries its own outgoing edges rather than being promoted from an existing Career field.
- Additive field: `EvidenceRecord.related_skill: str | None = None` — the real, new extension to the shared evidence model.
- Additive literal value: `"project"` added to `EvidenceRecord.source` and `record_new_evidence`'s source parameter.
- `ProjectAttempt` + `ProjectAttemptEvidence` models (structurally distinct from `ExperimentCompletion`/`ExperimentEvidence` — see Design Checkpoint), `StudentProfile.project_attempts: list[ProjectAttempt]` — additive list field, same category of change as `career_experiments`, explicitly not the deferred Student refactor.
- `complete_project_attempt()` service function mirroring `complete_experiment()`'s structure — appends the attempt, writes real `EvidenceRecord`s (`source="project"`, `related_skill=<id>`) for each of the project's `target_skill_ids`, gated on genuine engagement.
- Backend: `ProjectRepository`, `project_view.py`, `GET /v1/projects` + `GET /v1/projects/{id}` (mirroring Skill/Company), plus `POST /v1/students/{student_id}/projects/{project_id}/complete` (mirroring the existing experiment-completion route).
- Real seed data: real, attemptable project briefs, derived from real target skills/careers already seeded.
- Frontend: Project browse page, Project detail page (with an inline completion form — artifact URL + reflection, mirroring the detail-page-embedded-interaction pattern already used elsewhere), a small Projects section on the Career detail page (mirroring `CareerSkillsSection`/`CareerCompaniesSection` exactly — the same established pattern, not a new one).

## Explicit Out-of-Scope Items

- Learning Resource entity or any relationship to it
- Student refactor (the core/ledger split) — `project_attempts` is additive only
- Any UI redesign
- Recommendation engine or AI changes
- Skill-evidence-tier display on the Skill detail page (a real, natural future consumer of `related_skill` evidence — deliberately deferred, not built reactively this sprint)
- WorldSignal reinforcement from Project completion — that mechanism is Experiment-specific (tied to `related_world`, which Project doesn't have); Project's evidence is scoped to Skills only

## Task Checklist

- [x] Define `Project` domain model
- [x] Additive migration: `projects` table
- [x] Additive field: `EvidenceRecord.related_skill`
- [x] Additive: `"project"` source literal on `EvidenceRecord`/`record_new_evidence`
- [x] `ProjectAttempt`/`ProjectAttemptEvidence` models + `StudentProfile.project_attempts`
- [x] `complete_project_attempt()` service function
- [x] Seed script: real, attemptable projects
- [x] Backend: Project repository + service + read routes
- [x] Backend: completion route
- [x] Backend tests (catalog + completion + evidence-writing)
- [x] Full backend regression run
- [x] Frontend: Project browse page
- [x] Frontend: Project detail page + inline completion form
- [x] Frontend: Projects section on Career detail page
- [x] `tsc` + production build clean
- [x] Live manual walkthrough (including a real completion, confirming real evidence written)
- [x] Tracker updated, release summary, commit

## Acceptance Criteria

- A `Project` has a title, brief, difficulty, and estimated hours, fetchable via a real API route.
- A Project's `target_skill_ids`/`related_career_ids` resolve to real Skill/Career entities on its detail page.
- Completing a project with a real artifact URL or reflection writes a real `ProjectAttempt` to the student's profile and real `EvidenceRecord`s (`source="project"`, `related_skill` set) for each target skill.
- Completing a project with neither an artifact URL nor a reflection does **not** write evidence (genuine-engagement gate holds).
- No existing Career, Skill, Company, or Experiment route's behavior changes.

## Testing Checklist

Same shape as Sprint 1/2: model/view composition tests, route tests with fake repositories, a dedicated test proving the genuine-engagement gate (evidence written only when real signal exists, never on bare completion), full regression run, `tsc`/build clean, live walkthrough including an actual completion verified against live data.

## Demo Checklist

Open a Project → see real target skills/careers → complete it with a real reflection → see confirmation → check the student's evidence graph shows a real new entry citing the right skill → confirm a second, empty-effort completion attempt is honestly rejected or produces no evidence.

## Risks

- **Evidence-model coupling:** touching `EvidenceRecord` (a shared, multi-consumer model) is higher-blast-radius than anything Sprint 1/2 touched. Mitigated by the field being purely additive/nullable and the literal addition being backward-compatible (existing values unaffected).
- **Duplication risk:** explicitly addressed in the Design Checkpoint above — mitigated by a structurally distinct evidence shape and reuse of the existing shared writer.
- **Scope pull toward a Skill-evidence-tier UI:** real and tempting once the data exists. Mitigated by explicit exclusion above.

## Rollback Strategy

`projects` table: new, droppable with zero impact. `EvidenceRecord.related_skill`: nullable, ignorable, droppable. `"project"` source literal: additive, no existing record needs it. `StudentProfile.project_attempts`: new list field, defaults empty, droppable. Frontend: new routes plus one new Career-page section, revertible independently.

## Definition of Done

All Task Checklist items complete, all Acceptance Criteria met (including the genuine-engagement gate proven both ways — evidence written when it should be, withheld when it shouldn't), all Testing/Demo Checklist items pass live, zero regressions, tracker updated, release summary written, working tree clean, committed.
