-- Career Exploration History — observational interaction log (opened,
-- bookmarked, revisited, etc.), deliberately separate from evidence_graph
-- and career_candidates. Additive only.

alter table student_profiles
    add column if not exists career_exploration_history jsonb not null default '[]';
