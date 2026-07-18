-- Discover Batch 2: Career Experiments + Talent Discovery Lab. Talent
-- Discovery Lab needs zero schema changes — it's a pure, stateless
-- function recomputed on every read from already-persisted state (see
-- the approved plan's Decisions Log). All additive; safe to run
-- alongside every prior migration.

-- Career Experiments catalog — real, seeded, structured content, same
-- normalized-rows shape as `trends`.
create table if not exists experiments (
    id text primary key,
    title text not null,
    category text not null,
    description text not null,
    instructions text not null,
    estimated_minutes integer not null,
    age_appropriate_note text not null default '',
    related_world text not null,
    target_traits jsonb not null default '[]',
    reflection_prompt text not null,
    source_note text not null default '',
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Student Experiment History — a brand-new top-level StudentProfile
-- field, never nested inside the frozen discovery_onboarding column.
alter table student_profiles
    add column if not exists career_experiments jsonb not null default '[]';
