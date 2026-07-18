-- Fixes a real gap from Connect Batch 2: `StudentProfile.circle_resource_progress`
-- was added to the Python model, but no migration ever added the matching
-- column to the real `student_profiles` table (that batch's own summary
-- incorrectly assumed jsonb-blob storage; `student_profile_repository.py`
-- actually does a column-per-field upsert against this wide table, same
-- as every other list field here). Without this column, every profile
-- save (including new student signup) fails with a PostgREST schema
-- cache error. Discovered and fixed during Decide Batch 1 verification.

alter table student_profiles
    add column if not exists circle_resource_progress jsonb not null default '[]';
