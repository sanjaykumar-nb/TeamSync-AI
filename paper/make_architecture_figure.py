"""Draw Fig. 1 — the system architecture block diagram.

A block diagram, not a flowchart: every box is a subsystem that exists in the
deployed system and every line is an interface between two of them. There are
no decisions, no start or end, and no ordering in time.

The analysis tier is drawn as three bands because that is where the paper's
claims live. The deterministic core computes every number without a model. The
agent layer runs the specialists and aggregates what they return. The narration
layer is the only place a language model may be called, and the only thing that
reaches it is one finding and its witness subgraph — drawn as the single heavy
connector, with the risk scores dashed around the outside to show they never
pass through it.

Layout rules that keep it readable at print size:
  * three tiers in a main column, stores and external systems in a right-hand
    column, so no connector has to cross a tier to reach a store;
  * a routing gutter between the columns and two return lanes inside the
    analysis tier, so every connector is orthogonal — no diagonals;
  * 516pt wide, the exact text width of an IEEE two-column page, so the figure
    is placed without rescaling and the 6-8pt labels keep their true size.

    python paper/make_architecture_figure.py
"""
from __future__ import annotations

import html
from pathlib import Path

W, H = 516, 408

INK = "#1b1b1b"
RULE = "#7d7d7d"
SOFT = "#f5f5f5"
TIER_FILL = "#fcfcfc"
CORE_FILL = "#e8edf4"
AGENT_FILL = "#edf1ea"
NARR_FILL = "#f8f1e7"
ACCENT = "#1f4e79"
AMBER = "#8a5a12"
GREEN = "#3b5c39"
EXTERNAL = "#6f6f6f"
SANS = "Helvetica, Arial, sans-serif"

out: list[str] = []
FRAMES: list[tuple[float, float, float, float]] = []


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def rect(x, y, w, h, *, fill="#ffffff", stroke=INK, sw=0.9, rx=2.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def text(x, y, s, *, size=7.2, anchor="middle", fill=INK, weight="normal", style="normal"):
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


def block(x, y, w, h, title, sub=None, sub2=None, *, fill="#ffffff", stroke=INK,
          sw=0.9, dash=None, tsize=7.2):
    rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash)
    cx = x + w / 2
    if sub2:
        text(cx, y + h / 2 - 5.0, title, size=tsize, weight="bold")
        text(cx, y + h / 2 + 3.4, sub, size=6.0, fill="#4f4f4f")
        text(cx, y + h / 2 + 11.0, sub2, size=6.0, fill="#4f4f4f")
    elif sub:
        text(cx, y + h / 2 - 1.2, title, size=tsize, weight="bold")
        text(cx, y + h / 2 + 7.4, sub, size=6.0, fill="#4f4f4f")
    else:
        text(cx, y + h / 2 + 2.4, title, size=tsize, weight="bold")


def poly(points, *, stroke=RULE, sw=0.9, dash=None, head=True, colour=None):
    c = colour or stroke
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    marker = f' marker-end="url(#{"ahA" if c == ACCENT else "ah"})"' if head else ""
    out.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}"{da}{marker}/>')


def iface(x, y, s, *, anchor="start", size=6.1, fill="#3d3d3d"):
    """An interface label on a white pad, so it never fights a connector."""
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

LBL = 11
MX0, MX1 = 22, 388
GUT = 398
RX0, RX1 = 408, 510

T1_Y, T1_H = 8, 48
T2_Y, T2_H = 64, 80
T3_Y, T3_H = 156, 214

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
    block(MX0 + 8 + i * (w1 + 8), 19, w1, 27, t, s)

# ------------------------------------------------------------------ tier 2
w2 = (MX1 - MX0 - 8 * 5) / 4
for i, (t, s) in enumerate([
    ("Authentication", "JWT + refresh"),
    ("Tenant guard", "org-scoped rows"),
    ("Work items", "CRUD · board"),
    ("Repository sync", "commits · PRs"),
]):
    block(MX0 + 8 + i * (w2 + 8), 76, w2, 26, t, s)

w2b = (MX1 - MX0 - 8 * 3) / 2
block(MX0 + 8, 109, w2b, 27, "Analysis orchestrator", "assembles the project snapshot")
block(MX0 + 16 + w2b, 109, w2b, 27, "Evidence recorder", "persists findings, scores, witness")

# ------------------------------------------------------------------ tier 3
IN0, IN1 = MX0 + 8, MX1 - 46
LANE_A, LANE_B = MX1 - 36, MX1 - 16

CORE_Y, CORE_H = 170, 58
AGENT_Y, AGENT_H = 242, 52
NARR_Y, NARR_H = 308, 50

rect(IN0, CORE_Y, IN1 - IN0, CORE_H, fill=CORE_FILL, stroke=INK, sw=1.0, rx=3)
text(IN0 + 6, CORE_Y + 11, "1 — DETERMINISTIC CORE · no model call, no fitted parameter",
     size=6.2, anchor="start", weight="bold", fill=ACCENT)
w3 = (IN1 - IN0 - 10 * 4) / 3
core = []
for i, (t, s, s2) in enumerate([
    ("Graph compiler", "5 node types, 9 edge kinds", "from tables already kept"),
    ("Risk metric bank", "critical path · betweenness", "articulation · degree · ratios"),
    ("Witness selector", "1 hop · ≤ 8 per seed", "≤ 60 nodes, seeds kept"),
]):
    x = IN0 + 10 + i * (w3 + 10)
    block(x, CORE_Y + 16, w3, 36, t, s, s2)
    core.append((x, w3))

rect(IN0, AGENT_Y, IN1 - IN0, AGENT_H, fill=AGENT_FILL, stroke=INK, sw=1.0, rx=3)
text(IN0 + 6, AGENT_Y + 11, "2 — AGENT LAYER · one output schema on either path",
     size=6.2, anchor="start", weight="bold", fill=GREEN)
w4 = (IN1 - IN0 - 8 * 6) / 5
agents = []
for i, t in enumerate(["Coordinator", "Planning", "Progress", "Workload", "Risk + action"]):
    x = IN0 + 8 + i * (w4 + 8)
    block(x, AGENT_Y + 17, w4, 25, t, tsize=6.4)
    agents.append((x, w4))

rect(IN0, NARR_Y, IN1 - IN0, NARR_H, fill=NARR_FILL, stroke=INK, sw=1.0, rx=3)
text(IN0 + 6, NARR_Y + 11, "3 — NARRATION LAYER · the only place a model is called",
     size=6.2, anchor="start", weight="bold", fill=AMBER)
narr = []
for i, (t, s) in enumerate([
    ("Prompt assembler", "columnar serialisation"),
    ("Model adapter", "LLM, or rule fallback"),
    ("Grounding verifier", "drops unresolvable ids"),
]):
    x = IN0 + 10 + i * (w3 + 10)
    block(x, NARR_Y + 16, w3, 28, t, s)
    narr.append((x, w3))

for row_y, boxes in ((CORE_Y + 34, core), (NARR_Y + 30, narr)):
    for i in range(2):
        x0 = boxes[i][0] + boxes[i][1]
        poly([(x0, row_y), (x0 + 10, row_y)])
for i in range(4):
    x0 = agents[i][0] + agents[i][1]
    poly([(x0, AGENT_Y + 29.5), (x0 + 8, AGENT_Y + 29.5)], head=(i in (0, 3)))

# ------------------------------------------------------------------ right column
rect(RX0 - 4, 70, (RX1 + 2) - (RX0 - 4), 74, fill=TIER_FILL, stroke=RULE, sw=0.7, rx=3)
FRAMES.append((RX0 - 4, 70, (RX1 + 2) - (RX0 - 4), 74))
text((RX0 + RX1) / 2, 79, "STORES", size=6.0, weight="bold", fill="#737373")
block(RX0, 84, RX1 - RX0, 25, "PostgreSQL 16", "system of record")
block(RX0, 113, RX1 - RX0, 25, "Redis + Celery", "cache · scheduled runs")

rect(RX0 - 4, 196, (RX1 + 2) - (RX0 - 4), 80, fill=TIER_FILL, stroke=RULE, sw=0.7, rx=3)
FRAMES.append((RX0 - 4, 196, (RX1 + 2) - (RX0 - 4), 80))
text((RX0 + RX1) / 2, 205, "EXTERNAL", size=6.0, weight="bold", fill="#737373")
block(RX0, 210, RX1 - RX0, 25, "Git host", "webhooks · REST",
      stroke=EXTERNAL, dash="3 2", fill=SOFT)
block(RX0, 240, RX1 - RX0, 25, "LLM provider", "optional ⇒ fallback",
      stroke=EXTERNAL, dash="3 2", fill=SOFT)

# ------------------------------------------------------------------ interfaces
poly([(MX0 + 8 + w1 / 2, 46), (MX0 + 8 + w1 / 2, 76)])
iface(MX0 + 12 + w1 / 2, 62, "HTTPS · bearer token")
poly([(MX0 + 16 + 2.5 * w1, 76), (MX0 + 16 + 2.5 * w1, 46)])
iface(MX0 + 12 + 2.5 * w1, 62, "board + findings", anchor="end")

poly([(MX0 + 8 + w2b / 2, 136), (MX0 + 8 + w2b / 2, CORE_Y)])
iface(MX0 + 12 + w2b / 2, 148, "project snapshot (internal REST)")

ax = core[1][0] + core[1][1] / 2
poly([(ax, CORE_Y + CORE_H), (ax, AGENT_Y)])
iface(ax + 5, (CORE_Y + CORE_H + AGENT_Y) / 2 + 2.4, "six risk scores + graph metrics")

wx = narr[2][0] + narr[2][1] / 2
poly([(wx, AGENT_Y + AGENT_H), (wx, NARR_Y)], colour=ACCENT, sw=1.7)
iface(wx - 7, (AGENT_Y + AGENT_H + NARR_Y) / 2 + 2.4,
      "one finding + its witness subgraph — all that crosses",
      anchor="end", fill=ACCENT, size=6.2)

bx = narr[0][0] + narr[0][1] / 2
poly([(bx, NARR_Y), (bx, AGENT_Y + AGENT_H)])
iface(bx + 5, NARR_Y - 5, "verified prose")

poly([(IN1, AGENT_Y + 26), (LANE_A, AGENT_Y + 26), (LANE_A, 136)])
iface(LANE_A - 4, 151.5, "agent output + evidence", anchor="end")

poly([(IN1, CORE_Y + 34), (LANE_B, CORE_Y + 34), (LANE_B, 136)], dash="4 2.5")
iface(LANE_B + 5, 151.5, "risk scores, never via a model")

poly([(MX1, 96), (RX0 - 4, 96)], head=False)
poly([(MX1, 126), (RX0 - 4, 126)], head=False)

poly([(RX0 - 4, 222), (GUT, 222), (GUT, 89), (MX1, 89)], dash="3 2")

mx = narr[1][0] + narr[1][1] / 2
poly([(mx, NARR_Y + NARR_H), (mx, NARR_Y + NARR_H + 8), (GUT - 4, NARR_Y + NARR_H + 8),
      (GUT - 4, 252), (RX0 - 4, 252)], dash="3 2")

# ------------------------------------------------------------------ legend
LY = H - 18
rect(MX0, LY - 10, (RX1 + 2) - MX0, 18, fill="#ffffff", stroke=RULE, sw=0.6, rx=2)
lx = MX0 + 8
out.append(f'<line x1="{lx}" y1="{LY}" x2="{lx + 15}" y2="{LY}" stroke="{RULE}" stroke-width="0.9" marker-end="url(#ah)"/>')
text(lx + 19, LY + 2.1, "interface between subsystems", size=6.1, anchor="start")
lx += 130
out.append(f'<line x1="{lx}" y1="{LY}" x2="{lx + 15}" y2="{LY}" stroke="{ACCENT}" stroke-width="1.7" marker-end="url(#ahA)"/>')
text(lx + 19, LY + 2.1, "the witness-subgraph boundary", size=6.1, anchor="start", fill=ACCENT)
lx += 138
out.append(f'<line x1="{lx}" y1="{LY}" x2="{lx + 15}" y2="{LY}" stroke="{RULE}" stroke-width="0.9" stroke-dasharray="3 2" marker-end="url(#ah)"/>')
text(lx + 19, LY + 2.1, "optional or external", size=6.1, anchor="start")

for fx, fy, fw, fh in FRAMES:
    rect(fx, fy, fw, fh, fill="none", stroke=RULE, sw=0.7, rx=3)

text(IN0 + 2, T3_Y + T3_H - 6, "FastAPI · NetworkX · pluggable model adapter",
     size=6.0, anchor="start", fill="#737373", style="italic")

out.append("</svg>")

dest = Path(__file__).resolve().parent / "figures" / "fig1_architecture_blocks.svg"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dest} ({dest.stat().st_size:,} bytes)")
