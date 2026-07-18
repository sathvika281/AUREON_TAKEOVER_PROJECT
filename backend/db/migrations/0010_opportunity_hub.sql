-- Aureon — Phase 2 Stage 2: Opportunity Hub
-- Run this once in the Supabase SQL Editor (Project > SQL Editor > New query).
-- Safe to re-run thanks to `if not exists`/`add column if not exists`.

create table if not exists opportunities (
    id text primary key,
    version integer not null default 1,
    title text not null,
    category text not null,
    organization text not null,
    organization_kind text not null,
    description text not null,
    eligibility jsonb not null default '[]',
    required_skills jsonb not null default '[]',
    preferred_skills jsonb not null default '[]',
    min_academic_level text not null default 'any',
    domain_tags jsonb not null default '[]',
    location text not null,
    is_remote boolean not null default false,
    countries jsonb not null default '[]',
    paid boolean not null default false,
    compensation_summary text,
    duration_label text not null,
    duration_weeks numeric,
    difficulty_level text not null default 'intermediate',
    estimated_competitiveness text not null default 'medium',
    application_deadline timestamptz,
    application_steps jsonb not null default '[]',
    timeline jsonb not null default '[]',
    benefits jsonb not null default '[]',
    official_link text not null,
    required_documents jsonb not null default '[]',
    source_note text not null default '',
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists opportunities_category_idx on opportunities(category);
create index if not exists opportunities_is_active_idx on opportunities(is_active);
create index if not exists opportunities_deadline_idx on opportunities(application_deadline);

-- Additive fix: no Stage 1 migration ever added `foundation_memory` to
-- student_profiles, so Career Memory (Evidence/Opportunities/Connections/
-- Growth) could not survive a real save() against Postgres until now.
-- Opportunity Hub is the first feature that actually depends on this
-- round-tripping, so it is fixed here rather than inherited silently.
alter table student_profiles
    add column if not exists foundation_memory jsonb not null default '{}'::jsonb;
