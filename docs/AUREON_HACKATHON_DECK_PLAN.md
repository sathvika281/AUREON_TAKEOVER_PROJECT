# Aureon — Hackathon Deck: Final Content & Design Plan

**Status:** Ready to build in PowerPoint/Keynote/Figma. This document is the single source of truth for both content and visual direction — every color, feature, and technical claim below was verified directly against the live codebase (see "Verification basis" at the end), not invented or assumed.

No hackathon guidelines PDF was found in the repo or attached to this conversation — per explicit confirmation, this document itself is the complete spec (17 slides, all required sections below).

---

## 0. Design System — the one true palette (verified in `frontend/tailwind.config.ts` + `Logo.tsx`)

Every slide must be built from these exact tokens. Do not introduce any other color.

| Role | Token | Hex / value | Use for |
|---|---|---|---|
| Canvas | `canvas` | `#070B18` | Slide background, every slide, no exceptions |
| Surface | `surface.raised` | `#0A0817` | Cards, panels — barely distinguishable from canvas |
| Border | `border` / `border-strong` | `#2A2650` / `#3A3560` | Hairline card/panel edges only — never a heavy rule |
| Primary text | `ink` | `#F2EDE0` (warm moonlight white) | Headlines, primary copy |
| Secondary text | `ink-muted` | `rgba(242,237,224,0.6)` | Subheads, body copy |
| Faint text | `ink-faint` | `rgba(242,237,224,0.32)` | Captions, eyebrows, timestamps |
| **Accent (the one true interactive color)** | `accent` / `accent-soft` | `#8B8FD9` / `#AEB2E8` | Links, active states, icons, diagram highlights, the "e" in the wordmark |
| Gold (rare — achievement only) | `gold` / `gold-soft` | `#D9B87A` / `#E9C98F` | Evidence markers, milestone/impact numbers only |
| Success (status only) | `success` | `#3D6B54` / `#7FB096` | "Live," "shipped," checkmarks on the current-state slides |
| Danger (errors only) | `danger` | `#C47A63` | Used sparingly, e.g. "what traditional approaches miss" |
| Atmosphere glows | indigo/violet/cyan | `rgba(76,66,168,.07)` / `rgba(130,96,176,.05)` / `rgba(96,180,196,.045)` | Extremely subtle radial gradient behind hero slides only (1, 17) — never a visible "glow effect," just a whisper of depth |

**Typography:** Sans body/UI face — `-apple-system, "SF Pro Display", "Segoe UI", Inter, system-ui`. A serif accent face — `"Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia` — reserved for exactly one thing in this deck: the two memorable pull-quotes (Slide 2 closing line, Slide 17 central statement), matching how the app itself reserves serif for "narrative/reflection moments only." Everything else stays sans.

**Logo:** Use the real Aureon mark — a thin open ring (career discovery is never fully complete), four compass ticks with open-ended arrows (guidance, not prescription), four small scattered accent dots (gathered evidence), a single curved accent-soft path breaking upward (understanding before direction), and two overlapping accent "leaf" shapes over an ink-colored seed ellipse (hidden potential, growing). Wordmark: **Aur*e*on**, entirely `ink` colored except the "e," which is `accent-soft`. Tagline directly under the wordmark, small caps, `ink-faint`, wide letter-spacing: **EVIDENCE BEFORE DIRECTION**. This exact mark + wordmark + tagline lockup is the in-app `Logo` component (`size="lg" withTagline`) — reproduce it faithfully rather than redrawing a new logo.

**Surface language:** Cards and panels sit at `surface.raised`, distinguished from the canvas only by a 1px `border` hairline and, where a card needs to feel "lifted" (e.g. a feature highlight), a barely-perceptible shadow — never a drop-shadow, never a gradient border, never glassmorphism/blur. Corners: soft, moderate rounding (`rounded-lg`/`rounded-xl` equivalent, ~10–16px) consistent with the app's own card treatment — never fully pill-shaped except for small badges/pills (tier badges, category tags), matching how the app itself only pills small status chips.

**Motif discipline:** Universe/orbit/star imagery appears in exactly three places: the Slide-1 background, the Slide-5 four-stage diagram (framed as an orbit), and the Slide-17 closing visual. Everywhere else, the deck should look like clean, confident product/architecture slides — not a space-themed deck end to end. This mirrors the app itself, where the galaxy visual language is concentrated in "Your Universe" and used sparingly elsewhere.

---

## 1. Slide-by-Slide Plan

### Slide 1 — Aureon

**Exact on-slide text:**
> Aur*e*on
> EVIDENCE BEFORE DIRECTION
>
> Discover who you could become.

**Visual/layout:** Full-bleed `canvas` background. Centered composition, vertically centered. Large Aureon mark (the real SVG mark, ~120–160px equivalent) above the wordmark, exactly as the app's `Logo size="lg" withTagline"` renders it, just scaled up. Below a small gap, the one line "Discover who you could become." in `ink-muted`, sans, no serif. Extremely subtle atmosphere glow (indigo/violet radial, near-invisible) behind the mark only — nothing else on the slide. No navigation chrome, no feature list, no logos-of-tech-used. This slide has one job: presence.

**Screenshots:** None — this is a title slide built from the logo asset, not a screenshot.

**Diagram:** None.

**Speaker notes:** "Aureon — evidence before direction. Not a career test. A career intelligence platform that discovers who a student could become, one real piece of evidence at a time." (Say the name once, clearly, then move immediately to the problem — don't over-explain the tagline here, it lands on its own.)

**Time:** 20 sec

---

### Slide 2 — The Problem

**Exact on-slide text:**
> **Students are asked to choose their future before they've had the chance to discover it.**
>
> **Limited self-understanding** — asked what they want to become before they've had enough real experiences to know their strengths, interests, and motivations.
>
> **Limited exposure** — you cannot choose a career you've never encountered. Most students' career universe is bounded by family, school, and geography.
>
> **Decisions without evidence** — marks, social pressure, popular choices, one-time assessments. Rarely accumulated evidence from actual exploration.
>
> *You cannot choose a future you never knew existed.*

**Visual/layout:** `canvas` background. Headline top, large, `ink`. Three items laid out as three quiet vertical panels (`surface.raised`, hairline border), each with a short accent-colored eyebrow label ("01 Self-Understanding," "02 Exposure," "03 Evidence") — numbering is justified here because these genuinely are three distinct, ordered dimensions of one problem, not decoration. The closing line sits alone below the three panels, serif face, `ink-muted`, slightly larger than body text, with generous whitespace around it so it reads as a beat, not a footnote.

**Screenshots:** None.

**Diagram:** None — three panels are the visual structure.

**Speaker notes:** Walk through each of the three panels in one sentence each. Land hard on the closing line — this is one of the two ideas we want judges to remember. Pause after saying it.

**Time:** 45 sec

---

### Slide 3 — Why Current Career Guidance Isn't Enough

**Exact on-slide text:**
> A one-time test can capture a moment. Career discovery is a journey.
>
> **Traditional approach** (psychometric tests, aptitude quizzes, one-time career questionnaires, generic AI career chats)
> — One-time assessment
> — Self-reported answers only
> — A snapshot of the student
> — Recommends from a fixed, known set of careers
> — No continuity after the result
> — No visibility into what happens next
>
> **Aureon**
> — Continuous discovery, not a single event
> — Multiple forms of real evidence
> — An understanding that evolves
> — Exposure to careers the student didn't know existed
> — Built from real experiences and reflection
> — Persistent memory across every session
> — Explainable decision support, not a verdict

**Visual/layout:** Two-column comparison on `canvas`. Left column header "Traditional Approach" in `ink-muted` on a plain (no card) background — deliberately understated, not a competitor callout. Right column header "Aureon" in `accent-soft`, its six lines each preceded by a small `success`-colored checkmark to visually read as "what Aureon adds," not "what's wrong with the other approach." No product/company names anywhere on this slide — the comparison is by approach category only (psychometric tests, aptitude quizzes, career questionnaires, static recommendation systems, generic AI chat), never named competitors. Closing line as a single centered strip beneath both columns, serif, `ink-muted`.

**Screenshots:** None.

**Diagram:** Simple two-column table/list, as described.

**Speaker notes:** "We're not claiming these approaches are worthless — a psychometric test can capture something real about a moment. Our claim is narrower and, we think, more important: a snapshot can't capture a journey. That's the gap Aureon fills." Explicitly do NOT name any specific product on this slide even verbally, to stay consistent with the deck's own comparison scope.

**Time:** 45 sec

---

### Slide 4 — The Solution

**Exact on-slide text:**
> AUREON
> An AI-native Career Intelligence Platform
>
> Aureon transforms career guidance from a one-time recommendation into a continuous journey of discovery.
>
> It continuously learns from a student's exploration, experiences, reflections, interests, and patterns — helping them:
>
> Understand themselves → Discover possibilities beyond what they already know → Explore and experience those possibilities → Learn from experts and relatable journeys → Build evidence → Make more informed decisions
>
> *Instead of telling students what to become, Aureon helps them discover what they could become — and understand why a path may truly fit.*

**Visual/layout:** `canvas`. Small eyebrow "AUREON" in accent, small caps, tracked. Large headline "An AI-native Career Intelligence Platform," `ink`. Solution statement as a standalone sentence, slightly larger, `ink-muted`. The six-step flow rendered as a single horizontal chain of six short labels connected by thin accent arrows (`→`), wrapping to two rows if needed — this is the first "flow" motif in the deck and should feel calm, not busy: each label is just 2-3 words, connected by the same open-ended-arrow motif used in the logo's compass ticks (visual continuity with Slide 1). Closing line, serif, centered, generous whitespace, echoing the treatment on Slide 2's closer.

**Screenshots:** None.

**Diagram:** The six-step horizontal flow described above.

**Speaker notes:** This is the pivot slide from problem to product — say it with energy. "Aureon doesn't ask 'what do you want to be' on day one. It builds understanding the same way a person actually forms it: through real experience, over time."

**Time:** 40 sec

---

### Slide 5 — How Aureon Works

**Exact on-slide text:**
> DISCOVER → EXPLORE → CONNECT → DECIDE
>
> **Discover** — Who am I?
> **Explore** — What possibilities exist beyond what I already know?
> **Connect** — What can I learn from people who've lived these paths?
> **Decide** — What does the evidence actually tell me?
>
> Not four separate pages. One connected intelligence.
> Career DNA · Evidence Graph · Reflection Journal · Decision Memory

**Visual/layout:** The one slide in the deck allowed a real orbit motif. Four nodes arranged along a gentle open arc (echoing the logo's open outer ring — "career discovery is never truly complete"), connected by thin accent lines with the same open-arrow style as the logo's compass ticks. Each node is a small `surface.raised` circle/pill with the stage name in `ink` and its one-line question in `ink-muted` beneath it, outside the arc. Below the arc, a thin horizontal band in `accent-dim` (the rgba wash, not a hard color) containing the four memory-system names in `gold` (evidence/achievement color, appropriate here since these are what Aureon "has learned") — with a short connecting line from each memory label up into the arc, visually showing that all four stages draw from and feed the same underlying memory, rather than four disconnected systems.

**Screenshots:** None — this is the deck's one intentionally illustrative/diagrammatic slide.

**Diagram:** Four-stage arc + memory band, as described. This is the most important diagram in the deck to get right — it's the visual spine the next four slides hang off of.

**Speaker notes:** "These aren't four tabs in a nav bar. A reflection a student writes in Discover can change what Decision Lab tells them weeks later, because it's the same underlying memory the whole way through." Name-check that "Career Memory" here is our label for Aureon's Career DNA + World Signal system, "Reflection Memory" is the Reflection Journal, and "Decision Memory" is a real, separately-modeled append-only log of *why* each decision-lab conclusion was reached — not a marketing name, an actual persisted structure in the codebase.

**Time:** 50 sec

---

### Slide 6 — Discover

**Exact on-slide text:**
> DISCOVER
> "How can I choose a direction when I don't yet understand myself?"
>
> **Your Universe** — an ongoing conversation that builds a real, evolving picture of who the student is
> **Experience Lab** — small, real activities across careers and real-world missions; participation and reflection surface both career fit and what purpose genuinely resonates
> **Learning Style Discovery** — how the student actually learns best
>
> Interaction → Experience → Reflection → Evidence → Better self-understanding

**Visual/layout:** `canvas`. Stage label + question at top, same visual weight as it will have on Slides 7-9 (consistent header treatment across all four stage slides — same eyebrow position, same question-in-quotes styling, so judges recognize the pattern immediately). Three feature rows below as a simple list (not heavy cards — keep this scannable), each a bold feature name in `ink` followed by an em-dash and a `ink-muted` one-liner. Bottom strip: the five-step flow (Interaction → Experience → Reflection → Evidence → Better self-understanding) in the same small horizontal-chain style as Slide 4, `accent` arrows.

**Screenshots:** "Your Universe" main screen (the conversational identity-discovery view with Career DNA/confidence visible) — this is the single most important screenshot in the deck since it's the entry point to the whole product.

**Diagram:** The five-step flow strip only.

**Speaker notes:** Confirm live status explicitly if asked: three real, working Discover destinations exist today; a fourth ("Reality Check") is an honest locked placeholder and should not be claimed as live if a judge asks to see it. If pressed on Experience Lab specifically: it's a deliberate merge — Life Missions is no longer a separate destination, its resonance intelligence now lives inside Experience Lab as "Your Emerging Missions," paired with real mission-connected activities a student can actually try, alongside career-connected ones. Passion Incubator has been retired from the product and should not be mentioned as current.

**Time:** 35 sec

---

### Slide 7 — Explore

**Exact on-slide text:**
> EXPLORE
> "Students cannot choose possibilities they've never encountered."
>
> **Career Explorer** — real careers, real day-to-day realities, not just job titles
> **College Explorer** — institutions and programs matched to the student's actual profile
> **Exposure Universe** — a map of what the student has explored, and the "missing worlds" they haven't
> **Global Trends** — how industries and in-demand skills are actually shifting
> **Opportunity Equality** — real internships, scholarships, and programs, surfaced fairly
>
> Broaden before narrowing.

**Visual/layout:** Same header treatment as Slide 6. Five-row feature list, identical styling to Slide 6 for pattern consistency. Closing line "Broaden before narrowing." set apart, larger, `accent-soft`, no arrow/flow diagram needed here — this slide's idea is better carried by one strong sentence than another flow chart (avoids visual fatigue after Slides 4-6 each having a flow strip).

**Screenshots:** Exposure Universe's map/missing-worlds view — the most visually distinctive and conceptually load-bearing screen in this stage (it's the one that literally embodies "broaden before narrowing").

**Diagram:** None (deliberately — see layout note).

**Speaker notes:** "Aureon doesn't reduce a student to three recommended careers immediately. It expands what they know is possible first — Exposure Universe is where that's most visible: it shows a student not just what they've explored, but what real, relevant worlds they haven't even encountered yet."

**Time:** 35 sec

---

### Slide 8 — Connect

**Exact on-slide text:**
> CONNECT
> "Career information tells you what a career is. People help you understand what the journey actually feels like."
>
> **Expert Connect** — the one human-guidance hub: find experts, read their real career journeys, request one as a mentor, track mentorship status, and get parent-friendly guidance — all in one place
> ("How did someone already in this career get there?")
>
> **Student Stories** — relatable discovery stories from students and young people, not professionals
> ("How did someone like me navigate the confusion and find their direction?")
>
> **Knowledge Circles** — structured exploration around career worlds and resources

**Visual/layout:** Same header pattern. Expert Connect and Student Stories get their own two side-by-side highlighted mini-cards (the deck must clearly distinguish them — this is a deliberate purpose split, and that distinction deserves visual weight), each card literally posing its "question answered" in quotes underneath the feature name. Expert Connect's card gets a small internal row of its own — "Find Experts · Career Journeys · Request as Mentor · My Mentors · Parent Connect" in `ink-faint`, tiny — showing at a glance that these are now facets of one destination, not five separate ones. Knowledge Circles sits below as a single smaller supporting line, since it's the one remaining standalone supporting feature.

**Screenshots:** Expert Connect's expert-detail view showing a real Career Journey timeline (proves the "journey," not just a directory listing).

**Diagram:** The two-card side-by-side contrast for Expert Connect vs. Student Stories, with Knowledge Circles as a smaller third element beneath.

**Speaker notes:** Emphasize this distinction explicitly and confidently, since it's genuinely a considered product decision: "Expert Connect is about learning from someone who already made it — a professional's real journey, and now the mentorship relationship that can follow from it. Student Stories is about someone still figuring it out, like the student themselves." If asked why Mentorship and Parent Connect aren't separate destinations anymore: "They're not separate questions — they're both part of 'who can help guide me,' so we brought them into Expert Connect instead of fragmenting the journey across five different places." If pressed on current content depth for Student Stories, be honest that the feature and its data model are fully built; expanding its illustrative story catalog is ongoing content work, not a missing capability.

**Time:** 45 sec

---

### Slide 9 — Decide

**Exact on-slide text:**
> DECIDE
> "Career decisions are often made before students have enough evidence."
>
> Self-understanding + Exploration + Experiences + Reflections + Career Intelligence + Human Perspectives → Decision Lab
>
> Decision Lab helps answer:
> Why might this direction fit? · What evidence supports it? · What evidence contradicts it? · What uncertainty remains? · What should I explore next?
>
> Explainable, evidence-informed decision support — never a verdict.

**Visual/layout:** Same header pattern. Center of the slide: the six-input funnel-arrow into "Decision Lab," rendered as six small `ink-muted` labels converging via thin accent lines into one `surface.raised` "Decision Lab" node (this is the payoff of Slide 5's memory band — literally the same inputs converging). Below it, the five questions as a compact 2-3 row grid of small pill-shaped tags, `accent-dim` background, `ink` text — these should read as "the actual questions the product answers," not decorative. Closing line, `gold` (matches the "evidence marker" semantic), bold, standalone.

**Screenshots:** Decision Lab's career-comparison view showing reasons-for/reasons-against and a readiness/gap indicator for one career.

**Diagram:** The six-input convergence funnel described above.

**Speaker notes:** "This is deliberately not a black box that says 'you should become X.' It shows its work — what evidence supports a direction, what evidence complicates it, and exactly what's still missing before the student can be confident." This is a strong differentiator to linger on if there's time to spare.

**Time:** 45 sec

---

### Slide 10 — What Makes Aureon Different

**Exact on-slide text:**
> **Continuous, not one-time** — Aureon evolves as the student evolves.
> **Discovery, not just recommendation** — it expands possibilities before narrowing them.
> **Evidence, not just answers** — real experiences and reflections build understanding.
> **Memory, not isolated conversations** — context persists across every session.
> **Explainability, not black-box output** — the student can see why a direction is being considered.
> **Human + AI** — experts, mentors, parents, and relatable journeys complement AI intelligence.
>
> Not another career test. A career intelligence system that evolves with you.

**Visual/layout:** `canvas`. Six items as a clean 2×3 grid of short cards — no icons needed beyond a small accent dot per row, this slide should feel confident and unornamented, letting the words carry it (contrast intentionally with Slide 5's busier diagram — after four feature-heavy slides, this one should feel like a breath). Bold lead phrase per card in `ink`, rest in `ink-muted`. Closing line, larger, `accent-soft`, centered below the grid.

**Screenshots:** None.

**Diagram:** 2×3 grid, no connecting lines.

**Speaker notes:** This is the "why us" slide judges will remember most concretely after the problem/vision bookends — deliver each line with a beat of pause, don't rush the six.

**Time:** 40 sec

---

### Slide 11 — Why Aureon Is Not Just Another AI Chatbot

**Exact on-slide text:**
> A general chatbot: Question → Answer.
>
> Aureon: Student Context + History + Evidence + Career Intelligence + Specialized Reasoning → Context-aware guidance.
>
> Student → Career Orchestrator (LangGraph) → Specialized Career-Intelligence Agents → Tools + Real Career Data → Memory + Evidence → Reasoning → Personalized Response
>
> 12 specialized agents, coordinated by a real LangGraph orchestration graph — 7 currently LLM-reasoning-live today (Discovery, Career Intelligence, Decision, Mentor, Institution, Growth, Opportunity Matching).
>
> **CURRENT** — implemented and running · **FUTURE** — Phase 2/3 vision (see later slides)

**Visual/layout:** `canvas`. Top: the two-line "general chatbot vs. Aureon" contrast, small, understated, almost like a caption — sets up the real diagram below without stealing its thunder. Center: the seven-stage vertical/flow diagram (Student → Career Orchestrator → Specialized Agents → Tools + Data → Memory + Evidence → Reasoning → Response), each stage a small `surface.raised` node connected by thin accent arrows, flowing top to bottom or left to right depending on available space. The "12 agents / 7 live" line sits directly under the "Specialized Agents" node as its caption, in `ink-muted`, small. A small, clearly-labeled `CURRENT` / `FUTURE` legend key sits in a bottom corner, tiny, using `success` for CURRENT and `ink-faint` for FUTURE, so nothing on this technical slide is ambiguous to a scrutinizing judge.

**Screenshots:** None — this is a pure architecture slide.

**Diagram:** The seven-stage flow, as the centerpiece.

**Speaker notes:** Be precise and ready for follow-up: "We use LangGraph for our real-time conversational orchestration — a planner node that decides, turn by turn, which specialized agent should act, built from a live agent registry rather than a hardcoded script. Of our 12 registered specialized agents, 7 are fully LLM-reasoning-live today via Groq; 2 are working scaffolds with their tools wired but reasoning still pending, and 2 are registered placeholders for future features. We'd rather tell you exactly where we are than round up." This honesty is itself a credibility signal for a technical judge.

**Time:** 55 sec

---

### Slide 12 — Technical Architecture

**Exact on-slide text:**
> **Frontend** — React · TypeScript · Vite · Tailwind CSS · React Router
> **Backend** — Python · FastAPI · Pydantic
> **Database** — PostgreSQL via Supabase, with Supabase Authentication
> **AI & Agents** — LangGraph · Groq LLM · 12 specialized agents
> **Memory & Intelligence** — Career DNA & World Signals · Evidence Graph · Reflection Journal · Decision Memory
> **Patterns** — Repository pattern · service-layer domain logic · thin REST API layer

**Visual/layout:** `canvas`. Six horizontal bands stacked top to bottom, each a thin full-width `surface.raised` strip with a small left-aligned `accent` label (Frontend/Backend/Database/AI & Agents/Memory & Intelligence/Patterns) and the stack items to its right in `ink`, separated by middle-dots — a classic clean layered-architecture diagram, connected by faint vertical accent connector lines between bands rather than boxed arrows, to keep it light. This is the "understandable in 10 seconds" slide — resist the urge to add anything not in the six bands above.

**Screenshots:** None.

**Diagram:** The six-band layered stack described above.

**Speaker notes:** If asked about specifics: no ORM (direct Supabase client via a clean repository layer, not SQLAlchemy), no vector database/embeddings today (career/story matching today uses deterministic tag-overlap and LLM reasoning, not vector similarity — a real, deliberate choice, not a gap), no separate file-storage layer in use yet. Precise honesty here builds trust with technical judges more than a padded stack list would.

**Time:** 35 sec

---

### Slide 13 — Impact

**Exact on-slide text:**
> **Students** — broader career awareness · better self-understanding · more informed decisions · reduced premature narrowing · confidence backed by evidence, not guesswork
>
> **Parents** — better visibility into their child's real exploration · more informed conversations · less reliance on assumptions
>
> **Institutions** — a path toward scalable, personalized career guidance · visibility into how students actually explore
>
> **Beyond the individual student** — helping talent discover pathways beyond the most visible, traditional careers · improving exposure to emerging and unconventional fields
>
> *(No fabricated statistics — impact framed as intended outcome, not a measured claim.)*

**Visual/layout:** `canvas`. Four columns (Students / Parents / Institutions / Beyond) of equal width, each a simple header + short bullet list, no cards/borders needed — a clean editorial four-column layout reads as more credible here than boxed "impact cards," which tend to read as marketing filler. No numbers, no percentages, no charts — deliberately.

**Screenshots:** None.

**Diagram:** Four-column layout, no connecting elements.

**Speaker notes:** Say explicitly, once, near the top of this slide: "We're not going to put fake numbers on this slide. This is what we believe the platform is built to deliver, and we'd rather earn the numbers than invent them." This line itself is a strong credibility beat for judges who've sat through decks full of invented statistics.

**Time:** 35 sec

---

### Slide 14 — Current → Phase 2 → Phase 3

**Exact on-slide text:**
> **CURRENT AUREON**
> Discover · Explore · Connect · Decide
> A career intelligence foundation for students.
>
> ↓
>
> **PHASE 2**
> Deeper Career Intelligence
>
> ↓
>
> **PHASE 3**
> Lifelong Career Intelligence

**Visual/layout:** `canvas`. A single vertical roadmap spine down the center of the slide — three large stops, each a `surface.raised` node with `success` styling for "CURRENT" (it's live) and `ink-faint`/outline-only styling for the two future phases (clearly not-yet-built), connected by the same open-arrow accent-line motif used throughout the deck. This slide is intentionally sparse — its only job is to set up the next two slides, so resist adding sub-bullets here even though there's room.

**Screenshots:** None.

**Diagram:** The three-stop vertical roadmap spine.

**Speaker notes:** Brief, transitional: "Everything we've shown you is real and running today. What comes next is where we think this becomes something much bigger."

**Time:** 20 sec

---

### Slide 15 — Phase 2: Deeper Career Intelligence

**Exact on-slide text:**
> Expand who Aureon can serve, and the full diversity of careers it understands.
>
> **Career Intelligence as Diverse as Human Potential** — the same depth of guidance for a future doctor, lawyer, artist, farmer, or craftsperson as for a future engineer — deepening across the full spectrum of real careers, not just the most visible tech-centric ones.
> *Medicine · Law · Arts · Design · Trades · Agriculture · Public Service · Research · + more*
>
> **Inclusive, Non-Linear Pathways** — career intelligence that works even when life didn't follow school → college → career — real routes through vocational training, apprenticeships, certifications, practical experience, and return-to-education, starting from wherever someone actually is today.
>
> **Real-Time Career Intelligence** — continuously tracking emerging careers, shifting industries, and AI's impact on roles, translated into "what this actually means for your path," not just headlines.
>
> **Dynamic Skill Forecasting** — understanding emerging skills, shifting demand, and new interdisciplinary skill combinations before they're common knowledge.
>
> **Global Career Ecosystem Intelligence** — universities, research hubs, industries, and innovation ecosystems, mapped by real geography and opportunity.
>
> **Adaptive Career Evolution** — as the student changes, Aureon's understanding of them changes too.
>
> **Help Aureon Grow — Verified Knowledge Evolution** — students can suggest a missing career, an outdated fact, a new opportunity, or a platform improvement; every suggestion is validated and verified before it becomes part of Aureon's knowledge — contribution never means automatic trust.

**Visual/layout:** `canvas`. "PHASE 2" eyebrow in `ink-faint` (future, not current — outline styling, no `success` green anywhere on this slide, deliberately, to keep the current/future visual language consistent with Slide 14). Lead statement large, `ink`. Seven items now, up from six — a 2-column, 4-row grid (last row a single full-width card) of short cards, same visual grammar as Slide 10's grid for pattern recognition, dashed border (vs. Slide 10's solid) as the deliberate "vision, not shipped product" cue. Bullet copy tightened to one crisp clause each to keep the denser grid readable — fuller explanation lives in speaker notes. The "Diverse Career Worlds" card is the one with a visual element: a short row of small `ink-faint` pill tags beneath its one-liner (reusing the exact pill style already established on Slide 9), ending in "+ more" — a genuine visual representation of breadth, never a giant text list.

**Screenshots:** None (future capability — no screenshot exists).

**Diagram:** 2-column, 4-row grid (7 cards, dashed borders), plus the small pill-tag row inside the "Diverse Career Worlds" card.

**Speaker notes:** On career-world breadth: "We don't want Aureon to become 'an AI that knows 500 tech jobs.' A future artist, doctor, farmer, or filmmaker deserves the same depth of guidance as a future engineer — this is about deepening coverage, not claiming we already have it." On non-linear pathways: "Not everyone's path is school → college → career, and that's not a failure state — Aureon should be able to ask 'given where this person is now, what's realistically next,' whether that's an apprenticeship, a certification, or returning to education later." On Help Aureon Grow: "This already exists in the product today as a way for students to flag something missing or outdated — Phase 2 is about that contribution loop becoming a real, verified way the platform's own knowledge keeps growing, never automatically trusted, always validated first."

**Time:** 50 sec

---

### Slide 16 — Phase 3: Lifelong Career Intelligence

**Exact on-slide text:**
> Career guidance should not end when someone chooses their first career.
>
> **Specialized Career-Path AI** — a Career Intelligence Orchestrator reasoning across domain-specialized intelligence (Medical, Legal, Creative, Research, Engineering, Vocational, and more) — curated knowledge, domain-specific retrieval, specialized agents, and fine-tuning only where genuinely justified, so a future doctor and a future filmmaker each get pathway-accurate guidance, not one generalist model stretched thin.
>
> **Career Switching Intelligence** — e.g. Software Engineer → Neuroscience, or Doctor → AI Researcher: mapping existing skills → transferable skills → missing knowledge → realistic bridge pathways.
>
> **Cross-Domain Career Pathways** — real intersections: AI + Medicine, Biology + Computing, Psychology + Technology, Climate + Finance, Arts + AI, Agriculture + Robotics.
>
> **Personal Career Intelligence Agent** — a persistent companion that understands a person's evolving career journey, not just a single decision.
>
> **Lifelong Career Evolution** — Student → Graduate → Early Career → Professional Growth → Specialization → Leadership / Research / Entrepreneurship → Career Switching → Continuous Reinvention.
>
> **Continuous Career Reflection** — understanding how goals, values, priorities, and someone's own definition of success change over time.
>
> **Global Career Intelligence Network** — a long-term, interconnected intelligence layer across careers, industries, experts, education, journeys, and emerging fields worldwide.

**Visual/layout:** `canvas`. Same dashed-future visual grammar as Slide 15 for consistency. Lead statement large. Six items now form a complete 2×3 grid (previously five cards in an uneven 2×3), with "Specialized Career-Path AI" as the new first card — placed first because it's the architectural foundation the other capabilities reason through. The "Lifelong Career Evolution" item keeps its existing special treatment as a small horizontal timeline strip (Student → Graduate → ... → Continuous Reinvention) spanning the slide width beneath the six grid items, unchanged from before.

**Screenshots:** None.

**Diagram:** Complete 2×3 grid (6 cards) + the lifelong-evolution timeline strip beneath.

**Speaker notes:** "Phase 3 is where Aureon stops being just a student tool and becomes a lifelong career intelligence layer — because the biggest career mistake isn't just made at 17, it can be made again at 35." On Specialized Career-Path AI specifically, be precise: "We're not claiming we'll train one completely separate LLM from scratch for every career — that's not a credible claim. The architecture is a Career Intelligence Orchestrator that reasons across domain-specialized intelligence: curated and verified knowledge bases, domain-specific retrieval, specialized agents, career knowledge graphs, and fine-tuned models only where genuinely justified. Take someone asking 'I'm a software engineer, but I'm becoming interested in neuroscience — can I switch?' — the Orchestrator combines Technology Career Intelligence, Research/Neuroscience Career Intelligence, and Career Switching Intelligence together to reason about transferable skills, missing foundations, and realistic bridge pathways. General AI knows about careers. Aureon's specialized career intelligence should understand career pathways."

**Time:** 50 sec

---

### Slide 17 — Vision / Closing

**Exact on-slide text:**
> Career guidance should not be a test you take once at 17.
> It should be an intelligence system that grows with you throughout your life.
>
> AUR*E*ON
> Discover who you could become.
>
> Thank you.
> Questions?

**Visual/layout:** Mirrors Slide 1 almost exactly — full-bleed `canvas`, same extremely subtle atmosphere glow, same centered composition — deliberately bookending the deck. The central statement appears first, serif face, `ink`, larger than any other text in the deck, generous line-height, centered. Below it after clear whitespace, the logo lockup again (smaller than Slide 1's), then "Thank you. / Questions?" in small `ink-faint` text at the very bottom. No new visual element is introduced on this slide — closing the deck by literally returning to where it opened is the point.

**Screenshots:** None.

**Diagram:** None.

**Speaker notes:** Deliver the central statement slowly, then pause before "Thank you." Do not rush the ending — this line is the second of the two ideas the whole deck is built to leave behind.

**Time:** 25 sec

---

## 2. Total Estimated Presentation Time

| Slide | Time |
|---|---|
| 1. Aureon | 0:20 |
| 2. The Problem | 0:45 |
| 3. Why Current Guidance Isn't Enough | 0:45 |
| 4. The Solution | 0:40 |
| 5. How Aureon Works | 0:50 |
| 6. Discover | 0:35 |
| 7. Explore | 0:35 |
| 8. Connect | 0:45 |
| 9. Decide | 0:45 |
| 10. What Makes Aureon Different | 0:40 |
| 11. Not Just Another AI Chatbot | 0:55 |
| 12. Technical Architecture | 0:35 |
| 13. Impact | 0:35 |
| 14. Current → Phase 2 → Phase 3 | 0:20 |
| 15. Phase 2 | 0:50 |
| 16. Phase 3 | 0:50 |
| 17. Vision / Closing | 0:25 |
| **Total** | **≈ 10 min 35 sec** |

This comfortably fits a typical 10–12 minute hackathon pitch slot with ~1–1.5 minutes of slack for pacing/breath or a live-demo cutaway between Slide 9 and Slide 10 if the format allows a demo. If the slot is strictly 7–8 minutes, the safest trims are: shorten Slide 3's speaker notes (keep the visual, talk less), compress Slides 6–8's spoken delivery to one sentence each instead of walking every feature, and let Slide 12 be visual-only with minimal narration.

---

## 3. Complete Deck Narrative Check

Problem (2) → Why current approaches fall short (3) → Solution (4) → How it works, the connective spine (5) → Discover (6) → Explore (7) → Connect (8) → Decide (9) → What makes it different (10) → the intelligence underneath (11) → the technology underneath that (12) → Impact (13) → the roadmap gateway (14) → Phase 2 (15) → Phase 3 (16) → Vision, returning to the opening image (17).

This reads as one continuous argument — problem, why it's unsolved, our answer, how the answer works end-to-end, why it's structurally different, what's under the hood, who it helps, and where it goes — never as a feature dump. The two memorable closing ideas ("you cannot choose a future you never knew existed" / "career guidance should not be a test you take once at 17") bookend Slides 2 and 17 exactly as required, and every slide in between builds toward one or the other.

---

## 4. Final List of Application Screenshots to Capture

1. **Your Universe** — the main conversational identity-discovery screen, with visible Career DNA / confidence indicators. *(Slide 6)*
2. **Exposure Universe** — the exposure map / missing-worlds view. *(Slide 7)*
3. **Expert Connect** — an expert's detail view showing a real, populated Career Journey timeline. *(Slide 8)*
4. **Decision Lab** — a career-comparison view showing reasons-for / reasons-against and a readiness/gap indicator. *(Slide 9)*

Only four screenshots are needed — deliberately minimal, each chosen because it's the single clearest visual proof of that stage's core idea, not a comprehensive feature tour. Capture at a clean viewport size with a logged-in demo account that has enough real evidence/history populated to avoid empty states (a fresh/empty account will undersell every one of these screens).

## 5. Final List of Diagrams to Create

1. **Six-step solution flow** (Slide 4) — Understand → Discover possibilities → Explore/experience → Learn from others → Build evidence → Decide.
2. **Four-stage orbit + memory band** (Slide 5) — the deck's central diagram; build this one first and reuse its visual grammar (node style, arrow style) everywhere else.
3. **Five-step Discover flow strip** (Slide 6) — Interaction → Experience → Reflection → Evidence → Better self-understanding.
4. **Expert Connect vs. Student Stories two-card contrast, plus Knowledge Circles** (Slide 8).
5. **Six-input convergence funnel into Decision Lab** (Slide 9).
6. **Seven-stage AI architecture flow** (Slide 11) — the deck's second most important diagram; build it directly from the exact node names given above, no embellishment.
7. **Six-band layered technical-architecture stack** (Slide 12).
8. **Three-stop vertical roadmap spine** (Slide 14) — current (solid/success) vs. two future phases (dashed/outline).
9. **Lifelong-evolution horizontal timeline strip** (Slide 16).

Nine diagrams total, all built from the same small set of visual primitives (thin accent connector lines, open-ended arrows echoing the logo's compass ticks, `surface.raised` nodes with hairline borders) — deliberately reused rather than each diagram inventing its own style, so the deck reads as one coherent system rather than 17 slides stitched from different templates.

---

## 6. Verification Basis (what this plan is grounded in, not guessed)

- **Live feature inventory (re-verified after the Experience Lab/Life Missions merge and Connect restructuring)**: direct read of `frontend/src/features/navigation/journeyConfig.ts`. **Discover** now has 3 live modules (Your Universe, Experience Lab, Learning Style Discovery) + 1 locked stub (Reality Check) — Life Missions is no longer a separate destination (merged into Experience Lab as "Your Emerging Missions," composed with real Mission Experiences a student can try); Passion Incubator has been retired from the product per explicit product decision and must not appear anywhere in the deck. **Connect** now has 3 destinations (Expert Connect, Knowledge Circles, Student Stories — renamed from Journey Stories) — Mentorship and Parent Connect are no longer separate destinations; both fold into Expert Connect as real routed tabs (Find Experts / My Mentors / Parent Connect), verified live end-to-end (request → pending → expert accepts via review token → accepted, shown correctly in My Mentors with resolved expert identity). "Help Aureon Grow" is a real, live, already-shipped contribution mechanism (sidebar-level, not one of the four main stages), confirmed in the app today.
- **AI/agent architecture**: direct read of `agents/orchestrator/graph.py` (confirmed real `langgraph.graph.StateGraph` usage), `agents/registry.py`, and every file under `agents/specialized/` (12 directories) — 7 confirmed LLM-backed via direct Groq calls (`llm.complete`), 2 confirmed working scaffolds without live reasoning yet, 1 confirmed deterministic non-LLM coordinator, 2 confirmed unimplemented registration placeholders. Confirmed Groq is the sole LLM provider in use (zero OpenAI/Anthropic SDK usage anywhere in the backend).
- **Memory architecture**: direct read of `domain/models/student_profile.py`, `evidence.py`, `career_dna.py`, `discovery_onboarding.py`, `reflection.py`, `decision_memory.py` — Evidence Graph, Career DNA, World Signals, Reflection Journal, and Decision Memory are all real, persisted, per-student fields, not invented framing.
- **Design tokens**: direct read of `frontend/tailwind.config.ts` (full file) and `frontend/src/design-system/components/Logo.tsx` (full file) — every hex value and the logo/tagline description above is copied from these files, not estimated.
- **Tech stack**: direct read of `frontend/package.json` and `backend/pyproject.toml` — confirmed no SQLAlchemy, no pgvector, no Supabase Storage usage anywhere in the codebase (each verified by targeted grep, not absence-of-mention).
- **Competitor scope**: no product names (LinkedIn, Coursera, Unstop, YouTube) appear anywhere in this plan, per explicit instruction — Slide 3's comparison is by approach category only.
