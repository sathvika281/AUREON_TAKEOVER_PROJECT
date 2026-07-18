import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { X } from "lucide-react";

import { Button } from "../../../design-system/components/Button";
import { Input } from "../../../design-system/components/Input";
import { EASE_CALM } from "../../../design-system/motion";
import { useDocumentIntelligenceContext } from "../../document-intelligence/DocumentIntelligenceContext";
import { useGitHubIntelligenceContext } from "../../github-intelligence/GitHubIntelligenceContext";
import { useSearchInvestigationContext } from "../../search-investigation/SearchInvestigationContext";
import { useUrlInvestigationContext } from "../../url-investigation/UrlInvestigationContext";
import { useDiscoveryContext } from "../DiscoveryContext";
import {
  EVIDENCE_DOORS,
  MISSION_HOLD_STAGE_INDEX,
  MISSION_STAGES,
  type EvidenceType,
} from "./evidenceMissionCopy";

const STAGE_INTERVAL_MS = 1300;

type Phase = "input" | "running" | "done" | "error";

/**
 * One ritual, five real doors. Every door calls the exact same
 * investigate()/sendMessage() the standalone screens already call —
 * only the presentation is unified. Stages before the last are honest
 * pacing over one real, non-streaming request (same precedent as
 * chat/AgentActivityIndicator.tsx); "Your Universe Has Evolved" is the
 * one stage that's always literally backed by a resolved, real change,
 * shown only after refreshProfile() completes so the Universe behind
 * this modal has already visually responded.
 */
export function EvidenceMissionModal({
  evidenceType,
  onClose,
}: {
  evidenceType: EvidenceType;
  onClose: () => void;
}) {
  const door = EVIDENCE_DOORS.find((d) => d.type === evidenceType)!;

  const github = useGitHubIntelligenceContext();
  const documentIntel = useDocumentIntelligenceContext();
  const urlIntel = useUrlInvestigationContext();
  const search = useSearchInvestigationContext();
  const { sendMessage, isSending, error: discoveryError, refreshProfile } = useDiscoveryContext();

  const [textValue, setTextValue] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [phase, setPhase] = useState<Phase>("input");
  const [stageIndex, setStageIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const wasInvestigatingRef = useRef(false);

  const activeIsInvestigating =
    evidenceType === "projects"
      ? github.isInvestigating
      : evidenceType === "resume" || evidenceType === "certificates" || evidenceType === "upload-file"
        ? documentIntel.isInvestigating
        : evidenceType === "portfolio" || evidenceType === "linkedin"
          ? urlIntel.isInvestigating
          : evidenceType === "career-research"
            ? search.isInvestigating
            : isSending;

  useEffect(() => {
    if (phase !== "running") return;
    const timer = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, MISSION_HOLD_STAGE_INDEX));
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [phase]);

  useEffect(() => {
    if (phase !== "running") {
      wasInvestigatingRef.current = activeIsInvestigating;
      return;
    }
    if (wasInvestigatingRef.current && !activeIsInvestigating) {
      if (didSucceed()) {
        void refreshProfile().then(() => {
          setStageIndex(MISSION_STAGES.length - 1);
          setPhase("done");
        });
      } else {
        setErrorMessage(currentError() ?? "Aureon couldn't complete this just now — please try again.");
        setPhase("error");
      }
    }
    wasInvestigatingRef.current = activeIsInvestigating;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeIsInvestigating, phase]);

  function didSucceed(): boolean {
    switch (evidenceType) {
      case "projects":
        return github.result?.status === "completed" && github.result.evidence_added;
      case "resume":
      case "certificates":
      case "upload-file":
        return documentIntel.result?.status === "completed" && documentIntel.result.evidence_added;
      case "portfolio":
      case "linkedin":
        return urlIntel.result?.status === "completed" && urlIntel.result.evidence_added;
      case "career-research":
        return search.result?.status === "completed" && search.result.evidence_added;
      case "reflection":
      case "personal-notes":
        return discoveryError === null;
    }
  }

  function currentError(): string | null {
    switch (evidenceType) {
      case "projects":
        return github.error;
      case "resume":
      case "certificates":
      case "upload-file":
        return documentIntel.error;
      case "portfolio":
      case "linkedin":
        return urlIntel.error;
      case "career-research":
        return search.error;
      case "reflection":
      case "personal-notes":
        return discoveryError;
    }
  }

  function submit() {
    setPhase("running");
    setStageIndex(0);
    setErrorMessage(null);
    if (evidenceType === "projects") void github.investigate(textValue.trim());
    else if ((evidenceType === "resume" || evidenceType === "certificates" || evidenceType === "upload-file") && file)
      void documentIntel.investigate(file);
    else if (evidenceType === "portfolio" || evidenceType === "linkedin") void urlIntel.investigate(textValue.trim());
    else if (evidenceType === "career-research") void search.investigate(textValue.trim());
    else if (evidenceType === "reflection" || evidenceType === "personal-notes") void sendMessage(textValue.trim());
  }

  const canSubmit = door.inputKind === "file" ? file !== null : textValue.trim().length > 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5, ease: EASE_CALM }}
      className="fixed inset-0 z-40 flex items-center justify-center bg-[#070B18]/95 px-6"
    >
      <div className="w-full max-w-md">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <door.icon size={16} className="text-[#D9B87A]" />
            <p className="text-sm font-medium text-[#F2EDE0]">{door.label}</p>
          </div>
          {phase !== "running" && (
            <button onClick={onClose} className="text-[#6E6A5E] transition hover:text-[#F2EDE0]">
              <X size={16} />
            </button>
          )}
        </div>

        {phase === "input" && (
          <div className="mt-6">
            <p className="font-serif text-lg text-[#F2EDE0]">{door.question}</p>
            <div className="mt-4">
              {door.inputKind === "file" ? (
                <label className="flex cursor-pointer items-center justify-center rounded-xl border border-dashed border-[#3A3560] bg-[#0C0A22] px-4 py-6 text-sm text-[#6E6A5E] transition hover:border-[#D9B87A]/40">
                  {file ? file.name : "Choose a PDF…"}
                  <input
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  />
                </label>
              ) : door.inputKind === "reflection" ? (
                <textarea
                  value={textValue}
                  onChange={(e) => setTextValue(e.target.value)}
                  placeholder={door.placeholder}
                  rows={4}
                  className="w-full rounded-xl border border-[#3A3560] bg-[#0C0A22] px-4 py-2.5 text-sm text-[#F2EDE0] placeholder:text-[#6E6A5E] focus:border-[#D9B87A]/40 focus:outline-none"
                />
              ) : (
                <Input
                  value={textValue}
                  onChange={(e) => setTextValue(e.target.value)}
                  placeholder={door.placeholder}
                  className="border-[#3A3560] bg-[#0C0A22] text-[#F2EDE0] placeholder:text-[#6E6A5E] focus:border-[#D9B87A]/40"
                />
              )}
            </div>
            <Button
              className="mt-4 w-full bg-[#D9B87A] text-[#141033] hover:bg-[#E9C98F]"
              disabled={!canSubmit}
              onClick={submit}
            >
              Begin
            </Button>
          </div>
        )}

        {(phase === "running" || phase === "done") && (
          <div className="mt-10 text-center">
            <motion.p
              key={stageIndex}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: EASE_CALM }}
              className="font-mono text-sm uppercase tracking-widest text-[#D9B87A]"
            >
              {MISSION_STAGES[stageIndex]}
            </motion.p>
            {phase === "done" && (
              <>
                <p className="mt-4 font-serif text-base leading-relaxed text-[#F2EDE0]">{door.completionSentence}</p>
                <Button className="mt-6 bg-[#D9B87A] text-[#141033] hover:bg-[#E9C98F]" onClick={onClose}>
                  Back to Your Universe
                </Button>
              </>
            )}
          </div>
        )}

        {phase === "error" && (
          <div className="mt-10 text-center">
            <p className="text-sm text-danger">{errorMessage}</p>
            <Button
              className="mt-6 text-[#9C978A] hover:text-[#F2EDE0]"
              variant="ghost"
              onClick={() => setPhase("input")}
            >
              Try Again
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
