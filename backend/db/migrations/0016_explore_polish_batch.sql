-- Explore Polish Batch: deepens Career Explorer, College Explorer, and
-- Global Trends with real, additive fields. No new tables — every
-- addition is a jsonb/text column on an existing table. Opportunity
-- Equality's new categories need no schema change (category is a
-- free-text column, the Literal is enforced only at the Pydantic layer).

alter table careers
    add column if not exists day_in_the_life text not null default '',
    add column if not exists weekly_routine text not null default '',
    add column if not exists daily_tools jsonb not null default '[]',
    add column if not exists career_progression jsonb not null default '[]',
    add column if not exists related_industries jsonb not null default '[]',
    add column if not exists research_areas jsonb not null default '[]',
    add column if not exists companies jsonb not null default '[]',
    add column if not exists universities jsonb not null default '[]',
    add column if not exists scholarships jsonb not null default '[]',
    add column if not exists competitions jsonb not null default '[]',
    add column if not exists books jsonb not null default '[]',
    add column if not exists communities jsonb not null default '[]',
    add column if not exists open_source_projects jsonb not null default '[]',
    add column if not exists certifications jsonb not null default '[]',
    add column if not exists projects jsonb not null default '[]',
    add column if not exists videos jsonb not null default '[]',
    add column if not exists common_misconceptions jsonb not null default '[]',
    add column if not exists faqs jsonb not null default '[]',
    add column if not exists adjacent_careers jsonb not null default '[]';

alter table institutions
    add column if not exists hostels jsonb not null default '[]',
    add column if not exists exchange_programs jsonb not null default '[]',
    add column if not exists campus_facilities jsonb not null default '[]',
    add column if not exists student_reviews jsonb not null default '[]';

alter table trends
    add column if not exists key_milestones jsonb not null default '[]',
    add column if not exists countries_leading jsonb not null default '[]',
    add column if not exists affected_careers jsonb not null default '[]',
    add column if not exists research_papers jsonb not null default '[]',
    add column if not exists companies jsonb not null default '[]',
    add column if not exists startups jsonb not null default '[]',
    add column if not exists government_initiatives jsonb not null default '[]',
    add column if not exists risks jsonb not null default '[]',
    add column if not exists opportunities jsonb not null default '[]';
