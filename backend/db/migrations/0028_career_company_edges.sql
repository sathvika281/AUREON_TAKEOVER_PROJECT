-- Sprint 2 — Career's Company promotion (docs/SPRINT_2.md). The existing
-- top-level `companies` free-text list is left completely untouched —
-- this adds a new, separate column pointing at real companies.id rows,
-- same pattern already proven for required_skill_ids in Sprint 1.

alter table careers add column if not exists company_ids jsonb not null default '[]';
