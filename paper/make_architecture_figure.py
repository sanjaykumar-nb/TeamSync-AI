"""Draw Fig. 1 — the system architecture block diagram.

A block diagram, not a flowchart: every box is a subsystem that exists in the
deployed system, and every line is an interface between two of them. There are
no decisions, no start or end, and no ordering in time. The one place where
sequence genuinely is the contribution — the boundary that only the witness
subgraph crosses, and the path the risk scores take around it — is drawn as a
labelled interface as well, so the reader can see what is and is not allowed
to reach the language model.

Layout rules that keep it readable at print size:
  * three tiers stacked in a main column, stores and external systems in a
    right-hand column, so no line has to cross a tier to reach a store;
  * a routing gutter between the two columns and a second one inside the
    analysis tier, so every connector is orthogonal — no diagonals;
  * 516pt wide, the exact text width of an IEEE two-column page, so the figure
    is placed without rescaling and the 6-8pt labels stay at their true size.

    python paper/make_architecture_figure.py
"""
from __future__ import annotations

import html
from pathlib import Path

W, H = 516, 350

INK = "#1b1b1b"
RULE = "#7d7d7d"
SOFT = "#f5f5f5"
TIER_FILL = "#fcfcfc"
CORE_FILL = "#e9edf3"
NARR_FILL = "#f7f1e8"
ACCENT = "#1f4e79"
AMBER = "#8a5a12"
EXTERNAL = "#6f6f6f"
SANS = "Helvetica, Arial, sans-serif"

out: list[str] = []


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def rect(x, y, w, h, *, fill="#ffffff", stroke=INK, sw=0.9, rx=2.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def text(x, y, s, *, size=7.3, anchor="middle", fill=INK, weight="normal", style="normal"):
    out.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}" '
        f'text-anchor="{anchor}">{esc(s)}</text>'
    )


def vtext(x, y, s, *, size=6.6, weight="bold", fill="#444444"):
    out.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="middle" letter-spacing="0.6" '
        f'transform="rotate(-90 {x:.1f} {y:.1f})">{esc(s)}</text>'
    )


def block(x, y, w, h, title, sub=None, *, fill="#ffffff", stroke=INK, sw=0.9,
          dash=None, tsize=7.3):
    rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash)
    cx = x + w / 2
    if sub:
        text(cx, y + h / 2 - 1.0, title, size=tsize, weight="bold")
        text(cx, y + h / 2 + 8.0, sub, size=6.3, fill="#4f4f4f")
    else:
        text(cx, y + h / 2 + 2.5, title, size=tsize, weight="bold")


def poly(points, *, stroke=RULE, sw=0.9, dash=None, head=True, colour=None):
    """Orthogonal connector through a list of (x, y) way-points."""
    c = colour or stroke
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    marker = f' marker-end="url(#{"ahA" if c == ACCENT else "ah"})"' if head else ""
    out.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}"{da}{marker}/>')


def iface(x, y, s, *, anchor="start", size=6.2, fill="#3d3d3d"):
    """An interface label, on a white pad so it never fights a connector."""
    w = len(s) * size * 0.44 + 2.5
    x0 = {"start": x - 1.5, "end": x - w + 1.5, "middle": x - w / 2}[anchor]
    rect(x0, y - size + 0.4, w, size + 2.4, fill="#ffffff", stroke="#ffffff", sw=0, rx=1)
    text(x, y, s, size=size, anchor=anchor, fill=fill, style="italic")


# ------------------------------------------------------------------ canvas
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">')
out.append(
    '<defs>'
    '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{RULE}"/></marker>'
    '<marker id="ahA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{ACCENT}"/></marker>'
    '</defs>'
)
rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0, rx=0)

LBL = 11                 # centre of the rotated tier-label strip
MX0, MX1 = 22, 388       # main column
GUT = 398                # routing gutter between the columns
RX0, RX1 = 408, 510      # right column (stores and external systems)

T1_Y, T1_H = 8, 50
T2_Y, T2_H = 66, 82
T3_Y, T3_H = 156, 186

FRAMES: list[tuple[float, float, float, float]] = []

for name, ty, th, tech in [
    ("PRESENTATION", T1_Y, T1_H, "Next.js 14 · React 18"),
    ("APPLICATION", T2_Y, T2_H, "FastAPI · SQLAlchemy async"),
    ("ANALYSIS", T3_Y, T3_H, None),
]:
    rect(MX0, ty, MX1 - MX0, th, fill=TIER_FILL, stroke=RULE, sw=0.7, rx=3)
    FRAMES.append((MX0, ty, MX1 - MX0, th))
    vtext(LBL, ty + th / 2, name)
    if tech:
        text(MX1 - 5, ty + 9.5, tech, size=6.0, anchor="end", fill="#737373", style="italic")

# ------------------------------------------------------------------ tier 1
w1 = (MX1 - MX0 - 8 * 4) / 3
for i, (t, s) in enumerate([
    ("Kanban board", "tasks · dependencies"),
    ("Risk dashboard", "findings + evidence"),
    ("Project settings", "capacity · repository"),
]):
    block(MX0 + 8 + i * (w1 + 8), 20, w1, 28, t, s)

# ------------------------------------------------------------------ tier 2
w2 = (MX1 - MX0 - 8 * 5) / 4
for i, (t, s) in enumerate([
    ("Authentication", "JWT + refresh"),
    ("Tenant guard", "org-scoped rows"),
    ("Work items", "CRUD · board"),
    ("Repository sync", "commits · PRs"),
]):
    block(MX0 + 8 + i * (w2 + 8), 78, w2, 27, t, s)

w2b = (MX1 - MX0 - 8 * 3) / 2
block(MX0 + 8, 112, w2b, 28, "Analysis orchestrator", "assembles the project snapshot")
block(MX0 + 16 + w2b, 112, w2b, 28, "Evidence recorder", "persists findings, scores, witness")

# ------------------------------------------------------------------ tier 3
IN0, IN1 = MX0 + 8, MX1 - 46      # sub-boxes stop short: right lane is for return paths
LANE_A, LANE_B = MX1 - 36, MX1 - 16

core_y, core_h = 176, 60
narr_y, narr_h = 268, 56

rect(IN0, core_y, IN1 - IN0, core_h, fill=CORE_FILL, stroke=INK, sw=1.0, rx=3)
text(IN0 + 6, core_y + 11.5, "DETERMINISTIC CORE — no model call, no randomness",
     size=6.3, anchor="start", weight="bold", fill=ACCENT)
w3 = (IN1 - IN0 - 10 * 4) / 3
core_boxes = []
for i, (t, s) in enumerate([
    ("Graph compiler", "typed nodes, 9 edge kinds"),
    ("Risk metric bank", "six graph algorithms"),
    ("Witness selector", "1 hop · ≤8/seed · ≤60"),
]):
    x = IN0 + 10 + i * (w3 + 10)
    block(x, core_y + 18, w3, 32, t, s)
    core_boxes.append((x, w3))

rect(IN0, narr_y, IN1 - IN0, narr_h, fill=NARR_FILL, stroke=INK, sw=1.0, rx=3)
text(IN0 + 6, narr_y + 11.5, "NARRATION LAYER — bounded prompt, checked afterwards",
     size=6.3, anchor="start", weight="bold", fill=AMBER)
narr_boxes = []
for i, (t, s) in enumerate([
    ("Prompt assembler", "columnar serialisation"),
    ("Model adapter", "LLM, or rule fallback"),
    ("Grounding verifier", "drops unresolvable ids"),
]):
    x = IN0 + 10 + i * (w3 + 10)
    block(x, narr_y + 17, w3, 31, t, s)
    narr_boxes.append((x, w3))

# in-tier chaining
for row_y, boxes in ((core_y + 34, core_boxes), (narr_y + 32.5, narr_boxes)):
    for i in range(2):
        x0 = boxes[i][0] + boxes[i][1]
        poly([(x0, row_y), (x0 + 10, row_y)])

# ------------------------------------------------------------------ right column
rect(RX0 - 4, 72, (RX1 + 2) - (RX0 - 4), 76, fill=TIER_FILL, stroke=RULE, sw=0.7, rx=3)
FRAMES.append((RX0 - 4, 72, (RX1 + 2) - (RX0 - 4), 76))
text((RX0 + RX1) / 2, 81, "STORES", size=6.0, weight="bold", fill="#737373")
block(RX0, 86, RX1 - RX0, 26, "PostgreSQL 16", "system of record")
block(RX0, 116, RX1 - RX0, 26, "Redis + Celery", "cache · scheduled runs")

rect(RX0 - 4, 196, (RX1 + 2) - (RX0 - 4), 82, fill=TIER_FILL, stroke=RULE, sw=0.7, rx=3)
FRAMES.append((RX0 - 4, 196, (RX1 + 2) - (RX0 - 4), 82))
text((RX0 + RX1) / 2, 205, "EXTERNAL", size=6.0, weight="bold", fill="#737373")
block(RX0, 210, RX1 - RX0, 26, "Git host", "webhooks · REST",
      stroke=EXTERNAL, dash="3 2", fill=SOFT)
block(RX0, 242, RX1 - RX0, 26, "LLM provider", "optional — absent ⇒ fallback",
      stroke=EXTERNAL, dash="3 2", fill=SOFT)

# ------------------------------------------------------------------ interfaces
# presentation <-> application
poly([(MX0 + 8 + w1 / 2, 48), (MX0 + 8 + w1 / 2, 78)])
iface(MX0 + 12 + w1 / 2, 64, "HTTPS · bearer token")
poly([(MX0 + 16 + 2.5 * w1, 78), (MX0 + 16 + 2.5 * w1, 48)])
iface(MX0 + 12 + 2.5 * w1, 64, "board + findings", anchor="end")

# application -> analysis (snapshot in)
poly([(MX0 + 8 + w2b / 2, 140), (MX0 + 8 + w2b / 2, core_y)])
iface(MX0 + 12 + w2b / 2, 150, "project snapshot (internal REST)")

# analysis -> application, up the right-hand lane inside the tier
poly([(IN1, narr_y + 32.5), (LANE_A, narr_y + 32.5), (LANE_A, 140)], colour=RULE)
iface(LANE_A - 4, 148, "verified finding", anchor="end")
iface(LANE_A - 4, 155.5, "+ evidence", anchor="end")

poly([(IN1, core_y + 34), (LANE_B, core_y + 34), (LANE_B, 140)], dash="4 2.5")
iface(LANE_B + 5, 148, "risk scores,")
iface(LANE_B + 5, 155.5, "never via the model")

# the single crossing
wx = core_boxes[2][0] + core_boxes[2][1] / 2
poly([(wx, core_y + core_h), (wx, narr_y)], colour=ACCENT, sw=1.6)
iface(wx - 8, (core_y + core_h + narr_y) / 2 + 2.5,
      "witness subgraph — the only thing that crosses", anchor="end", fill=ACCENT, size=6.3)

# stores
poly([(MX1, 99), (RX0 - 4, 99)], head=False)
poly([(MX1, 129), (RX0 - 4, 129)], head=False)

# git host -> repository sync, up the gutter
poly([(RX0 - 4, 223), (GUT, 223), (GUT, 92), (MX1, 92)], dash="3 2")

# model adapter -> llm provider, out through the gutter
mx = narr_boxes[1][0] + narr_boxes[1][1] / 2
poly([(mx, narr_y + narr_h), (mx, narr_y + narr_h + 8), (GUT - 4, narr_y + narr_h + 8),
      (GUT - 4, 255), (RX0 - 4, 255)], dash="3 2")

for fx, fy, fw, fh in FRAMES:
    rect(fx, fy, fw, fh, fill="none", stroke=RULE, sw=0.7, rx=3)

text(IN0 + 2, T3_Y + T3_H - 7, "FastAPI · NetworkX · pluggable model adapter",
     size=6.0, anchor="start", fill="#737373", style="italic")

out.append("</svg>")

dest = Path(__file__).resolve().parent / "figures" / "fig1_architecture_blocks.svg"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dest} ({dest.stat().st_size:,} bytes)")
