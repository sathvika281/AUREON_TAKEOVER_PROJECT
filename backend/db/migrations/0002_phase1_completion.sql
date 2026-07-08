-- Aureon — Phase 1 production-completion
-- Run this once in the Supabase SQL Editor (Project > SQL Editor > New query).
-- Purely additive: two new jsonb columns on the existing student_profiles
-- table, safe to run without downtime or data loss. Existing rows get the
-- empty-array default.

alter table student_profiles
    add column if not exists notebook_entries jsonb not null default '[]';

alter table student_profiles
    add column if not exists evidence_graph jsonb not null default '[]';
