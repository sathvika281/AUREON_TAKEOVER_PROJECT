import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

export type ParentLanguage = "en" | "hi" | "te";

export const SUPPORTED_PARENT_LANGUAGES: { code: ParentLanguage; nativeLabel: string; englishLabel: string }[] = [
  { code: "en", nativeLabel: "English", englishLabel: "English" },
  { code: "hi", nativeLabel: "हिन्दी", englishLabel: "Hindi" },
  { code: "te", nativeLabel: "తెలుగు", englishLabel: "Telugu" },
];

const STORAGE_KEY = "aureon-parent-connect-language";

interface ParentLanguageContextValue {
  language: ParentLanguage | null;
  setLanguage: (language: ParentLanguage) => void;
  resetLanguage: () => void;
}

const ParentLanguageContext = createContext<ParentLanguageContextValue | null>(null);

/**
 * Small, local-to-Parent-Connect language state — not a global app-wide
 * i18n system (none exists in Aureon today; see
 * scripts/translate_parent_connect_content.py for how the actual
 * translated content is generated). `language` is `null` until the
 * parent makes an explicit choice, which is the signal
 * ParentConnectScreen uses to show the language-choice step first.
 */
export function ParentLanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<ParentLanguage | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "en" || stored === "hi" || stored === "te") {
      setLanguageState(stored);
    }
  }, []);

  const setLanguage = useCallback((next: ParentLanguage) => {
    localStorage.setItem(STORAGE_KEY, next);
    setLanguageState(next);
  }, []);

  const resetLanguage = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setLanguageState(null);
  }, []);

  return (
    <ParentLanguageContext.Provider value={{ language, setLanguage, resetLanguage }}>
      {children}
    </ParentLanguageContext.Provider>
  );
}

export function useParentLanguage(): ParentLanguageContextValue {
  const ctx = useContext(ParentLanguageContext);
  if (!ctx) throw new Error("useParentLanguage must be used within a ParentLanguageProvider");
  return ctx;
}
