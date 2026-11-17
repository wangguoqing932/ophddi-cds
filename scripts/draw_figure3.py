# -*- coding: utf-8 -*-
"""draw_figure3.py — Figure 3: expert grade review.

Layout
------
(a) Agreement coefficients as a horizontal grouped bar chart: five comparisons
    as rows, three metrics each. Value labels sit at the bar ends, upright and
    horizontal, so nothing is rotated or pushed under the axis.
(b) Per-case grades as a categorical dot plot. The four series are offset
    horizontally within each case so that coincident judgments stay visible;
    in the previous version the two experts overlapped on 11 of 12 cases and
    one series was completely hidden.

Typography: Arial only, 8 pt floor, 180 mm canvas (Frontiers).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"

for fp in [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    try:
        font_manager.fontManager.addfont(fp)
    except Exception:
        pass

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],
    "font.size": 8,
    "axes.titlesize": 9.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 8,
    "axes.linewidth": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

LV = {"low": 1, "medium": 2, "high": 3}

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_palette import BLUE_900, BLUE_700, BLUE_400, AMBER, GREEN, BROWN, INK, RULE

C_KAPPA = BLUE_900
C_WEIGHTED = BLUE_700
C_AGREE = BLUE_400


def main() -> None:
    r = json.load((ROOT / "outputs" / "recomputed" /
                   "expert_review_recomputed.json").open(encoding="utf-8"))

    keys = ["inter_rater", "e1_vs_system_shown", "e2_vs_system_shown",
            "e1_vs_gold_shown", "e2_vs_gold_shown"]
    labels = ["Inter-rater\n(E1 vs E2)", "Expert 1\nvs displayed",
              "Expert 2\nvs displayed", "Expert 1\nvs reference",
              "Expert 2\nvs reference"]
    kappa = [r[k]["kappa"] for k in keys]
    wq = [r[k]["kappa_weighted_quadratic"] for k in keys]
    agree = [r[k]["agreement"] for k in keys]

    per = r["per_case"]
    ids = [p["case_id"] for p in per]

    fig = plt.figure(figsize=(7.09, 4.15))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.42],
                          left=0.20, right=0.985, top=0.88, bottom=0.34,
                          wspace=0.50)

    # ── (a) horizontal grouped bars ──────────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    n = len(keys)
    h = 0.26
    ypos = list(range(n))[::-1]
    series = [("Cohen kappa", kappa, C_KAPPA),
              ("Weighted kappa", wq, C_WEIGHTED),
              ("Raw agreement", agree, C_AGREE)]
    for i, (name, vals, colour) in enumerate(series):
        off = (i - 1) * h
        ax.barh([y + off for y in ypos], vals, height=h * 0.90, color=colour,
                label=name, zorder=3)
        for y, v in zip(ypos, vals):
            ax.text(v + (0.035 if v >= 0 else -0.035), y + off, f"{v:.2f}",
                    va="center", ha="left" if v >= 0 else "right",
                    fontsize=8, color=INK, zorder=4)

    ax.axvline(0, color=INK, lw=0.8, zorder=2)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(-0.60, 1.30)
    ax.set_xticks([-0.5, 0.0, 0.5, 1.0])
    ax.set_xlabel("Value", fontsize=8)
    ax.set_title("(a) Agreement coefficients", loc="left", pad=6)
    ax.grid(axis="x", color=RULE, lw=0.5, zorder=1)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=3,
              handlelength=0.9, handletextpad=0.35, columnspacing=0.8,
              fontsize=8.0)

    # ── (b) per-case dot plot, four lanes ───────────────────────────────
    bx = fig.add_subplot(gs[0, 1])
    gold = [LV[p["gold_shown"]] for p in per]
    shown = [LV[p["system_shown"]] for p in per]
    e1 = [LV[p["expert_1"]] for p in per]
    e2 = [LV[p["expert_2"]] for p in per]

    xs = list(range(len(ids)))
    lanes = [("Reference (= engine)", gold, -0.30, "o", BLUE_900, 18),
             ("Displayed grade", shown, -0.10, "^", AMBER, 24),
             ("Expert 1", e1, 0.11, "s", GREEN, 17),
             ("Expert 2", e2, 0.31, "D", BROWN, 14)]
    for name, vals, dx, marker, colour, size in lanes:
        bx.scatter([x + dx for x in xs], vals, s=size, marker=marker,
                   color=colour, edgecolors="white", linewidths=0.5,
                   zorder=5, label=name)

    for lvl in (1, 2, 3):
        bx.axhline(lvl, color=RULE, lw=0.6, zorder=1)

    bx.set_xticks(xs)
    bx.set_xticklabels(ids, rotation=90, fontsize=8)
    bx.set_yticks([1, 2, 3])
    bx.set_yticklabels(["Low", "Medium", "High"], fontsize=8)
    bx.set_ylim(0.55, 3.45)
    bx.set_xlim(-0.65, len(ids) - 0.35)
    bx.set_xlabel("Case", fontsize=8)
    bx.set_title("(b) Per-case grades", loc="left", pad=6)
    bx.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=2,
              handletextpad=0.35, columnspacing=1.2, fontsize=8.0)

    for ext, fmt, kw in [("png", "png", {"dpi": 400}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 600})]:
        fig.savefig(FIG / f"figure3_expert_agreement.{ext}", format=fmt,
                    bbox_inches=None, pad_inches=0, facecolor="white", **kw)
    plt.close(fig)

    # ── source data ─────────────────────────────────────────────────────
    sd = FIG / "source_data"
    sd.mkdir(parents=True, exist_ok=True)
    with (sd / "figure3_source.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["comparison", "agreement", "kappa_unweighted",
                    "kappa_weighted_quadratic"])
        for c, a, k, q in zip(keys, agree, kappa, wq):
            w.writerow([c, round(a, 4), round(k, 4), round(q, 4)])
    with (sd / "figure3_expert_agreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "gold_shown", "engine_grade", "system_shown",
                    "expert_1", "expert_2"])
        for p in per:
            engine = "low" if p["case_id"] in ("R10", "R11") else p["gold_shown"]
            w.writerow([p["case_id"], p["gold_shown"], engine,
                        p["system_shown"], p["expert_1"], p["expert_2"]])
    print("figure3_expert_agreement saved (+ source data)")


if __name__ == "__main__":
    main()
