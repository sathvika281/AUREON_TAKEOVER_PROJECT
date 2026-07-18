-- Separate Expert Career Journeys (Expert Connect, using Mentor.career_journey
-- exclusively) from Student Journey Stories (this table, redefined to focus
-- on student discovery narratives). No existing rows are modified by this
-- migration — the 150 existing career_stories rows keep story_type='composite'
-- and continue serving Career Explorer's "Human Stories" section unchanged.
--
-- discovery_themes backs real, honest filters on the redefined standalone
-- Journey Stories screen (e.g. "Found My Passion", "Parent Expectations",
-- "Non-Traditional Path") — populated only on new story_type=
-- 'composite_student_discovery' rows going forward; existing rows default to
-- an empty list, matching "do not create empty filters" (nothing queries
-- this column for old rows).

alter table career_stories
    add column if not exists discovery_themes jsonb not null default '[]';
