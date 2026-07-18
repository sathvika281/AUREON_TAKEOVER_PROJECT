import {
  Award,
  FileText,
  GitBranch,
  Globe,
  IdCard,
  MessageSquareQuote,
  NotebookPen,
  Search,
  Upload,
  type LucideIcon,
} from "lucide-react";

export type EvidenceType =
  | "resume"
  | "projects"
  | "portfolio"
  | "linkedin"
  | "certificates"
  | "career-research"
  | "reflection"
  | "personal-notes"
  | "upload-file";

/**
 * The single source of truth for the unified evidence attachment
 * experience. Aureon has one intelligence — these are not separate
 * tools, only different kinds of evidence a student can share. Every
 * door still calls exactly one of the same four investigate()/
 * sendMessage() functions the codebase already had (github/document/url/
 * search intelligence + Discovery's own conversation) — see
 * EvidenceMissionModal.tsx for the routing. GitHub itself is never
 * named or emphasized; "Projects" is the one real door into it, framed
 * around what the student built rather than which platform it's on.
 */
export interface EvidenceDoor {
  type: EvidenceType;
  label: string;
  question: string;
  icon: LucideIcon;
  inputKind: "file" | "text" | "reflection";
  placeholder?: string;
  /** Shown once, after a real, evidence-adding response — never on
   * failure, never inventing a specific fact beyond this fixed line. */
  completionSentence: string;
}

export const EVIDENCE_DOORS: EvidenceDoor[] = [
  {
    type: "resume",
    label: "Resume / CV",
    question: "What have you achieved?",
    icon: FileText,
    inputKind: "file",
    completionSentence: "Aureon now understands your achievements better.",
  },
  {
    type: "projects",
    label: "Projects",
    question: "What have you built?",
    icon: GitBranch,
    inputKind: "text",
    placeholder: "A link to a project, repo, or something you made",
    completionSentence: "Aureon now understands your engineering experience better.",
  },
  {
    type: "reflection",
    label: "Reflection Journal",
    question: "How are you evolving?",
    icon: MessageSquareQuote,
    inputKind: "reflection",
    placeholder: "What's been on your mind lately?",
    completionSentence: "Aureon has learned more about your motivations.",
  },
  {
    type: "certificates",
    label: "Certificates",
    question: "What have you earned?",
    icon: Award,
    inputKind: "file",
    completionSentence: "Aureon now understands what you've earned better.",
  },
  {
    type: "career-research",
    label: "Career Research",
    question: "What are you curious about?",
    icon: Search,
    inputKind: "text",
    placeholder: "Should I pursue AI Research?",
    completionSentence: "Your curiosity is becoming clearer.",
  },
  {
    type: "portfolio",
    label: "Portfolio Website",
    question: "What have you created?",
    icon: Globe,
    inputKind: "text",
    placeholder: "https://your-portfolio.com",
    completionSentence: "Aureon now understands your work better.",
  },
  {
    type: "linkedin",
    label: "LinkedIn Profile",
    question: "How do you present yourself professionally?",
    icon: IdCard,
    inputKind: "text",
    placeholder: "https://linkedin.com/in/…",
    completionSentence: "Aureon now understands your professional story better.",
  },
  {
    type: "personal-notes",
    label: "Personal Notes",
    question: "What's on your mind?",
    icon: NotebookPen,
    inputKind: "reflection",
    placeholder: "Anything you want Aureon to know…",
    completionSentence: "Aureon has taken note.",
  },
  {
    type: "upload-file",
    label: "Upload File",
    question: "Is there something else worth sharing?",
    icon: Upload,
    inputKind: "file",
    completionSentence: "Aureon now understands you a little better.",
  },
];

/** The one ritual sequence, identical for every door. Every stage before
 * the last is honest pacing over one real, non-streaming request (same
 * precedent as chat/AgentActivityIndicator.tsx) — the last stage is the
 * one moment that's always literally backed by a resolved change. */
export const MISSION_STAGES = [
  "Understanding You",
  "Investigating",
  "Finding Patterns",
  "Connecting Everything",
  "Updating Your Universe",
  "Your Universe Has Evolved",
] as const;

/** The stage index the pacing timer holds at while the real request is
 * still in flight — it never advances to the final stage on its own. */
export const MISSION_HOLD_STAGE_INDEX = MISSION_STAGES.length - 2;

/** A satellite's icon, matched against the real, free-form
 * NotebookEntry.source string the backend writes — never a fixed
 * frontend enum, since sources like "github" have no identically-named
 * door (GitHub is deliberately folded into "Projects" and never named).
 * Unmatched sources fall back to a plain dot rather than guessing. */
const SOURCE_SYNONYMS: Record<string, EvidenceType> = {
  github: "projects",
  project: "projects",
  repo: "projects",
  document: "resume",
  pdf: "resume",
  certificate: "certificates",
  url: "portfolio",
  link: "portfolio",
  web: "portfolio",
  website: "portfolio",
  search: "career-research",
  research: "career-research",
  conversation: "personal-notes",
  chat: "personal-notes",
  note: "personal-notes",
};

export function matchEvidenceIcon(source: string): LucideIcon | null {
  const normalized = source.trim().toLowerCase().replace(/[\s_-]+/g, "");
  const direct = EVIDENCE_DOORS.find((door) => {
    const type = door.type.replace(/-/g, "");
    const label = door.label.toLowerCase().replace(/[\s/]+/g, "");
    return type === normalized || normalized.includes(type) || label.includes(normalized);
  });
  if (direct) return direct.icon;

  const synonymEntry = Object.entries(SOURCE_SYNONYMS).find(([key]) => normalized.includes(key));
  if (synonymEntry) {
    const door = EVIDENCE_DOORS.find((d) => d.type === synonymEntry[1]);
    if (door) return door.icon;
  }

  return null;
}
