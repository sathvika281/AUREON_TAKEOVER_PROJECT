import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../api/client";
import type { HealthResponse } from "../api/types";

type HealthState = "checking" | "ok" | "error";

function StatusDot({ health }: { health: HealthState }) {
  const color =
    health === "ok" ? "bg-emerald-500" : health === "error" ? "bg-red-500" : "bg-slate-500";
  return (
    <span
      className={`h-1.5 w-1.5 rounded-full ${color}`}
      title={health === "ok" ? "Connected" : health === "error" ? "Unreachable" : "Checking…"}
    />
  );
}

/**
 * The outer app shell: a fixed-height frame so the persistent Journey
 * Navigation and the main content area can each scroll independently,
 * plus a quiet corner status indicator rather than a bordered header bar.
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
    <div className="h-screen overflow-hidden bg-canvas">
      <div className="fixed right-5 top-5 z-30">
        <StatusDot health={health} />
      </div>
      {children}
    </div>
  );
}
