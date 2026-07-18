-- Discover Batch 5: Learning Style Discovery + Passion Incubator. Both
-- are real, seeded knowledge bases (same normalized-rows shape as
-- career_worlds/life_missions). Both analyses are computed fresh on
-- every read from already-persisted StudentProfile state — no new
-- per-student columns needed.

create table if not exists learning_styles (
    id text primary key,
    name text not null,
    description text not null,
    strengths jsonb not null default '[]',
    excels_in jsonb not null default '[]',
    common_struggles jsonb not null default '[]',
    study_strategies jsonb not null default '[]',
    note_taking_techniques jsonb not null default '[]',
    memory_strategies jsonb not null default '[]',
    active_learning_methods jsonb not null default '[]',
    project_ideas jsonb not null default '[]',
    practice_routines jsonb not null default '[]',
    collaboration_techniques jsonb not null default '[]',
    learning_environments jsonb not null default '[]',
    productivity_systems jsonb not null default '[]',
    recommended_books jsonb not null default '[]',
    research_backed_resources jsonb not null default '[]',
    online_courses jsonb not null default '[]',
    communities jsonb not null default '[]',
    ways_to_strengthen jsonb not null default '[]',
    keywords jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists passion_resource_domains (
    id text primary key,
    name text not null,
    keywords jsonb not null default '[]',
    books jsonb not null default '[]',
    documentaries jsonb not null default '[]',
    podcasts jsonb not null default '[]',
    youtube_channels jsonb not null default '[]',
    creators jsonb not null default '[]',
    communities jsonb not null default '[]',
    competitions jsonb not null default '[]',
    workshops jsonb not null default '[]',
    hackathons jsonb not null default '[]',
    research_organizations jsonb not null default '[]',
    museums_and_science_centers jsonb not null default '[]',
    exhibitions_and_conferences jsonb not null default '[]',
    journals_and_newsletters jsonb not null default '[]',
    learning_platforms jsonb not null default '[]',
    open_source_projects jsonb not null default '[]',
    challenge_platforms jsonb not null default '[]',
    source_note text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
