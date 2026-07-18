-- Discover Batch 1 backend migration: adaptive onboarding, World
-- Signals, Uncertainty Signals. New top-level StudentProfile field
-- (see domain/models/discovery_onboarding.py) — the student_profiles
-- table stores one jsonb column per top-level field (see migration
-- 0001), so a new top-level field needs a migration; everything nested
-- inside this column (world_signals, uncertainty_signals, ...) is
-- schema-less and needs none.
alter table student_profiles
    add column if not exists discovery_onboarding jsonb not null default '{}'::jsonb;
