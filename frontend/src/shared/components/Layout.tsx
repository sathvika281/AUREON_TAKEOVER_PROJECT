import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../api/client";
import type { HealthResponse } from "../api/types";

type HealthState = "checking" | "ok" | "error";

function StatusDot({ health }: { health: HealthState }) {
  const color =
    health === "ok" ? "bg-success-soft" : health === "error" ? "bg-danger" : "bg-ink-faint";
  return (
    <span
      className={`block h-1.5 w-1.5 rounded-full transition-colors duration-500 ${color} ${health === "checking" ? "animate-pulse" : ""}`}
      title={health === "ok" ? "Connected" : health === "error" ? "Unreachable" : "Checking…"}
    />
  );
}

/**
 * The outer app shell — four conceptual layers, back to front, present on
 * every screen: a distant, near-static star field (the universe exists
 * whether or not you're looking); a restrained atmosphere glow built from
 * the indigo/violet/cyan tokens; the interface (nav + chrome, passed in
 * as `children`); and each screen's own foreground content on top of
 * that. Depth here comes from layering and opacity, never a drop shadow.
 */
export function Layout({ children }: { children: ReactNode }) {
  const [health, setHealth] = useState<HealthState>("checking");

  useEffect(() => {
    apiClient
      .get<HealthResponse>("/health")
      .then((res) => setHealth(res.status === "ok" ? "ok" : "error"))
      .catch(() => setHealth("error"));
  }, []);

  return (
    <div className="relative h-screen overflow-hidden bg-canvas">
      {/* Layer 1 — distant universe: a fixed, barely-perceptible star field. */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 opacity-70"
        style={{
          backgroundImage:
            "radial-gradient(1px 1px at 8% 22%, rgba(242,237,224,0.5) 0, transparent 60%)," +
            "radial-gradient(1px 1px at 22% 68%, rgba(242,237,224,0.35) 0, transparent 60%)," +
            "radial-gradient(1.5px 1.5px at 38% 12%, rgba(242,237,224,0.4) 0, transparent 60%)," +
            "radial-gradient(1px 1px at 54% 84%, rgba(242,237,224,0.3) 0, transparent 60%)," +
            "radial-gradient(1px 1px at 68% 34%, rgba(242,237,224,0.45) 0, transparent 60%)," +
            "radial-gradient(1.5px 1.5px at 81% 58%, rgba(242,237,224,0.3) 0, transparent 60%)," +
            "radial-gradient(1px 1px at 92% 14%, rgba(242,237,224,0.4) 0, transparent 60%)," +
            "radial-gradient(1px 1px at 47% 46%, rgba(242,237,224,0.25) 0, transparent 60%)",
        }}
      />
      {/* Layer 2 — atmosphere: soft indigo/violet/cyan glow, never assigned
          to text/border/interactive color, only ever this ambient wash. */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          backgroundImage:
            "radial-gradient(60% 50% at 18% 0%, rgba(76,66,168,0.09) 0%, transparent 65%)," +
            "radial-gradient(55% 45% at 100% 30%, rgba(130,96,176,0.06) 0%, transparent 65%)," +
            "radial-gradient(50% 40% at 30% 100%, rgba(96,180,196,0.05) 0%, transparent 65%)",
        }}
      />

      {/* Layers 3 + 4 — interface (JourneyNav) and each screen's own
          foreground content, both passed in as `children`, sit above
          the atmosphere as one stacking context. */}
      <div className="relative z-10 h-full">{children}</div>

      {/* The connection-status signal — quieter than a bordered header,
          a single point of light rather than a chrome element. */}
      <div className="fixed right-5 top-5 z-30">
        <StatusDot health={health} />
      </div>
    </div>
  );
}
