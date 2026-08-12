# Aureon — Knowledge Graph

Aureon connects a real, growing set of entities — but not every entity
touches every other one, and this document only claims the edges actually
confirmed in the domain models and repositories. See
[`docs/diagrams/knowledge-graph.svg`](./diagrams/knowledge-graph.svg) for
the visual version.

## Why this matters

A student's understanding of a career shouldn't stop at a job title. The
same Career row connects outward to the skills it actually requires, the
companies that actually hire for it, the projects that let a student
demonstrate readiness for it, and the real people who've walked it — so a
student exploring "what is this career, really" gets a connected answer,
not an isolated one.

## Entities and confirmed relationships

### Student ↔ Career
`StudentProfile.career_candidates` (from Career Intelligence's
`analyze_careers()`) and `evidence_graph[].related_career` — a student's
relationship to a career is always evidence-backed, never a static
bookmark.

### Career ↔ Skill
`Career.required_skill_ids` — a real, typed `jsonb` array of `Skill` ids
(promoted from a free-text field in Sprint 1). `Skill.parent_skill_id` is
the one edge in this graph with a real database foreign key.

### Career ↔ Company
`Career.company_ids` — real `Company` ids (promoted from a free-text
field in Sprint 2), reused `OrganizationKind` from the existing
`Opportunity` model rather than a parallel taxonomy.

### Career ↔ Project
`Project.related_career_ids` — Project carries its own outgoing edges
(it's a new entity, not a promotion), resolved in reverse on the Career
detail page.

### Project ↔ Skill
`Project.target_skill_ids` — completing a Project with genuine content
writes real `EvidenceRecord`s tagged `related_skill` for each target
skill. See [`EVIDENCE_ENGINE.md`](./EVIDENCE_ENGINE.md).

### Project ↔ Company (optional)
`Project.related_company_ids`.

### Career ↔ CareerStory
`career_stories.career_id` — illustrative composite professional
journeys, tagged by role/experience (e.g. "Data Scientist, 6 years
experience"), never presented as real named individuals.

### Mentor ↔ Career
`Mentor.career_ids` — real experts are linked to the careers they can
speak to, which is how Expert Connect's Career-DNA-aligned matching works.

### Student ↔ Mentor
A real request → pending → accepted lifecycle (via a review token an
expert acts on), surfaced in Expert Connect's "My Mentors" tab.

### Knowledge Circle ↔ Topic Resource Domain
Each circle links to a shared, topic-keyed resource catalog
(`linked_topic_domain_ids`) composed alongside Career/Trend/CareerWorld
resources into the circle's own resource list.

### Student Story ↔ World Signal
`CareerStory.trait_tags` for Student Discovery stories are topic/world
words (Space, AI, Healthcare, ...), matched against a student's real
`world_signals` via `personalize_stories()` — a deliberately *different*
matching contract than Career/Mentor/Institution's own `trait_tags`
field, which matches against Career DNA trait names instead. (Confirmed
by tracing each field's actual consumer — see
[`DECISIONS.md`](./DECISIONS.md).)

### Institution ↔ Student
Matched via Career DNA trait-tag alignment — not a direct edge to a
specific `Career` row.

### Trend ↔ Career
The Career detail route resolves Trend context alongside Skill/Company/
Project — industry-shift data attached to a career's real profile, not a
separate unconnected catalog.

## A relationship that deliberately does *not* exist yet

**Opportunity ↔ Skill.** `Opportunity.required_skills`/`preferred_skills`
remain free text, not linked to the real `Skill` catalog. A real audit
checked this directly: **0 of 33** distinct skill strings used across all
seeded Opportunities match any Skill catalog entry — the two vocabularies
are genuinely different in kind (broad conceptual categories vs. granular
tool/technology names), not just inconsistently spelled. Promoting this
edge would require expanding the Skill catalog first; documented as a
real, open gap in
[`TECHNICAL_DEBT_REGISTER.md`](./TECHNICAL_DEBT_REGISTER.md#12) rather
than a connection this document should claim.

## How edges are stored

Every cross-entity edge listed above (except `Skill.parent_skill_id`) is
a typed `jsonb` array of ids — validated at write time by the seed/backfill
scripts, but not enforced by a database foreign key. At the current
catalog scale (27 careers, 23 skills, 31 companies, 20 projects — see the
root [`README.md`](../README.md) for the full current dataset), this is a
deliberate, documented trade-off, not an oversight; the reasoning and the
real trigger for revisiting it live in the Technical Debt Register.
