import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Page background — near-black, not pure black.
        canvas: "#0b0b0b",
        // Cards. `raised` is used sparingly for a second layer of hierarchy
        // (e.g. a hero panel above ordinary tiles), not as a glow effect.
        surface: {
          DEFAULT: "#141414",
          raised: "#181818",
        },
        border: "#2a2a2a",
        ink: {
          DEFAULT: "#f7f7f7",
          muted: "#9b9b9b",
          faint: "#6e6e6e",
        },
        // The single restrained accent — used only for primary actions,
        // the active mission, progress indicators, and agent badges.
        // Never used to color a whole screen.
        accent: {
          DEFAULT: "#3d6b54",
          soft: "#5c8a72",
          dim: "#2a4a3c",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
} satisfies Config;
