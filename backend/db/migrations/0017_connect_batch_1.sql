-- Connect Batch 1: Expert Connect + Parent Connect. Extends the existing
-- `mentors` table (an expert IS a Mentor — no new parallel Expert
-- table) and adds the genuinely new schema Parent Connect and Shared
-- (Joint) Sessions need, since neither has any existing analog.

alter table mentors
    add column if not exists profession text not null default '',
    add column if not exists specialization text not null default '',
    add column if not exists country text not null default '',
    add column if not exists city text not null default '',
    add column if not exists industries jsonb not null default '[]',
    add column if not exists education jsonb not null default '[]',
    add column if not exists "current_role" text not null default '',
    add column if not exists languages jsonb not null default '[]',
    add column if not exists photo_url text,
    add column if not exists accepts_mentorship boolean not null default false,
    add column if not exists max_students integer not null default 0,
    add column if not exists who_should_talk_to_me jsonb not null default '[]',
    add column if not exists career_ids jsonb not null default '[]',
    add column if not exists career_journey jsonb not null default '[]',
    add column if not exists day_in_the_life text not null default '',
    add column if not exists weekly_routine text not null default '',
    add column if not exists biggest_challenges jsonb not null default '[]',
    add column if not exists favourite_part text not null default '',
    add column if not exists biggest_misconceptions jsonb not null default '[]',
    add column if not exists what_surprised_them text not null default '',
    add column if not exists biggest_mistake text not null default '',
    add column if not exists one_regret text not null default '',
    add column if not exists salary_reality text not null default '',
    add column if not exists work_life_balance text not null default '',
    add column if not exists daily_skills jsonb not null default '[]',
    add column if not exists daily_tools jsonb not null default '[]',
    add column if not exists recommended_books jsonb not null default '[]',
    add column if not exists recommended_communities jsonb not null default '[]',
    add column if not exists advice_for_beginners text not null default '',
    add column if not exists advice_for_parents text not null default '',
    add column if not exists faqs jsonb not null default '[]',
    add column if not exists projects jsonb not null default '[]',
    add column if not exists research jsonb not null default '[]',
    add column if not exists certifications jsonb not null default '[]',
    add column if not exists conferences jsonb not null default '[]',
    add column if not exists organizations jsonb not null default '[]',
    add column if not exists volunteer_work jsonb not null default '[]',
    add column if not exists portfolio_links jsonb not null default '[]',
    add column if not exists social_links jsonb not null default '[]';

create table if not exists parent_career_guides (
    id text primary key,
    career_id text not null,
    common_misconceptions jsonb not null default '[]',
    earning_reality text not null default '',
    career_stability text not null default '',
    work_life_balance text not null default '',
    growth_opportunities text not null default '',
    educational_pathways jsonb not null default '[]',
    alternative_routes jsonb not null default '[]',
    global_demand text not null default '',
    risks jsonb not null default '[]',
    opportunities jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create unique index if not exists parent_career_guides_career_id_idx on parent_career_guides (career_id);

create table if not exists parent_questions (
    id text primary key,
    category text not null,
    career_id text,
    question text not null,
    expert_response text not null default '',
    responding_expert_id text,
    is_seeded boolean not null default true,
    created_at timestamptz not null default now()
);
create index if not exists parent_questions_category_idx on parent_questions (category);
create index if not exists parent_questions_career_id_idx on parent_questions (career_id);

create table if not exists shared_sessions (
    id text primary key,
    student_id text not null,
    mentor_id text not null,
    career_id text,
    access_token text not null,
    participant_label text not null default '',
    topic text not null default '',
    status text not null default 'invited',
    scheduled_slot timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create unique index if not exists shared_sessions_access_token_idx on shared_sessions (access_token);
create index if not exists shared_sessions_student_id_idx on shared_sessions (student_id);

create table if not exists shared_session_notes (
    id text primary key,
    session_id text not null,
    author_role text not null,
    note text not null,
    created_at timestamptz not null default now()
);
create index if not exists shared_session_notes_session_id_idx on shared_session_notes (session_id);
