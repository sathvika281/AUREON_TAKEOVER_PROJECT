-- V12: Authentication, User Identity & Investigation History — additive
-- persisted records for GitHub Intelligence and Document Intelligence
-- (previously left only Evidence/Notebook trails), so both become
-- genuinely reopenable from Investigation History.

alter table student_profiles
    add column if not exists github_investigations jsonb not null default '[]',
    add column if not exists document_investigations jsonb not null default '[]';
