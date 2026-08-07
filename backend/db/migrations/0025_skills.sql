-- Sprint 1 — Skill as a first-class entity (see docs/AUREON_DATA_ARCHITECTURE.md
-- §3 and docs/SPRINT_1.md). Purely additive: a new table, nothing existing
-- is touched here. related_skill_ids/evidence_types_that_count stay jsonb
-- arrays rather than child tables — same "don't over-normalize a small,
-- single-purpose list" reasoning every other catalog model in this codebase
-- already uses (see e.g. opportunities.eligibility, trends.risks).

create table if not exists skills (
    id text primary key,
    name text not null,
    category text not null,
    description text not null,
    parent_skill_id text references skills (id),
    related_skill_ids jsonb not null default '[]',
    evidence_types_that_count jsonb not null default '[]',
    is_canonical boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Canonical/alias merge story starts honest from day one — no two
-- canonical skills may share a display name (aliases are handled via
-- is_canonical=false + a distinct name, never a duplicate canonical row).
create unique index if not exists skills_name_idx on skills (name);
create index if not exists skills_category_idx on skills (category);
