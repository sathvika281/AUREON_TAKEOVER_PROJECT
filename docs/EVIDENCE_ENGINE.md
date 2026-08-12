# Aureon — Evidence Engine

Aureon's central discipline is that nothing is claimed about a student
that isn't backed by something they actually did or said. This document
covers the Project → Evidence pathway specifically — the clearest,
most demoable instance of that discipline — grounded in
`domain/services/project.py` and `domain/models/evidence.py`. See
[`docs/diagrams/evidence-loop.svg`](./diagrams/evidence-loop.svg) for the
visual version.

## The flow

```
Career exploration → Project (real, attemptable brief) → Attempt submitted
    → genuine-engagement gate → Evidence written (if real) / withheld (if empty)
    → Skill/Career signal in the Evidence Graph → read by Career Explorer, Decision Lab
```

## What "genuine engagement" actually means

`POST /v1/students/{student_id}/projects/{project_id}/complete` accepts
`artifact_url: str | None` and `reflection: str`. The completion is
**always** recorded — an attempt is an honest fact, whether or not it
produced anything — but `EvidenceRecord`s (one per `target_skill_id`,
tagged `source="project"`, `related_skill=<id>`) are written **only** if
at least one of `artifact_url` or `reflection` is real, non-whitespace
content.

This gate is deliberately **stricter** than the parallel Experience Lab
completion flow. Experience Lab's `complete_experiment()` always writes
at least one evidence string, falling back to `f"Completed '{title}'"`
when nothing else was reported — because Experience Lab answers "did the
student explore this," where even an undescribed completion is a real,
weak signal about interest. Project answers a different question — "did
the student demonstrate this" — and a capability claim can't rest on
"they clicked a button." So Project's gate withholds evidence entirely on
an empty submission, live-verified both ways:

- A real submission (artifact URL and/or a genuine reflection) writes
  exactly one `EvidenceRecord` per target skill.
- An empty submission records the attempt but writes zero evidence — the
  attempt is honestly logged, but nothing is claimed about the student's
  capability from it.

## What is stored

- `StudentProfile.project_attempts` — every attempt, including empty ones,
  with a timestamp and whatever content was actually submitted.
- `StudentProfile.evidence_graph` — the single source of truth for all
  evidence in the product, of every kind (conversation, reflection,
  document, project, experiment, search). Project-sourced records carry
  `source="project"` and a real `related_skill` id — a dimension no other
  evidence source in the product writes, extending the graph rather than
  duplicating it.

## Repeated attempts

A student can attempt the same project more than once. Each attempt is
recorded independently in `project_attempts`; each one that shows genuine
engagement writes its own evidence. Nothing is deduplicated away or
silently overwritten — a second, better attempt adds evidence, it doesn't
erase the record of the first.

## What this deliberately does not claim

**No automated evaluation of attempt quality or correctness.** The gate
checks for the *presence* of real content (a URL, a non-trivial written
reflection) — it does not grade the artifact, verify the link resolves to
genuine work, or assess whether the reflection is insightful. This is an
honest boundary, not a hidden limitation: Aureon records that a student
did real work and describes it, and lets that description speak for
itself elsewhere in the product (e.g. on a Decision Workspace card), never
manufacturing a skill-proficiency score from it.

**No World Signal reinforcement from Project completion.** Unlike
Experience Lab, completing a Project never touches `world_signals` —
Project's edge is to Skills/Careers/Companies, not to one of the
onboarding Worlds; conflating the two would blur "does this look like
demonstrated capability" with "does this look like curiosity," which is
exactly the distinction this whole system exists to keep separate. See
[`DECISIONS.md`](./DECISIONS.md) for the full reasoning.
