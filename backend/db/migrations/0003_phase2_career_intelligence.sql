-- Phase 2: Explore Careers — Career Knowledge Base + persisted Career
-- Candidates. Careers/stories are normalized rows (unlike student_profiles'
-- jsonb-per-student blob) because they need to be searched, filtered, and
-- joined (by category/industry/country, career -> stories) rather than
-- read/written whole. Rich nested detail (reality, future_lens) stays
-- jsonb on the row since it's read/written whole per career.

create table if not exists careers (
    id text primary key,
    name text not null,
    category text not null,
    industry text not null,
    countries jsonb not null default '[]',
    one_liner text not null,
    trait_tags jsonb not null default '[]',
    reality jsonb not null default '{}',
    future_lens jsonb not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists career_stories (
    id text primary key,
    career_id text not null references careers(id),
    person_label text not null,
    background text not null,
    journey text not null,
    challenges text not null,
    turning_points text not null,
    advice text not null,
    lessons_learned text not null,
    trait_tags jsonb not null default '[]',
    created_at timestamptz not null default now()
);

create index if not exists career_stories_career_id_idx on career_stories(career_id);
create index if not exists careers_category_idx on careers(category);
create index if not exists careers_industry_idx on careers(industry);

alter table student_profiles
    add column if not exists career_candidates jsonb not null default '[]';
