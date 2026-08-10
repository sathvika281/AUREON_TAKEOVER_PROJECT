-- Sprint 3 — Project as a first-class entity (see docs/AUREON_DATA_ARCHITECTURE.md
-- §4 and docs/SPRINT_3.md). Purely additive: a new table, nothing existing
-- is touched here. Unlike companies/skills, Project isn't promoted from an
-- existing Career field — it carries its own outgoing edges, stored as jsonb
-- arrays, same "don't over-normalize a small, single-purpose list" convention
-- every other catalog model in this codebase already uses.

create table if not exists projects (
    id text primary key,
    title text not null,
    brief text not null,
    difficulty_level text not null,
    estimated_hours numeric not null,
    target_skill_ids jsonb not null default '[]',
    related_career_ids jsonb not null default '[]',
    related_company_ids jsonb not null default '[]',
    submission_type text not null default 'reflection_only',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists projects_title_idx on projects (title);
create index if not exists projects_difficulty_idx on projects (difficulty_level);
