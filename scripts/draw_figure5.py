#!/usr/bin/env python3
"""draw_figure5.py — 推理链路（论文 Figure 5）。

级联各步骤耗时散点（L1 规则 → L2 矩阵 → L3 G19 → 决策 → LLM 仲裁未用），
每步毫秒标注。出版尺寸排版（figsize 6.6×3.4 in）。
"""
from __future__ import annotations

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
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent))
from figure_palette import BLUE_900, BLUE_400, GREY, RULE

GRAY = GREY
LIGHT = RULE


def main() -> None:
    steps = [
        ("L1 rule matching", 1.2, BLUE_900),
        ("L2 matrix upgrade check", 0.4, BLUE_900),
        ("L3 G19 hard constraint", 0.2, BLUE_900),
        ("MAX-MATCH decision", 0.1, BLUE_900),
        ("LLM arbitration (not used)", 0.0, BLUE_400),
    ]
    fig, ax = plt.subplots(figsize=(7.09, 3.0))
    y = list(range(len(steps)))[::-1]
    ax.scatter([s[1] for s in steps], y, s=80, color=[s[2] for s in steps], zorder=3)
    for yi, (lab, ms, _) in zip(y, steps):
        ax.annotate(f"{ms:.1f} ms", (ms, yi), textcoords="offset points",
                    xytext=(9, 0), fontsize=9.5, color=GRAY)
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in steps], fontsize=10)
    ax.set_xlabel("Latency (ms)", fontsize=11)
    ax.set_title("Cascade inference steps: timolol x atenolol", fontsize=12)
    ax.set_xlim(0, 2.1)

    fig.tight_layout()
    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 300})]:
        fig.savefig(FIG / f"figure5_reasoning_trace.{ext}", format=fmt,
                    bbox_inches="tight", **kw)
    plt.close(fig)
    print("figure5_reasoning_trace saved")


if __name__ == "__main__":
    main()
