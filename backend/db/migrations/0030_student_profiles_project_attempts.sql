-- Fixes a real gap from Sprint 3: `StudentProfile.project_attempts` was
-- added to the Python model, but no migration ever added the matching
-- column to the real `student_profiles` table — same column-per-field
-- upsert shape as career_experiments/circle_resource_progress, not a
-- jsonb-blob table. Without this column, every profile save (including
-- new student signup) fails with a PostgREST schema cache error.
-- Discovered during Sprint 3's live verification, same class of gap as
-- 0019_student_profiles_circle_resource_progress.sql.

alter table student_profiles
    add column if not exists project_attempts jsonb not null default '[]';
