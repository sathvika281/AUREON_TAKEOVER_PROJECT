-- Merge Experience Lab and Life Missions into one unified frontend feature.
-- Life Mission resonance already reads career_experiments via tag-substring
-- matching (life_mission_engine.py::_evidence_from_experiments) — that stays
-- as the generous, implicit evidence-matching path. This column is a
-- separate, deliberate editorial relationship: which experiences the catalog
-- author explicitly curated for a given mission, used to build the "Mission
-- Experiences" / "Your Emerging Missions" sections without relying on
-- accidental string overlap for UI grouping. Additive only — the 14 existing
-- experiments default to an empty list and are otherwise untouched.

alter table experiments
    add column if not exists related_life_mission_ids jsonb not null default '[]';
