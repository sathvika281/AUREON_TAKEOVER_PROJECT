-- V10: Multi-Source Search Intelligence — additive Career Investigations
-- history column on student_profiles, same pattern as Phase 3's
-- career_comparisons/decision_memory columns.

alter table student_profiles
    add column if not exists career_investigations jsonb not null default '[]';
