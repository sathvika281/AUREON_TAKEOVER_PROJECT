import { useRef, useState } from "react";
import { FileSearch, FileText, GitBranch, ShieldAlert } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useDocumentIntelligenceContext } from "./DocumentIntelligenceContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: FileText,
    title: "Reads only real, embedded text",
    description: "A genuine PDF text extraction — never OCR, never a guess at scanned or image-only pages.",
  },
  {
    icon: FileSearch,
    title: "Classifies deterministically",
    description: "Filename and, if needed, the document's own first-page wording decide the type — never an LLM guess.",
  },
  {
    icon: GitBranch,
    title: "Routes to the right specialist",
    description: "A resume goes to Discovery, a university brochure to Institution, a research paper to Career Intelligence, a publication to Mentor — automatically.",
  },
  {
    icon: ShieldAlert,
    title: "Explains itself honestly",
    description: "Encrypted, corrupt, or scan-only documents get a clear explanation — never fabricated findings.",
  },
];

export function findingsReport({
  title, summary, keyFindings, structuredFields,
}: {
  title: string | null;
  summary: string | null;
  keyFindings: string[];
  structuredFields: Record<string, string>;
}) {
  return (
    <Surface tone="raised" padding="md">
      {title && <p className="text-sm font-medium text-ink">{title}</p>}
      {summary && <p className="mt-2 text-sm leading-relaxed text-ink-muted">{summary}</p>}
      {keyFindings.length > 0 && (
        <ul className="mt-3 space-y-1">
          {keyFindings.map((finding, i) => (
            <li key={i} className="text-xs text-ink-muted"><span className="text-accent">＋</span> {finding}</li>
          ))}
        </ul>
      )}
      {Object.entries(structuredFields).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border pt-3">
          {Object.entries(structuredFields).map(([key, value]) => (
            <span key={key} className="rounded-full border border-border px-2 py-1 font-mono text-[0.65rem] text-ink-faint">
              {key.replace(/_/g, " ")}: {value}
            </span>
          ))}
        </div>
      )}
    </Surface>
  );
}

export function DocumentIntelligenceScreen() {
  const { result, isInvestigating, error, investigate } = useDocumentIntelligenceContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Document Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Upload a career-related document — a resume, a university brochure, a research paper, a
        publication — and Aureon investigates it as a real mission, routing to whichever
        specialist actually owns that kind of document.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How Document Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full truncate rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-left text-sm text-ink-muted transition-colors hover:border-accent-soft/40"
        >
          {selectedFile ? selectedFile.name : "Choose a PDF…"}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
        />
        <Button
          onClick={() => selectedFile && investigate(selectedFile)}
          disabled={isInvestigating || !selectedFile}
        >
          {isInvestigating ? "Investigating…" : "Investigate"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-danger">{error}</p>}

      {!result && !isInvestigating && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={FileText}
            title="No Document Investigated Yet"
            description="Choose a PDF above and Aureon will read it, classify it, and route it to the specialist who owns that document type."
          />
        </div>
      )}

      {result && result.status !== "completed" && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Complete This Investigation"
            description={result.explanation ?? "This document couldn't be read."}
          />
        </div>
      )}

      {result && result.status === "completed" && (
        <div className="mt-8">
          <MissionWorkspace
            snapshot={result.mission}
            artifactsUpdated={result.artifacts_updated}
            finalReport={findingsReport({
              title: result.title, summary: result.summary,
              keyFindings: result.key_findings, structuredFields: result.structured_fields,
            })}
          />
        </div>
      )}
    </div>
  );
}
