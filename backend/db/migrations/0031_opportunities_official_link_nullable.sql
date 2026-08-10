-- Sprint 4 — Data Quality. `opportunities.official_link` was `not null`,
-- but every one of the 40 seeded rows carried a fake `example.org`
-- placeholder (there is no real listing to link to for an illustrative
-- composite posting). A fabricated URL is worse than an honest absence
-- — see domain/models/opportunity.py's own comment on this field.
-- Purely additive: loosens a constraint, drops nothing, alters no other
-- column. The 40 existing rows get their fake links nulled out
-- separately (a data fix, not part of this migration).

alter table opportunities alter column official_link drop not null;
