-- V13: Career Exploration Ecosystem — College Collaboration + Expert
-- Connect. Schema only; seed data (incl. NIAT) lives in the existing
-- seed_mentors_institutions.py script, same pattern already established
-- for the rest of the Institution/Mentor Knowledge Base.

alter table institutions
    add column if not exists is_partner boolean not null default false;

alter table mentors
    add column if not exists organization text not null default '',
    add column if not exists years_experience integer not null default 0,
    add column if not exists journey_highlights jsonb not null default '[]',
    add column if not exists discussion_topics jsonb not null default '[]';

create table if not exists innovation_centers (
    id text primary key,
    institution_id text not null references institutions(id),
    name text not null,
    focus_area text not null,
    description text not null
);

create table if not exists faculty_highlights (
    id text primary key,
    institution_id text not null references institutions(id),
    name text not null,
    title text not null,
    expertise_area text not null,
    bio text not null
);

create table if not exists student_ambassadors (
    id text primary key,
    institution_id text not null references institutions(id),
    student_label text not null,
    program text not null,
    message text not null
);

create table if not exists student_projects (
    id text primary key,
    institution_id text not null references institutions(id),
    student_label text not null,
    project_title text not null,
    description text not null,
    skills_used jsonb not null default '[]'
);

create table if not exists internship_opportunities (
    id text primary key,
    institution_id text not null references institutions(id),
    title text not null,
    field text not null,
    description text not null
);

create table if not exists career_events (
    id text primary key,
    title text not null,
    event_type text not null,
    institution_id text references institutions(id),
    mentor_id text references mentors(id),
    description text not null,
    scheduled_at timestamptz not null default now()
);

create index if not exists innovation_centers_institution_id_idx on innovation_centers(institution_id);
create index if not exists faculty_highlights_institution_id_idx on faculty_highlights(institution_id);
create index if not exists student_ambassadors_institution_id_idx on student_ambassadors(institution_id);
create index if not exists student_projects_institution_id_idx on student_projects(institution_id);
create index if not exists internship_opportunities_institution_id_idx on internship_opportunities(institution_id);
create index if not exists career_events_institution_id_idx on career_events(institution_id);
create index if not exists career_events_mentor_id_idx on career_events(mentor_id);

alter table student_profiles
    add column if not exists expert_session_bookings jsonb not null default '[]',
    add column if not exists guidance_requests jsonb not null default '[]',
    add column if not exists event_registrations jsonb not null default '[]',
    add column if not exists saved_experts jsonb not null default '[]';
