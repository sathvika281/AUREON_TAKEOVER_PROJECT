-- Explore Batch 1: Career Explorer upgrade, College Explorer + Entrance
-- Hub merge, Global Trends, Exposure Universe. Opportunity Equality
-- needs zero schema changes — it reuses Opportunity Hub's existing
-- `opportunities` table/scoring wholesale (see the approved plan's
-- Decisions Log). All additive; safe to run alongside every prior
-- migration.

-- Career Explorer upgrade — new, nullable-defaulted columns.
alter table careers
    add column if not exists description text not null default '',
    add column if not exists why_people_love_it text not null default '',
    add column if not exists branches jsonb not null default '[]',
    add column if not exists curiosity_hook text;

-- College Explorer upgrade — merged Entrance Hub content.
alter table institutions
    add column if not exists campus_life_and_culture text not null default '',
    add column if not exists fees_summary text not null default '',
    add column if not exists scholarships_summary text not null default '';

-- Entrance exams are a genuinely independent entity (accepted by many
-- institutions) — a denormalized accepted_institution_ids array avoids
-- a second join table for a relationship this simple at this catalog size.
create table if not exists entrance_exams (
    id text primary key,
    name text not null,
    description text not null,
    eligibility jsonb not null default '[]',
    preparation_guidance text not null,
    typical_timeline text not null,
    accepted_institution_ids jsonb not null default '[]',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Global Trends — industry/market-level, deliberately distinct from any
-- single career's own FutureLens narrative (which stays a jsonb column
-- on `careers`, unchanged).
create table if not exists trends (
    id text primary key,
    title text not null,
    category text not null,
    summary text not null,
    description text not null,
    affected_industries jsonb not null default '[]',
    affected_skills jsonb not null default '[]',
    regions jsonb not null default '[]',
    time_horizon text not null,
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists trends_category_idx on trends(category);

-- Exposure Universe's own suggestion log — a brand-new top-level
-- StudentProfile field, never nested inside the frozen
-- discovery_onboarding column.
alter table student_profiles
    add column if not exists exposure_history jsonb not null default '[]';
