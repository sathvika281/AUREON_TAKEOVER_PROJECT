-- Aureon — Discovery Module tables
-- Run this once in the Supabase SQL Editor (Project > SQL Editor > New query).
-- No formal migration tool yet (Supabase CLI vs Alembic still undecided,
-- per docs/ARCHITECTURE.md) — this is the first hand-authored schema, safe
-- to re-run thanks to `if not exists`.

create table if not exists conversations (
    id text primary key,
    student_id text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists turns (
    id bigint generated always as identity primary key,
    conversation_id text not null references conversations(id) on delete cascade,
    role text not null,
    content text not null,
    agent_name text,
    created_at timestamptz not null default now()
);

create index if not exists turns_conversation_id_idx on turns (conversation_id);

-- One row per student. The nested Career DNA / hypotheses / journal /
-- history fields are stored as jsonb rather than normalized tables — they
-- are read and written as whole Pydantic-modeled objects on the backend
-- (see StudentProfileRepository), never queried piecemeal by SQL, so jsonb
-- keeps this simple without a premature normalization effort.
create table if not exists student_profiles (
    student_id text primary key,
    interests jsonb not null default '[]',
    strengths jsonb not null default '[]',
    "values" jsonb not null default '[]',
    goals jsonb not null default '[]',
    persona text,
    confidence_score double precision not null default 0,
    confidence_history jsonb not null default '[]',
    exploration_history jsonb not null default '[]',
    career_history jsonb not null default '[]',
    learning_progress jsonb not null default '{}',
    mentor_interactions jsonb not null default '[]',
    career_dna jsonb not null default '{}',
    career_hypotheses jsonb not null default '[]',
    reflection_journal jsonb not null default '[]',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- RLS intentionally left off: the backend talks to Supabase using the
-- secret (service-role-equivalent) key, which bypasses RLS by design.
-- Revisit if the frontend is ever given direct Supabase access.
