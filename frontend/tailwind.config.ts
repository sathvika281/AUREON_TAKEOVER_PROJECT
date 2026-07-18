import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // The Observatory's ground — the same deep midnight navy as the
        // Identity Discovery scene itself, extended app-wide so every
        // screen reads as one continuous galaxy rather than its own room.
        canvas: "#070B18",
        // Cards, sidebar, and chrome bars — the same flat shade as the
        // canvas itself, so every panel blends into the scene rather than
        // reading as its own distinct blue-tinted region. Only the hairline
        // border and (for raised) a barely-perceptible lift distinguish
        // a panel from open space.
        surface: {
          DEFAULT: "#070B18",
          raised: "#0A0817",
        },
        // A hairline in the observatory's own indigo-violet, not a flat
        // solid rule.
        border: "#2A2650",
        "border-strong": "#3A3560",
        ink: {
          // Warm moonlight — primary text stays warm white throughout.
          DEFAULT: "#f2ede0",
          // Secondary/muted text is the same warm white, just faded toward
          // whatever's behind it (now always the same flat background) —
          // never a separate, distinctly-colored hue.
          muted: "rgba(242,237,224,0.6)",
          faint: "rgba(242,237,224,0.32)",
        },
        // The one true UI accent — a calm starlight blue/periwinkle,
        // matching the observatory's own stars and constellation glow.
        // Reserved for anything interactive: active nav, active tab,
        // links, selected states, progress, icons.
        accent: {
          DEFAULT: "#8B8FD9",
          soft: "#AEB2E8",
          dim: "rgba(139,143,217,0.14)",
        },
        // A rare semantic color — genuine achievement/milestone moments
        // and evidence markers only. Never a general-purpose accent.
        gold: {
          DEFAULT: "#D9B87A",
          soft: "#E9C98F",
        },
        // A rare semantic color — system status only (ready, complete,
        // online, healthy). Never the general interactive accent.
        success: {
          DEFAULT: "#3d6b54",
          soft: "#7fb096",
        },
        // A rare semantic color — errors only.
        danger: {
          DEFAULT: "#c47a63",
        },
        // Atmosphere-only tints — indigo/violet/cyan exist exclusively as
        // gradient/glow stops at very low opacity, defined here so every
        // screen draws from the same restrained palette. Never assigned to
        // text, border, icon, or interactive utilities.
        atmosphere: {
          indigo: "rgba(76,66,168,0.07)",
          violet: "rgba(130,96,176,0.05)",
          cyan: "rgba(96,180,196,0.045)",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "SF Pro Display",
          "Segoe UI",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
        // The Night Sky Editorial 10% — reserved for narrative/reflection
        // moments, never the default body face.
        serif: [
          "Iowan Old Style",
          "Palatino Linotype",
          "Book Antiqua",
          "Georgia",
          "serif",
        ],
      },
    },
  },
  plugins: [],
} satisfies Config;
