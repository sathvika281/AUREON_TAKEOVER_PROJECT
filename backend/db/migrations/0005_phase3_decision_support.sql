-- Phase 3: Decide Confidently — Mentor + Institution Knowledge Bases,
-- plus additive Decision Support columns on student_profiles.

create table if not exists mentors (
    id text primary key,
    name text not null,
    role_type text not null,
    field text not null,
    bio text not null,
    trait_tags jsonb not null default '[]',
    learning_style_fit text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists institutions (
    id text primary key,
    name text not null,
    country text not null,
    city text not null,
    research_culture text not null,
    innovation_ecosystem text not null,
    industry_collaboration text not null,
    placements text not null,
    learning_environment text not null,
    trait_tags jsonb not null default '[]',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists research_labs (
    id text primary key,
    institution_id text not null references institutions(id),
    name text not null,
    focus_area text not null,
    description text not null
);

create table if not exists student_organizations (
    id text primary key,
    institution_id text not null references institutions(id),
    name text not null,
    focus_area text not null,
    description text not null
);

create table if not exists academic_programs (
    id text primary key,
    institution_id text not null references institutions(id),
    name text not null,
    degree_type text not null,
    field text not null,
    description text not null
);

create index if not exists research_labs_institution_id_idx on research_labs(institution_id);
create index if not exists student_organizations_institution_id_idx on student_organizations(institution_id);
create index if not exists academic_programs_institution_id_idx on academic_programs(institution_id);
create index if not exists mentors_role_type_idx on mentors(role_type);
create index if not exists institutions_country_idx on institutions(country);

alter table student_profiles
    add column if not exists career_comparisons jsonb not null default '[]',
    add column if not exists parallel_universe_scenarios jsonb not null default '[]',
    add column if not exists mentor_matches jsonb not null default '[]',
    add column if not exists college_matches jsonb not null default '[]',
    add column if not exists decision_memory jsonb not null default '[]';
