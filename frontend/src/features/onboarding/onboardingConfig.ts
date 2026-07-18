/**
 * The data-driven question model for adaptive onboarding — mirrors
 * features/navigation/journeyConfig.ts's array/record-of-config
 * convention. Every choice set that represents genuine uncertainty
 * ("I have no idea what I want," "I'm not sure yet," "None Yet") is a
 * first-class, equally-valid option — never a fallback or error state.
 */

export type CurrentSituation = "no_idea" | "few_careers" | "dream_career" | "switch_careers";

export const CURRENT_SITUATIONS: { id: CurrentSituation; label: string }[] = [
  { id: "no_idea", label: "I have no idea what I want." },
  { id: "few_careers", label: "I have a few careers in mind." },
  { id: "dream_career", label: "I already know my dream career." },
  { id: "switch_careers", label: "I want to switch careers." },
];

export const WORLDS = ["AI", "Space", "Healthcare", "Business", "Design", "Arts", "Psychology"] as const;
export type World = (typeof WORLDS)[number];

// Per-world follow-up question content (prompts/options) is now
// backend-owned — see Progressive Discovery Service
// (domain/services/progressive_discovery.py's WORLD_FOLLOWUPS) — and
// arrives via GET/POST .../progressive-discovery responses. The
// frontend renders whatever the backend sends; it no longer hardcodes
// the question content itself.

export const LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Marathi", "Bengali", "Other"];
export const STAGE_OPTIONS = ["School", "College", "Professional"] as const;
export type StudentStage = (typeof STAGE_OPTIONS)[number];
