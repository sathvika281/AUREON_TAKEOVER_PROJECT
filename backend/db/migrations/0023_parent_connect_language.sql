-- Connect restructuring — genuine multilingual support for Parent Connect
-- (moved inside Expert Connect). English-only rows already in these
-- tables default to language='en' and are completely unaffected.
-- Hindi/Telugu rows are added as new sibling rows (new ids, same
-- career_id/category) by scripts/translate_parent_connect_content.py,
-- never by mutating existing English rows in place.

alter table parent_career_guides
    add column if not exists language text not null default 'en';

alter table parent_questions
    add column if not exists language text not null default 'en';
