# Aureon — Product Flow

Aureon's guided journey has four real stages — **Discover → Explore →
Connect → Decide** — plus one deliberately ungated fifth destination, the
**Knowledge Base**, that sits outside the progression. This is a loop, not
a funnel: a student who reaches Decide and needs more evidence is routed
back to Explore or Connect, not left at a dead end. Source of truth for
every module named below: `frontend/src/features/navigation/journeyConfig.ts`.

See [`docs/diagrams/student-journey.svg`](./diagrams/student-journey.svg)
for the visual version of this document.

---

## Discover — "Who am I?"

**Purpose:** build a real, evidence-backed model of the student before
anyone — human or algorithm — proposes a direction.

**Actual functionality:**
- **Your Universe** (`/discover/identity`) — the conversational identity-
  discovery experience. Every exchange runs through the Discovery Agent
  (real Groq reasoning, one structured tool-call per turn), which extracts
  Career DNA trait updates, forms and revises career hypotheses, asks
  reflective "why" questions capped at depth 2 per topic, and surfaces a
  suggested activity grounded in a named evidence gap — never a generic
  "explore more."
- **Experience Lab** (`/discover/experience-lab`) — hands-on
  micro-experiments a student actually completes, plus "Your Emerging
  Missions," Life Mission resonance composed into the same screen.
- **Learning Style Discovery** (`/discover/learning-style-discovery`) —
  inferred from real interaction, not a stated preference form.
- **Reality Check** (`/discover/reality-check`) — an honest locked stub;
  the module explainer names what it will do (compare stated self-belief
  against observed evidence) without claiming it's live.

**Data produced:** `career_dna` (per-trait confidence scores),
`evidence_graph` entries, `career_hypotheses` (with a real lifecycle:
investigating → growing → strong → validated, or discarded),
`notebook_entries`, `reflection_journal`, and — from onboarding —
`world_signals` and `uncertainty_signals`.

**Feeds into:** Explore (career candidates reason over this same Career
DNA + Evidence Graph), Connect (mentor matching reads the same profile),
and Decide (every Decision Workspace card cites this evidence directly).

---

## Explore — "What's possible?"

**Purpose:** turn accumulated evidence into real, specific options —
grounded in data, never in aspiration alone — and deliberately widen what
a student has been exposed to before narrowing.

**Actual functionality:**
- **Career Explorer** (`/explore/career-reality`) — real career data
  (salary ranges, daily work, stress, automation risk, remote/travel
  realities) plus personalized candidates from `analyze_careers()`, the
  same reasoning function the conversational path uses.
- **College Explorer** (`/experience/college-collaboration`) — real
  institution matches.
- **Global Trends** (`/explore/global-trends`) — industry/skill-shift data,
  distinct from any one career's own outlook.
- **Exposure Universe** (`/explore/exposure-universe`) — composes the
  former Missing Worlds detection engine (what a student hasn't
  meaningfully explored) with open-ended possibility surfacing.
- **Opportunity Equality** (`/explore/opportunity-equality`) — real
  internships/scholarships/competitions, ranked by how unlikely a student
  would have been to find them unassisted, not by popularity.

**Data produced:** `career_candidates` (each with supporting/contradicting
evidence and a qualitative Evidence Strength label — never a raw
confidence number shown to the student).

**Feeds into:** Connect (a candidate career surfaces relevant experts),
Decide (candidates are the literal input to Decision Workspace cards).

---

## Knowledge Base — always open, never gated

**Purpose:** a plain, always-reachable reference layer — **Skills**,
**Companies**, **Projects** — deliberately *not* part of the guided,
evidence-gated progression above. Reached via nav or cross-links from
Career pages, with no personalization gate.

**Actual functionality:** browse/detail pages for all three entities,
each cross-linked to the Careers they relate to. **Projects** is the one
entity here that also writes back into the Evidence Graph — see
[`EVIDENCE_ENGINE.md`](./EVIDENCE_ENGINE.md).

**Data produced:** `project_attempts` and, when a submission shows genuine
engagement, real `EvidenceRecord`s tagged by skill.

---

## Connect — "Who can guide me?"

**Purpose:** no career decision this consequential should be made without
real human context.

**Actual functionality:**
- **Expert Connect** (`/experience/expert-connect`) — one destination with
  three real tabs: Find Experts (matched against Career DNA), My Mentors
  (request → pending → accepted lifecycle via a review token), and Parent
  Connect.
- **Student Stories** (`/experience/journey-stories`, titled "Student
  Stories" in the UI) — relatable discovery narratives from students and
  young people, distinct in purpose from Expert Connect's professional
  journeys; personalized ordering via `personalize_stories()` against real
  World Signals.
- **Knowledge Circles** (`/experience/knowledge-circles`) — peer
  communities structured around career worlds and a shared topic resource
  catalog.

**Data produced:** mentorship request/acceptance records, joint-session
tokens, knowledge-circle membership and resource-progress state.

**Feeds into:** Decide (relevant people surfaced on a Decision Workspace
card come from here).

---

## Decide — "What does the evidence say?"

**Purpose:** convergence, with a strict design discipline — Decide
introduces **no new intelligence**. Every number and every label here is
composed from what Discover, Explore, and Connect already produced.

**Actual functionality — Decision Lab** (`/decide/decision-lab`):
- **Decision Workspace** — one card per real career candidate: an
  overview, a Reality Check pulled from Explore's own data, a "why this
  fits" explanation that includes reasons *against*, relevant strengths,
  relevant people, and a concrete next step.
- **Career Comparison** — careers placed side by side across real
  dimensions, including several genuinely personal ones (interest
  alignment, Career DNA alignment, learning-style alignment) computed from
  the student's own evidence, not a generic rubric.
- **Future Simulation** — a forward-looking view composed from the same
  underlying data.

Two numbers appear on every card and are kept deliberately separate:
**Decision Confidence** ("does this fit, based on the evidence" — an
honest band, never a manufactured score) and **Decision Progress** ("have
you actually done the work to know" — a plain, itemized checklist).

**Data produced:** `decision_memory` — an append-only log of what was
compared, shortlisted, or removed, and why.

**Loops back to:** Explore/Connect, whenever the evidence on hand is
genuinely too thin for a confident decision — the product says so rather
than manufacturing false confidence.
