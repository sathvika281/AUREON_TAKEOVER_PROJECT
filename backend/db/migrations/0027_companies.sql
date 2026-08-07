-- Sprint 2 — Company as a first-class entity (see docs/AUREON_DATA_ARCHITECTURE.md
-- §5 and docs/SPRINT_2.md). Purely additive: a new table, nothing existing
-- is touched here. hiring_focus_areas stays a jsonb array rather than a
-- child table — same "don't over-normalize a small, single-purpose list"
-- convention every other catalog model in this codebase already uses.

create table if not exists companies (
    id text primary key,
    name text not null,
    organization_kind text not null,
    industry text not null,
    size_category text,
    what_they_do text not null,
    logo_url text,
    hiring_focus_areas jsonb not null default '[]',
    notable_for text not null default '',
    is_partner boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists companies_name_idx on companies (name);
create index if not exists companies_industry_idx on companies (industry);
