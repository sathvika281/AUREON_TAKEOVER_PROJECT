-- Sprint 1 — Career's Skill promotion (docs/SPRINT_1.md). The existing
-- reality.required_skills free-text list (nested inside the `reality`
-- jsonb column) is left completely untouched — this adds a new,
-- separate top-level column pointing at real skills.id rows, proving
-- the promotion pattern on one entity before it's repeated elsewhere.

alter table careers add column if not exists required_skill_ids jsonb not null default '[]';
