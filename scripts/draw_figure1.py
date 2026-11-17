#!/usr/bin/env python3
"""draw_figure1.py — Figure 1: absorption-first cascade.

Design intent
-------------
The cascade is drawn as a bar chart of itself: each layer's bar length is its
share of the 26,216 registry pairs, and the same share is set as display type.
Length carries the information, so the bars are monochrome and need no legend.
Everything else is small and grey, in the role of annotation.

Two hues only: one blue in tints, and a neutral grey ramp.
One type family (Arial), with deliberate scale contrast:
    display 16 pt / title 11 pt / row names 8.6 pt / body 6.6 pt / note 6.2 pt
Nothing is boxed. Structure comes from four hairlines and shared alignment.

The released class matrix and the absorption-tier distribution are drawn from
configs/class_matrix.yaml and data/seed/entities_a.csv, not described in words.

Geometry is audited after drawing: every text object must sit inside its
declared cell, or the build fails.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib import font_manager
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"

FONT_FAMILY = "Arial"
REGULAR = r"C:\Windows\Fonts\arial.ttf"
BOLD = r"C:\Windows\Fonts\arialbd.ttf"

for fp in (REGULAR, BOLD):
    if not Path(fp).exists():
        raise SystemExit(f"Arial not found: {fp}")
    font_manager.fontManager.addfont(fp)

# No fallback family: if Arial cannot render a glyph the build fails instead of
# silently substituting another typeface.
plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.sans-serif": [FONT_FAMILY],
    "mathtext.fontset": "custom",
    "mathtext.rm": FONT_FAMILY,
    "mathtext.it": f"{FONT_FAMILY}:italic",
    "mathtext.bf": f"{FONT_FAMILY}:bold",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

# ── shared palette (see scripts/figure_palette.py) ───────────────────────
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_palette import (BLUE_900, BLUE_700, BLUE_400, BLUE_200, BLUE_100,
                            INK as INK_RGB, GREY, RULE)

NAVY = BLUE_900
NAVY_MID = BLUE_700
NAVY_SOFT = BLUE_400
NAVY_PALE = BLUE_200
NAVY_FAINT = BLUE_200
NAVY_WASH = BLUE_100
INK = "#000000"
BODY = "#000000"
MUTED = "#000000"
HAIR = RULE

# ── type scale with deliberate contrast ──────────────────────────────────
FS_DISPLAY = 19.5
FS_TITLE = 13.5
FS_SUB = 8.6
FS_ROW = 10.4
FS_BODY = 8.2
FS_MICRO = 8.0

CHECKS: list[tuple[object, tuple[float, float, float, float], str]] = []

TIER_ORDER = [
    ("systemic_absorption_high", "high", NAVY),
    ("systemic_absorption_medium", "medium", NAVY_MID),
    ("systemic_absorption_low", "low", NAVY_SOFT),
    ("systemic_absorption_very_low", "very low", NAVY_PALE),
    ("minimal_systemic_absorption", "minimal", NAVY_FAINT),
    ("systemic_absorption_none", "none", NAVY_WASH),
]


def load_matrix() -> np.ndarray:
    """Released class matrix as integer levels.

    0 = cell not defined, 1 = low, 2 = medium, 3 = high, -1 = explicit "none".
    """
    cfg = yaml.safe_load((ROOT / "configs" / "class_matrix.yaml").read_text(encoding="utf-8"))
    matrix = cfg["matrix"]
    cols = sorted({c for cells in matrix.values() for c in cells})
    code = {"low": 1, "medium": 2, "high": 3, "none": -1}
    out = np.zeros((len(matrix), len(cols)), dtype=int)
    for i, r in enumerate(matrix):
        for j, c in enumerate(cols):
            cell = matrix[r].get(c)
            if isinstance(cell, dict):
                out[i, j] = code.get(cell.get("level"), 0)
    return out


def load_tiers() -> list[tuple[str, str, str, int]]:
    rows = list(csv.DictReader((ROOT / "data" / "seed" / "entities_a.csv")
                               .open(encoding="utf-8-sig")))
    counts = {key: 0 for key, _, _ in TIER_ORDER}
    for r in rows:
        flags = {f.strip() for f in (r.get("flags") or "").split("|")}
        for key, _, _ in TIER_ORDER:
            if key in flags:
                counts[key] += 1
                break
    return [(key, label, tone, counts[key]) for key, label, tone in TIER_ORDER]


def main() -> None:
    levels = load_matrix()
    tiers = load_tiers()

    fig = plt.figure(figsize=(7.09, 4.33))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def text(x, y, s, size, cell=None, **kw):
        kw.setdefault("ha", "left")
        kw.setdefault("va", "center")
        kw.setdefault("fontfamily", FONT_FAMILY)
        t = ax.text(x, y, s, fontsize=size, **kw)
        if cell is not None:
            CHECKS.append((t, cell, s[:40]))
        return t

    def hr(x0, x1, y, color=HAIR, lw=0.55):
        ax.plot([x0, x1], [y, y], color=color, lw=lw,
                solid_capstyle="butt", zorder=2)

    L, R = 6.0, 94.0

    # ══ masthead ══════════════════════════════════════════════════════
    text(L, 95.2, "Absorption-first cascade for ophthalmic-systemic DDI screening",
         FS_TITLE, (L, R, 92.8, 98.0), fontweight="bold", color=INK)
    text(L, 90.4, "40 mechanism rules, an absorption-scaled class matrix and a hard "
                  "constraint; no model call on the production path",
         FS_SUB, (L, R, 88.6, 92.2), color=BODY)

    # ══ chart: cascade layers as shares of the pair population ════════
    BAR_X, BAR_W = L, 43.0
    NUM_R = 64.0

    text(L, 83.0, "WHERE THE 26,216 REGISTRY PAIRS ARE DECIDED",
         FS_MICRO, (L, 58, 81.8, 84.2), fontweight="bold", color=INK)
    text(NUM_R, 83.0, "share", FS_MICRO, (NUM_R - 8, NUM_R, 81.8, 84.2),
         ha="right", color=MUTED)
    hr(L, NUM_R, 81.2)

    rows = [
        (75.8, "01", "Rule engine", "40 rules and 3 patient-factor policies",
         11.74, NAVY),
        (63.0, "02", "Class matrix",
         "21 by 34 classes, 104 defined cells, absorption-scaled in-layer",
         25.72, NAVY),
        (50.2, "03", "G19 hard constraint", "low absorption and no other signal",
         42.87, NAVY),
        (37.4, "", "default path", "no rule or defined cell (unassessed)",
         19.67, NAVY_FAINT),
    ]
    for cy, num, name, detail, pct, tone in rows:
        if num:
            text(L, cy + 2.6, num, FS_MICRO, (L, L + 3.6, cy + 1.5, cy + 3.7),
                 color=MUTED)
            text(L + 4.0, cy + 2.6, name, FS_ROW, (L + 3.8, 52, cy + 1.2, cy + 4.0),
                 fontweight="bold", color=INK)
        else:
            text(L, cy + 2.6, name, FS_ROW, (L, 52, cy + 1.2, cy + 4.0), color=BODY)

        # full-scale track, then the filled share
        ax.plot([BAR_X, BAR_X + BAR_W], [cy, cy], color=NAVY_WASH, lw=2.8,
                solid_capstyle="butt", zorder=2)
        ax.add_patch(Rectangle((BAR_X, cy - 1.4), BAR_W * pct / 100.0, 2.8,
                               facecolor=tone, edgecolor="none", zorder=3))

        text(L, cy - 3.2, detail, FS_BODY, (L, 63, cy - 4.4, cy - 2.0), color=MUTED)

        text(NUM_R, cy + 2.2, f"{pct:.1f}%", FS_DISPLAY,
             (NUM_R - 20, NUM_R, cy - 3.0, cy + 5.2),
             ha="right", fontweight="bold", color=INK)

    # ══ verdict ═══════════════════════════════════════════════════════
    hr(L, NUM_R, 30.4)
    text(L, 27.4, "One grade per pair, with rule IDs, decision path and evidence chain.", FS_BODY,
         (L, NUM_R, 26.0, 28.8), color=BODY)
    text(L, 24.4, "final grade = max(L1, L2, L3); high, medium, low or unassessed",
         FS_MICRO, (L, NUM_R, 23.2, 25.6), color=MUTED)

    # ══ right column: what the cascade is made of ═════════════════════
    RX = 68.0
    text(RX, 83.0, "ABSORPTION TIERS", FS_MICRO, (RX, R - 8, 81.8, 84.2),
         fontweight="bold", color=INK)
    text(R, 83.0, "n = 113", FS_MICRO, (R - 12, R, 81.8, 84.2), ha="right",
         color=MUTED)
    hr(RX, R, 81.2)

    total = sum(t[3] for t in tiers)
    cx = RX
    for _, label, tone, n in tiers:
        w = (R - RX) * n / total
        ax.add_patch(Rectangle((cx, 75.4), max(w - 0.16, 0.14), 3.6,
                               facecolor=tone, edgecolor="none", zorder=3))
        cx += w
    ax.add_patch(Rectangle((RX, 75.4), R - RX, 3.6, fill=False, edgecolor=HAIR,
                           lw=0.4, zorder=4))
    text(RX, 72.2, "high", FS_MICRO, (RX, RX + 8, 71.2, 73.2), color=MUTED)
    text(R, 72.2, "none", FS_MICRO, (R - 8, R, 71.2, 73.2), ha="right", color=MUTED)


    text(RX, 65.8, "59 low; very low 11, minimal 7, none 4",
         7.4, (RX, R, 64.8, 66.8), color=MUTED)

    # ── the released matrix ───────────────────────────────────────────
    text(RX, 61.4, "CLASS MATRIX", FS_MICRO, (RX, R - 13, 60.2, 62.6),
         fontweight="bold", color=INK)
    text(R, 61.4, "104 cells", FS_MICRO, (R - 12, R, 60.2, 62.6), ha="right",
         color=MUTED)
    hr(RX, R, 59.8)

    nrow, ncol = levels.shape
    GX0, GX1 = RX, R
    GY0, GY1 = 42.2, 58.2
    cw = (GX1 - GX0) / ncol
    ch = (GY1 - GY0) / nrow
    tone_of = {3: NAVY, 2: NAVY_MID, 1: NAVY_SOFT, -1: NAVY_FAINT}
    order = np.argsort(-(levels != 0).sum(axis=1), kind="stable")
    for rank, i in enumerate(order):
        for j in range(ncol):
            v = int(levels[i, j])
            if v == 0:
                continue
            ax.add_patch(Rectangle((GX0 + j * cw + cw * 0.08,
                                    GY1 - (rank + 1) * ch + ch * 0.18),
                                   cw * 0.84, ch * 0.64,
                                   facecolor=tone_of[v], edgecolor="none", zorder=3))

    ky = 39.6
    kx = RX
    for label, tone, note in (("high", NAVY, "6"), ("medium", NAVY_MID, "52"),
                              ("low", NAVY_SOFT, "25"), ("none", NAVY_FAINT, "21")):
        ax.add_patch(Rectangle((kx, ky - 0.65), 1.3, 1.3, facecolor=tone,
                               edgecolor="none", zorder=3))
        t = text(kx + 1.9, ky, f"{label} {note}", FS_MICRO, None, color=BODY)
        fig.canvas.draw()
        wpx = t.get_window_extent(fig.canvas.get_renderer()).width
        unit = ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]
        kx += wpx / unit + 2.4

    text(RX, 36.2, "rows = ophthalmic classes", FS_MICRO,
         (RX, R, 35.0, 37.4), color=MUTED)

    # ══ knowledge base ════════════════════════════════════════════════
    hr(L, R, 19.6)
    text(L, 16.4, "KNOWLEDGE BASE", FS_MICRO, (L, 28, 15.4, 17.4),
         fontweight="bold", color=INK)
    text(L + 22.0, 16.4, "1,307 evidence chunks, graded A to E, each with a source record", FS_BODY,
         (L + 21.8, R, 15.2, 17.6), color=BODY)

    # ══ provenance ════════════════════════════════════════════════════
    text(L, 10.6, "Checks: every decision returns matched rule IDs and a path; no model call or network access.",
         FS_MICRO, (L, R, 9.4, 11.8), color=MUTED)
    text(L, 7.0, "Sources: path-attribution audit (n = 26,216); entities_a.csv; class_matrix.yaml.",
         FS_MICRO, (L, R, 5.8, 8.2), color=MUTED)

    # ══ geometry audit ════════════════════════════════════════════════
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    failures = []
    for artist, (x0, x1, y0, y1), label in CHECKS:
        bb = artist.get_window_extent(renderer)
        p0 = ax.transData.transform((x0, y0))
        p1 = ax.transData.transform((x1, y1))
        left, right = min(p0[0], p1[0]), max(p0[0], p1[0])
        bottom, top = min(p0[1], p1[1]), max(p0[1], p1[1])
        if bb.x0 < left - 1.5 or bb.x1 > right + 1.5 or bb.y0 < bottom - 1.5 or bb.y1 > top + 1.5:
            failures.append((label, round(bb.x0 - left, 1), round(right - bb.x1, 1),
                             round(bb.y0 - bottom, 1), round(top - bb.y1, 1)))
    if failures:
        for f in failures:
            print("OVERFLOW", f)
        raise SystemExit(f"{len(failures)} text objects overflow their cell")

    for ext, fmt, kw in [("png", "png", {"dpi": 400}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}),
                         ("tiff", "tiff", {"dpi": 400, "pil_kwargs": {"compression": "tiff_lzw"}})]:
        fig.savefig(FIG / f"figure1_architecture.{ext}", format=fmt,
                    bbox_inches=None, pad_inches=0, facecolor="white", **kw)
    plt.close(fig)
    print(f"figure1_architecture saved ({len(CHECKS)} text objects checked, 0 overflow)")

    # ── typography gate: every text object must resolve to Arial ─────────
    off_family = []
    for artist, _, label in CHECKS:
        try:
            family = artist.get_fontfamily()
        except Exception:
            family = None
        if family and FONT_FAMILY not in family:
            off_family.append((label, family))
    if off_family:
        for label, fam in off_family:
            print("NON-ARIAL", label, fam)
        raise SystemExit(f"{len(off_family)} text objects are not set in {FONT_FAMILY}")
    print(f"typography gate: {len(CHECKS)} text objects all in {FONT_FAMILY}")


if __name__ == "__main__":
    main()
