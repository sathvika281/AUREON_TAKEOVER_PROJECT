-- Connect Batch 2: Knowledge Circles, Journey Stories, Mentorship.
-- Journey Stories extends the existing `career_stories` table (a
-- Journey Story IS a CareerStory — no parallel table). Knowledge
-- Circles and Mentorship are genuinely new schema, since neither has
-- any existing analog. Zero changes to `mentors` this batch —
-- `accepts_mentorship`/`max_students` already exist from Connect
-- Batch 1 and are simply read for the first time.

alter table career_stories
    add column if not exists timeline jsonb not null default '[]',
    add column if not exists career_switch boolean not null default false,
    add column if not exists gap_year boolean not null default false,
    add column if not exists uncertainty_period text not null default '',
    add column if not exists current_outcome text not null default '',
    add column if not exists industry text not null default '',
    add column if not exists linked_expert_id text,
    add column if not exists linked_life_mission_id text,
    add column if not exists story_type text not null default 'composite',
    add column if not exists source_reference text not null default '';

create table if not exists knowledge_circles (
    id text primary key,
    name text not null,
    overview text not null default '',
    what_this_field_is_about text not null default '',
    beginner_projects jsonb not null default '[]',
    advanced_projects jsonb not null default '[]',
    laboratories jsonb not null default '[]',
    startups jsonb not null default '[]',
    ngos jsonb not null default '[]',
    scholarships jsonb not null default '[]',
    linked_career_world_id text,
    linked_passion_domain_ids jsonb not null default '[]',
    related_career_industries jsonb not null default '[]',
    related_trend_ids jsonb not null default '[]',
    related_life_mission_ids jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create unique index if not exists knowledge_circles_name_idx on knowledge_circles (name);

create table if not exists mentorships (
    id text primary key,
    student_id text not null,
    expert_id text not null,
    review_token text not null,
    status text not null default 'requested',
    goals text not null default '',
    progress_notes jsonb not null default '[]',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create unique index if not exists mentorships_review_token_idx on mentorships (review_token);
create index if not exists mentorships_student_id_idx on mentorships (student_id);
create index if not exists mentorships_expert_id_idx on mentorships (expert_id);
