#!/usr/bin/env python3
"""draw_figure1.py — 系统架构图（论文 Figure 1，示意图）。

简洁线框风格：输入 → 三层确定性级联 → 输出/可解释性 + 知识库接入。
出版尺寸排版（figsize 10×6.2 in，Arial）。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

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
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})


def main() -> None:
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def box(x, y, w, h, title, lines, fc, fs_title=10, fs_body=8.6):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           fc=fc, ec="#334155", lw=1.1)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h - 0.26, title, ha="center", va="top",
                fontsize=fs_title, fontweight="bold", color="#111827")
        ax.text(x + w / 2, y + h / 2 - 0.1, lines, ha="center", va="center",
                fontsize=fs_body, color="#374151")

    def arrow(x1, y1, x2, y2, label=""):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=13, lw=1.2, color="#6B7280")
        ax.add_patch(a)
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.18, label, ha="center",
                    fontsize=7.8, color="#6B7280")

    ax.text(5, 7.7, "Ophthalmic DDI Clinical Decision Support System",
            ha="center", fontsize=14, fontweight="bold", color="#111827")
    ax.text(5, 7.25, "Three-layer deterministic cascade  ·  zero LLM calls  ·  fully traceable",
            ha="center", fontsize=9, color="#6B7280")

    box(0.5, 5.8, 4.3, 1.15, "INPUT", "Ophthalmic topical drug A (113 agents, 6 absorption tiers)\nSystemic drug B (232 agents, mechanism flags & classes)", "#EFF6FF")
    box(5.6, 5.8, 3.9, 1.15, "KNOWLEDGE BASE", "1,307 curated evidence chunks (A 53 · B 191 · C 215 · D 584 · E 264)\nRule source records; class-matrix cells", "#F0FDF4")

    box(0.5, 3.15, 9.0, 1.95, "DETERMINISTIC CASCADE",
        "L1  Rule engine — 40 mechanism rules + 3 patient-factor policies (MAX-MATCH; not absorption-gated) — 12.0% of pairs\n"
        "L2  Class matrix — 21 × 40 classes (34 used); 104 cells (83 graded + 21 \"none\"); absorption scaling forces low/very-low to low — 68.7%\n"
        "L3  G19 hard constraint — low/very-low absorption, no other signal → low; unknown drug → explicit error — 12.2% (+7.1% default)\n"
        "Final grade = max(L1, L2)",
        "#FEF3C7", fs_body=8.2)
    arrow(2.6, 5.8, 2.6, 5.10)
    arrow(5.2, 5.8, 5.2, 5.10)
    arrow(7.5, 5.8, 7.5, 5.10, "provenance")

    box(0.5, 0.8, 4.3, 1.55, "DECISION OUTPUT", "high / medium / low\nmatched rule IDs + decision path\ndeposit-linked evidence chain", "#FEE2E2")
    box(5.6, 0.8, 3.9, 1.55, "EXPLAINABILITY", "Traceable decision path\nEvidence citations (PMID/DOI)\nAuditable in clinical review", "#F3E8FF")
    arrow(5.2, 3.15, 2.6, 2.35)
    arrow(5.2, 3.15, 7.5, 2.35)

    ax.text(5, 0.25, "full_system: deterministic cascade (0 LLM calls, about 2 ms per pair)  ·  zero variance across 5 temperature conditions  ·  path shares from 26,216 registry pairs (deposited audit)",
            ha="center", fontsize=8.0, color="#6B7280")

    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 300})]:
        fig.savefig(FIG / f"figure1_architecture.{ext}", format=fmt,
                    bbox_inches="tight", **kw)
    plt.close(fig)
    print("figure1_architecture saved")


if __name__ == "__main__":
    main()
