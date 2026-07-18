-- Discover Batch 4: Missing Worlds + Life Missions. Both are real,
-- seeded knowledge bases (same normalized-rows shape as
-- trends/experiments). Classification/resonance analysis is computed
-- fresh on every read from already-persisted StudentProfile state — no
-- new per-student columns needed.

create table if not exists career_worlds (
    id text primary key,
    name text not null,
    description text not null,
    why_it_matters text not null,
    global_importance text not null,
    future_growth text not null,
    famous_careers jsonb not null default '[]',
    beginner_roadmap jsonb not null default '[]',
    required_skills jsonb not null default '[]',
    misconceptions jsonb not null default '[]',
    related_industries jsonb not null default '[]',
    videos jsonb not null default '[]',
    books jsonb not null default '[]',
    communities jsonb not null default '[]',
    beginner_projects jsonb not null default '[]',
    internships jsonb not null default '[]',
    colleges jsonb not null default '[]',
    companies jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists life_missions (
    id text primary key,
    name text not null,
    description text not null,
    famous_people jsonb not null default '[]',
    organizations jsonb not null default '[]',
    companies jsonb not null default '[]',
    nonprofits jsonb not null default '[]',
    books jsonb not null default '[]',
    documentaries jsonb not null default '[]',
    podcasts jsonb not null default '[]',
    communities jsonb not null default '[]',
    real_world_examples jsonb not null default '[]',
    suggested_careers jsonb not null default '[]',
    projects jsonb not null default '[]',
    volunteering_opportunities jsonb not null default '[]',
    research_areas jsonb not null default '[]',
    startup_ideas jsonb not null default '[]',
    related_tags jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
