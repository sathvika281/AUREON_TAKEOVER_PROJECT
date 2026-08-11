import {
  BookOpen,
  Brain,
  Briefcase,
  Building2,
  Compass,
  Eye,
  FlaskConical,
  Globe,
  Hammer,
  Handshake,
  Layers,
  LineChart,
  Scale,
  Sprout,
  Telescope,
  Users,
  type LucideIcon,
} from "lucide-react";

export type StageId = "discover" | "explore" | "connect" | "decide" | "knowledge";

export interface ModuleExplainerStep {
  icon: LucideIcon;
  title: string;
  description: string;
}

export interface ModuleEntry {
  id: string;
  path: string;
  title: string;
  icon: LucideIcon;
  stage: StageId;
  /** Real data source today, vs. a stub agent with nothing to show yet. */
  locked: boolean;
  /** Only present for locked modules — never "Coming Soon." */
  lockedCopy?: string;
  /** What this module actually does, once it exists — for locked modules only. */
  lockedDescription?: string;
  /** How this module will work, framed as mechanism rather than a feature pitch. */
  lockedSteps?: ModuleExplainerStep[];
}

export interface StageConfig {
  id: StageId;
  title: string;
  modules: ModuleEntry[];
}

/**
 * Aureon V2 Phase 1 — a decisive consolidation of what had grown into 5
 * stage groups / ~17 modules. Each visible module answers exactly one
 * real user question (Your Universe: who am I? Career Explorer: what
 * careers fit me? College Explorer: where should I study? Expert
 * Connect: who can guide me? Decision Lab: which path should I choose?).
 * Career DNA / Reflection Journal / Hidden Potential are no longer
 * listed here — they're real tabs inside the Your Universe workspace
 * now (see features/discovery/components/UniverseWorkspaceTabs.tsx),
 * still real routes, just not separate sidebar entries. Global Trends
 * and Entrance Hub have no real backend yet — honest locked stubs,
 * deferred to a future phase, never fabricated content.
 *
 * Discover Navigation Refactor — Experience Lab (formerly "Career
 * Experiments") and Hidden Potential (now also home to what was
 * Talent Discovery) are each their own destination here, same as
 * Career Explorer/Expert Connect, not tabs inside Your Universe.
 *
 * Discover Batch 4 shipped Missing Worlds and Life Missions as real,
 * unlocked modules. Discover Batch 5 shipped Learning Style Discovery
 * the same way. Only Reality Check remains a
 * locked stub (see LockedModule.tsx), same pattern every prior module
 * used before it shipped.
 *
 * Exposure Universe merge — Missing Worlds is no longer a separate
 * Discover destination; its detection engine (missing_worlds_engine.py)
 * lives on unchanged, composed into the Explore stage's Exposure
 * Universe module instead. Never delete this history — Life Missions
 * was genuinely part of the same Discover Batch 4 as Missing Worlds,
 * which is why they were originally mentioned together.
 *
 * Experience Lab / Life Missions merge — Life Missions is no longer a
 * separate Discover destination either; its resonance engine
 * (life_mission_engine.py) lives on unchanged, composed into Experience
 * Lab as "Your Emerging Missions" instead, alongside real, curated
 * Mission Experiences a student can actually try. /discover/life-missions
 * now redirects to /discover/experience-lab (see App.tsx).
 *
 * Connect restructuring — Mentorship and Parent Connect are no longer
 * separate Connect destinations; both fold into Expert Connect as real
 * routed tabs (ExpertConnectTabs.tsx — /experience/expert-connect/
 * my-mentors and /parent-connect), since requesting a mentor is a
 * natural continuation of discovering an expert, and Parent Connect
 * serves the same human-guidance journey from a parent's side.
 * /experience/mentorships and the old /experience/parent-connect both
 * redirect (see App.tsx). Journey Stories keeps its internal id/path/
 * backend names but is now titled "Student Stories" everywhere
 * user-facing, since expert professional journeys live inside Expert
 * Connect now — the old name read as ambiguous between the two.
 */
export const STAGES: StageConfig[] = [
  {
    id: "discover",
    title: "Discover",
    modules: [
      {
        id: "identity",
        path: "/discover/identity",
        // User-facing copy only — internal id/path/component/context all
        // stay "Identity Discovery" per the Grand Finale redesign's
        // constraint that architecture names don't change.
        title: "Your Universe",
        icon: Sprout,
        stage: "discover",
        locked: false,
      },
      {
        id: "experience-lab",
        path: "/discover/experience-lab",
        title: "Experience Lab",
        icon: FlaskConical,
        stage: "discover",
        locked: false,
      },
      {
        id: "learning-style-discovery",
        path: "/discover/learning-style-discovery",
        title: "Learning Style Discovery",
        icon: Brain,
        stage: "discover",
        locked: false,
      },
      {
        id: "reality-check",
        path: "/discover/reality-check",
        title: "Reality Check",
        icon: Eye,
        stage: "discover",
        locked: true,
        lockedCopy: "An honest mirror, not a critique — grounded entirely in your own real evidence.",
        lockedDescription: "A candid look at how your self-image compares to what Aureon has actually observed about you.",
        lockedSteps: [
          {
            icon: Eye,
            title: "Compares belief against evidence",
            description: "Looks at what you've said about yourself against what your Career DNA and Evidence Graph actually show.",
          },
          {
            icon: Sprout,
            title: "Never a score, always explained",
            description: "Any gap it surfaces comes with the real evidence behind it — never a number, never framed as a failure.",
          },
        ],
      },
    ],
  },
  {
    id: "explore",
    title: "Explore",
    modules: [
      {
        id: "career-reality",
        path: "/explore/career-reality",
        title: "Career Explorer",
        icon: Globe,
        stage: "explore",
        locked: false,
      },
      {
        id: "college-collaboration",
        path: "/experience/college-collaboration",
        title: "College Explorer",
        icon: Building2,
        stage: "explore",
        locked: false,
      },
      {
        id: "global-trends",
        path: "/explore/global-trends",
        title: "Global Trends",
        icon: LineChart,
        stage: "explore",
        locked: false,
      },
      {
        // Exposure Universe merge — this destination now composes both
        // the former Missing Worlds engine (detection: "what haven't I
        // meaningfully explored?") and Exposure Universe's own unfamiliar-
        // possibility selection (discovery + action) into one screen.
        // "Missing Worlds" is no longer a separate navigation entry; its
        // intelligence lives on unchanged in missing_worlds_engine.py.
        id: "exposure-universe",
        path: "/explore/exposure-universe",
        title: "Exposure Universe",
        icon: Telescope,
        stage: "explore",
        locked: false,
      },
      {
        id: "opportunity-equality",
        path: "/explore/opportunity-equality",
        title: "Opportunity Equality",
        icon: Handshake,
        stage: "explore",
        locked: false,
      },
    ],
  },
  {
    // Sprint 8 — Discoverability & Navigation. Skills/Companies/Projects
    // were previously reachable only through Career detail cross-links
    // or a direct URL — fine while Sprints 1-3 built them incrementally,
    // no longer right now that they're real, connected capabilities.
    // Deliberately its OWN stage rather than folded into "Explore":
    // Discover/Explore/Connect/Decide are the guided, evidence-gated
    // journey (each answers a personalized "what fits me" question),
    // while these three are an always-open reference layer with no
    // gating at all — merging them into Explore would misrepresent them
    // as part of that progression. "Knowledge Base" reuses the exact
    // term already used internally for these three (see e.g.
    // domain/models/project.py's "Project Knowledge Base"), not an
    // invented label. Careers is deliberately NOT duplicated here —
    // Career Explorer under Explore already is that entry point, and
    // the frozen IA doc calls overlap a defect. This adds no new
    // routes; /skills, /companies, /projects already exist (Sprints
    // 1-3) and NavLink's default (non-`end`) matching already keeps
    // this section highlighted on nested detail pages like /skills/:id.
    id: "knowledge",
    title: "Knowledge Base",
    modules: [
      {
        id: "skills",
        path: "/skills",
        title: "Skills",
        icon: Layers,
        stage: "knowledge",
        locked: false,
      },
      {
        id: "companies",
        path: "/companies",
        title: "Companies",
        icon: Briefcase,
        stage: "knowledge",
        locked: false,
      },
      {
        // Sprint 7 made this a real evidence surface (persisted attempt
        // history, evidence/no-evidence distinction, repeat attempts),
        // not just a passive catalog — reflected in also being the one
        // Knowledge Base entry additionally surfaced on Mission
        // Control's existing Quick Actions row (see HomeScreen.tsx).
        id: "projects",
        path: "/projects",
        title: "Projects",
        icon: Hammer,
        stage: "knowledge",
        locked: false,
      },
    ],
  },
  {
    id: "connect",
    title: "Connect",
    modules: [
      {
        id: "expert-connect",
        path: "/experience/expert-connect",
        title: "Expert Connect",
        icon: Users,
        stage: "connect",
        locked: false,
      },
      {
        id: "knowledge-circles",
        path: "/experience/knowledge-circles",
        title: "Knowledge Circles",
        icon: Compass,
        stage: "connect",
        locked: false,
      },
      {
        id: "journey-stories",
        path: "/experience/journey-stories",
        title: "Student Stories",
        icon: BookOpen,
        stage: "connect",
        locked: false,
      },
    ],
  },
  {
    id: "decide",
    title: "Decide",
    modules: [
      {
        id: "decision-lab",
        path: "/decide/decision-lab",
        title: "Decision Lab",
        icon: Scale,
        stage: "decide",
        locked: false,
      },
    ],
  },
];

export const ALL_MODULES: ModuleEntry[] = STAGES.flatMap((s) => s.modules);
