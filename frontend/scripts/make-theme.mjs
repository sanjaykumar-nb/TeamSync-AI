/**
 * Generate src/app/globals.css from one palette definition.
 *
 * The theme is Tailwind's own palette: Slate for neutrals, Indigo for the
 * accent, and Emerald / Amber / Orange / Rose for the four risk levels. Those
 * scales are published, contrast-checked and stable, which is the point — the
 * previous theme was stock shadcn defaults plus about forty hard-coded colours
 * scattered through components, so a risk badge in one view did not match the
 * same risk in another.
 *
 * Everything is emitted as `H S% L%` triples so Tailwind's hsl(var(--x)) tokens
 * keep working, and every colour has a dark counterpart chosen from the same
 * scale rather than invented.
 *
 *   node scripts/make-theme.mjs
 */
import { writeFileSync } from "node:fs";

const TW = {
  slate: {
    50: "#f8fafc", 100: "#f1f5f9", 200: "#e2e8f0", 300: "#cbd5e1", 400: "#94a3b8",
    500: "#64748b", 600: "#475569", 700: "#334155", 800: "#1e293b", 900: "#0f172a",
    950: "#020617",
  },
  indigo: {
    50: "#eef2ff", 100: "#e0e7ff", 200: "#c7d2fe", 300: "#a5b4fc", 400: "#818cf8",
    500: "#6366f1", 600: "#4f46e5", 700: "#4338ca", 800: "#3730a3", 900: "#312e81",
    950: "#1e1b4b",
  },
  emerald: {
    50: "#ecfdf5", 100: "#d1fae5", 400: "#34d399", 500: "#10b981", 600: "#059669",
    700: "#047857", 900: "#064e3b", 950: "#022c22",
  },
  amber: {
    50: "#fffbeb", 100: "#fef3c7", 400: "#fbbf24", 500: "#f59e0b", 600: "#d97706",
    700: "#b45309", 900: "#78350f", 950: "#451a03",
  },
  orange: {
    50: "#fff7ed", 100: "#ffedd5", 400: "#fb923c", 500: "#f97316", 600: "#ea580c",
    700: "#c2410c", 900: "#7c2d12", 950: "#431407",
  },
  rose: {
    50: "#fff1f2", 100: "#ffe4e6", 400: "#fb7185", 500: "#f43f5e", 600: "#e11d48",
    700: "#be123c", 900: "#881337", 950: "#4c0519",
  },
  white: { 0: "#ffffff" },
};

function hsl(hex) {
  const n = parseInt(hex.slice(1), 16);
  const r = ((n >> 16) & 255) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  let h = 0, s = 0;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0));
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h /= 6;
  }
  const round = (x) => Math.round(x * 10) / 10;
  return `${round(h * 360)} ${round(s * 100)}% ${round(l * 100)}%`;
}

const c = (scale, step) => hsl(TW[scale][step]);

const LIGHT = {
  background: c("slate", 50),
  foreground: c("slate", 900),
  card: c("white", 0),
  "card-foreground": c("slate", 900),
  popover: c("white", 0),
  "popover-foreground": c("slate", 900),
  primary: c("indigo", 600),
  "primary-foreground": c("white", 0),
  secondary: c("slate", 100),
  "secondary-foreground": c("slate", 900),
  muted: c("slate", 100),
  "muted-foreground": c("slate", 500),
  accent: c("slate", 100),
  "accent-foreground": c("slate", 900),
  destructive: c("rose", 600),
  "destructive-foreground": c("white", 0),
  border: c("slate", 200),
  input: c("slate", 300),
  ring: c("indigo", 500),

  // Semantic, so a severity looks the same everywhere it appears.
  success: c("emerald", 600),
  "success-subtle": c("emerald", 50),
  "success-strong": c("emerald", 700),
  warning: c("amber", 500),
  "warning-subtle": c("amber", 50),
  "warning-strong": c("amber", 700),
  caution: c("orange", 500),
  "caution-subtle": c("orange", 50),
  "caution-strong": c("orange", 700),
  danger: c("rose", 600),
  "danger-subtle": c("rose", 50),
  "danger-strong": c("rose", 700),
  info: c("indigo", 600),
  "info-subtle": c("indigo", 50),
  "info-strong": c("indigo", 700),
};

const DARK = {
  background: c("slate", 950),
  foreground: c("slate", 100),
  card: c("slate", 900),
  "card-foreground": c("slate", 100),
  popover: c("slate", 900),
  "popover-foreground": c("slate", 100),
  primary: c("indigo", 500),
  "primary-foreground": c("slate", 950),
  secondary: c("slate", 800),
  "secondary-foreground": c("slate", 100),
  muted: c("slate", 800),
  "muted-foreground": c("slate", 400),
  accent: c("slate", 800),
  "accent-foreground": c("slate", 100),
  destructive: c("rose", 500),
  "destructive-foreground": c("slate", 950),
  border: c("slate", 800),
  input: c("slate", 700),
  ring: c("indigo", 400),

  success: c("emerald", 400),
  "success-subtle": c("emerald", 950),
  "success-strong": c("emerald", 400),
  warning: c("amber", 400),
  "warning-subtle": c("amber", 950),
  "warning-strong": c("amber", 400),
  caution: c("orange", 400),
  "caution-subtle": c("orange", 950),
  "caution-strong": c("orange", 400),
  danger: c("rose", 400),
  "danger-subtle": c("rose", 950),
  "danger-strong": c("rose", 400),
  info: c("indigo", 400),
  "info-subtle": c("indigo", 950),
  "info-strong": c("indigo", 400),
};

const block = (vars, indent) =>
  Object.entries(vars).map(([k, v]) => `${indent}--${k}: ${v};`).join("\n");

const css = `@tailwind base;
@tailwind components;
@tailwind utilities;

/* Generated by scripts/make-theme.mjs - edit the palette there, not here.
   Neutrals: Tailwind Slate. Accent: Indigo. Severities: Emerald, Amber,
   Orange, Rose, in that order of seriousness. */

@layer base {
  :root {
${block(LIGHT, "    ")}
    --radius: 0.5rem;
  }

  .dark {
${block(DARK, "    ")}
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1, "cv05" 1;
    -webkit-font-smoothing: antialiased;
  }
  /* Figures in a table or a metric should line up under each other. */
  .tabular, table, [data-metric] {
    font-variant-numeric: tabular-nums;
  }
  h1, h2, h3, h4 {
    letter-spacing: -0.011em;
  }
}

@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
`;

writeFileSync(new URL("../src/app/globals.css", import.meta.url), css);
console.log("wrote src/app/globals.css");
