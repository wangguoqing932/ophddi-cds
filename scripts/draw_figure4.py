#!/usr/bin/env python3
"""draw_figure4.py — 演示案例（论文 Figure 4）。

左：demo 案例命中规则及严重度权重（横向柱）
右：8 个演示案例最终风险分布（交通灯散点）
出版尺寸排版（figsize 9.5×3.6 in）。
"""
from __future__ import annotations

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
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 11,
    "axes.titlesize": 12.0,
    "axes.titleweight": "bold",
    "axes.labelsize": 11.0,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 9,
    "legend.frameon": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

GRAY = "#767676"
LIGHT = "#D9D9D9"
SEV_SCORE = {"high": 3, "medium": 2, "low": 1}
RISK_MAP = {"high": 3, "medium": 2, "low": 1}
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_palette import RISK as COLOR_MAP, BLUE_900, INK


def main() -> None:
    demo = [json.loads(l) for l in (ROOT / "outputs" / "data_outputs" / "demo_cases.jsonl").open(encoding="utf-8") if l.strip()]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.09, 2.69))
    d1 = demo[0]
    rules = [(s["rule_id"], SEV_SCORE.get(s.get("severity", "low"), 1))
             for s in d1.get("signals", [])]
    rules.sort(key=lambda x: -x[1])
    ax1.barh([r[0] for r in rules], [r[1] for r in rules], color=BLUE_900,
             height=0.45, zorder=3)
    ax1.set_xlabel("Severity weight", fontsize=11.0)
    ax1.set_title("(a) Rule signals: timolol x atenolol", fontsize=10.5)
    ax1.set_xlim(0, 3.3)
    ax1.set_xticks([1, 2, 3])
    ax1.set_ylim(-0.35, 1.35)
    for rect, v in zip(ax1.patches, [r[1] for r in rules]):
        ax1.text(v + 0.08, rect.get_y() + rect.get_height() / 2, f"{v}",
                 va="center", fontsize=10.0, color=INK)

    for i, d in enumerate(demo):
        rl = d.get("risk_level", d.get("risk", "low"))
        val = RISK_MAP[rl]
        ax2.barh(i, val, color=COLOR_MAP[rl], height=0.55, zorder=3)
        ax2.text(val + 0.08, i, rl, va="center", fontsize=8.5,
                 color=INK, zorder=4)
    ax2.set_yticks(range(len(demo)))
    ax2.set_yticklabels([d['ophthalmic'] + chr(10) + 'x ' + d['systemic'] for d in demo],
                        fontsize=8.0)
    ax2.set_xlim(0, 3.9)
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(["Low", "Medium", "High"], fontsize=8.6)
    ax2.invert_yaxis()
    ax2.set_title("(b) Final risk of the 6 demo cases", fontsize=10.5)

    fig.subplots_adjust(left=0.30, right=0.98, top=0.86, bottom=0.18, wspace=0.75)
    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 300})]:
        fig.savefig(FIG / f"figure4_demo_case.{ext}", format=fmt,
                    bbox_inches="tight", **kw)
    plt.close(fig)
    print("figure4_demo_case saved")


if __name__ == "__main__":
    main()
