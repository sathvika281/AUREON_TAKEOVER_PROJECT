-- V11: Career Simulator & Decision Laboratory — additive
-- career_simulations history column on student_profiles, same pattern as
-- V10's career_investigations column.

alter table student_profiles
    add column if not exists career_simulations jsonb not null default '[]';
