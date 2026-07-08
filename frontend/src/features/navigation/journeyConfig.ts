import {
  BarChart3,
  Briefcase,
  Building2,
  Dna,
  GitBranch,
  Globe,
  Layers,
  Map,
  NotebookPen,
  Orbit,
  Puzzle,
  RefreshCw,
  Rocket,
  Route,
  Scale,
  ScanSearch,
  ShieldAlert,
  ShieldCheck,
  Sprout,
  TrendingUp,
  Users,
  type LucideIcon,
} from "lucide-react";

export type StageId = "discover" | "explore" | "experience" | "decide" | "build";

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
 * Single source of truth for both the persistent Journey Navigation and
 * route registration. Only the Discover Yourself modules have a real
 * backend behind them today (the Discovery Agent) — every other stage's
 * agents (Career Intelligence, Decision, Skill Gap, Roadmap, Mentor,
 * Institution) are still honest no-op stubs, so those modules render the
 * shared LockedModule with stage-appropriate copy rather than fabricated
 * content.
 */
export const STAGES: StageConfig[] = [
  {
    id: "discover",
    title: "Discover Yourself",
    modules: [
      {
        id: "identity",
        path: "/discover/identity",
        title: "Identity Discovery",
        icon: Sprout,
        stage: "discover",
        locked: false,
      },
      {
        id: "career-dna",
        path: "/discover/career-dna",
        title: "Career DNA",
        icon: Dna,
        stage: "discover",
        locked: false,
      },
      {
        id: "reflection-journal",
        path: "/discover/reflection-journal",
        title: "Reflection Journal",
        icon: NotebookPen,
        stage: "discover",
        locked: false,
      },
      {
        id: "hidden-potential",
        path: "/discover/hidden-potential",
        title: "Hidden Potential",
        icon: Puzzle,
        stage: "discover",
        locked: false,
      },
    ],
  },
  {
    id: "explore",
    title: "Explore Careers",
    modules: [
      {
        id: "career-intelligence",
        path: "/explore/career-intelligence",
        title: "Career Intelligence",
        icon: Globe,
        stage: "explore",
        locked: false,
      },
      {
        id: "career-reality",
        path: "/explore/career-reality",
        title: "Career Reality",
        icon: BarChart3,
        stage: "explore",
        locked: false,
      },
      {
        id: "future-lens",
        path: "/explore/future-lens",
        title: "Future Lens",
        icon: Rocket,
        stage: "explore",
        locked: false,
      },
    ],
  },
  {
    id: "experience",
    title: "Career Exploration Ecosystem",
    modules: [
      {
        id: "college-collaboration",
        path: "/experience/college-collaboration",
        title: "College Collaboration",
        icon: Building2,
        stage: "experience",
        locked: false,
      },
      {
        id: "expert-connect",
        path: "/experience/expert-connect",
        title: "Expert Connect",
        icon: Users,
        stage: "experience",
        locked: false,
      },
    ],
  },
  {
    id: "decide",
    title: "Decide Confidently",
    modules: [
      {
        id: "decision-lab",
        path: "/decide/decision-lab",
        title: "Decision Lab",
        icon: Scale,
        stage: "decide",
        locked: false,
      },
      {
        id: "parallel-universe",
        path: "/decide/parallel-universe",
        title: "Parallel Universe",
        icon: Orbit,
        stage: "decide",
        locked: false,
      },
      {
        id: "mentor-match",
        path: "/decide/mentor-match",
        title: "Mentor Match",
        icon: Users,
        stage: "decide",
        locked: false,
      },
      {
        id: "career-simulator",
        path: "/decide/career-simulator",
        title: "Career Simulator",
        icon: Route,
        stage: "decide",
        locked: false,
      },
    ],
  },
  {
    id: "build",
    title: "Build Your Journey",
    modules: [
      {
        id: "skill-gap",
        path: "/build/skill-gap",
        title: "Skill Gap Intelligence",
        icon: TrendingUp,
        stage: "build",
        locked: true,
        lockedCopy: "This stage unlocks once Discovery reaches sufficient confidence.",
        lockedDescription:
          "Compares what your target careers actually require against what your evidence already shows you can do.",
        lockedSteps: [
          {
            icon: ScanSearch,
            title: "Reads required skills",
            description: "Pulled from the real skill profiles of your shortlisted and candidate careers — not a generic job description.",
          },
          {
            icon: Layers,
            title: "Reads your evidenced skills",
            description: "From your Career DNA and Discovery Notebook — never a self-assessment form you fill in yourself.",
          },
          {
            icon: Puzzle,
            title: "Names the gap honestly",
            description: "A missing skill is labeled 'not yet evidenced,' never scored, ranked, or guessed at.",
          },
        ],
      },
      {
        id: "roadmap",
        path: "/build/roadmap",
        title: "Personalized Roadmap",
        icon: Map,
        stage: "build",
        locked: true,
        lockedCopy: "This stage unlocks once Discovery reaches sufficient confidence.",
        lockedDescription:
          "Turns your skill gaps and career direction into a sequence of concrete, adaptive milestones.",
        lockedSteps: [
          {
            icon: Map,
            title: "Milestones, not a checklist",
            description: "Each step is derived from an actual gap or goal in your profile — not a stock plan for your target career.",
          },
          {
            icon: RefreshCw,
            title: "Adaptive",
            description: "As new evidence arrives, the roadmap replans instead of ignoring what's changed about you.",
          },
          {
            icon: ShieldCheck,
            title: "Evidence-driven",
            description: "No milestone is added unless there's a real reason for it in your Career DNA or Skill Gap results.",
          },
        ],
      },
      {
        id: "opportunity-graph",
        path: "/build/opportunity-graph",
        title: "Opportunity Graph",
        icon: Briefcase,
        stage: "build",
        locked: true,
        lockedCopy: "This stage unlocks once Discovery reaches sufficient confidence.",
        lockedDescription:
          "Connects real internships, scholarships, competitions, research programs, and jobs to your Career DNA.",
        lockedSteps: [
          {
            icon: Briefcase,
            title: "Five categories",
            description: "Internships, scholarships, competitions, research, and jobs — organized around what's actually relevant to you.",
          },
          {
            icon: GitBranch,
            title: "Connected to Career DNA",
            description: "Every opportunity will be reasoned against your evidence, the same way career candidates are today.",
          },
          {
            icon: ShieldAlert,
            title: "Never fabricated listings",
            description: "This view stays empty rather than inventing a plausible-sounding internship or scholarship that doesn't exist.",
          },
        ],
      },
      {
        id: "progress-intelligence",
        path: "/build/progress-intelligence",
        title: "Progress Intelligence",
        icon: TrendingUp,
        stage: "build",
        locked: false,
      },
    ],
  },
];

export const ALL_MODULES: ModuleEntry[] = STAGES.flatMap((s) => s.modules);
