import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig(({ mode }) => ({
  // GitHub Pages serves this as a project page at /AUREON_TAKEOVER_PROJECT/,
  // not the domain root — `npm run build:gh-pages` passes --mode gh-pages;
  // local dev and any other build target stay at root.
  base: mode === "gh-pages" ? "/AUREON_TAKEOVER_PROJECT/" : "/",
  plugins: [react()],
  server: {
    port: 5173,
  },
}));
