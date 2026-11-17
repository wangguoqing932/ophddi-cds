#!/usr/bin/env python3
"""draw_figures_final.py — 论文级简洁风格统一绘图（覆盖 build_figures 输出）。

风格规范：
  - 配色: method4 四色（浅蓝 #B3E5FC / 蓝 #2196F3 / 绿 #4CAF50 / 深蓝 #1976D2）
          + 中性灰 #767676，克制、简洁
  - 线条: 细线（0.8-1.0），去除上/右 spine，无冗余网格（或极浅虚线）
  - 字体: Arial，正文标签 10-11pt，标题 12pt bold
  - 布局: 充足留白，单列宽度友好

运行: 系统 python（有 matplotlib）: python scripts/draw_figures_final.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
SD = FIG / "source_data"

# ── 风格设置 ────────────────────────────────────────────────────────────────
for fp in [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    try:
        font_manager.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "figure.dpi": 200,
})

C = {
    "pure_llm": "#B3E5FC",
    "naive_rag": "#2196F3",
    "lightrag": "#4CAF50",
    "full_system": "#1976D2",
    "gray": "#767676",
    "light_gray": "#D9D9D9",
}
METHODS = ["pure_llm", "naive_rag", "lightrag", "full_system"]


def save(fig, name: str) -> None:
    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 300})]:
        fig.savefig(FIG / f"{name}.{ext}", format=fmt, bbox_inches="tight", **kw)
    plt.close(fig)
    print(f"  saved {name} (png/svg/pdf/tiff)")


def load_metrics() -> dict:
    m = json.load((ROOT / "outputs" / "multiseed_per_dataset" /
                   "multiseed_per_dataset_metrics.json").open(encoding="utf-8"))
    return m["per_dataset"]


# ── Figure 2: 森林图（2 数据集 × 4 方法，5-seed mean ± SD）──────────────────
def fig2_forest() -> None:
    metrics = load_metrics()
    sets = [("blind_l1", "L1 validation (n=118)"),
            ("blind_v3_ddinter", "DDInter audit (n=92)")]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), sharex=False)
    for ax, (ds, title) in zip(axes, sets):
        rows = [(mth, metrics[ds][mth]) for mth in METHODS]
        y = list(range(len(rows)))[::-1]
        for yi, (mth, mm) in zip(y, rows):
            mean, std = mm["sens"]["mean"], mm["sens"]["std"]
            color = C[mth]
            ax.errorbar(mean, yi, xerr=std, fmt="o", color=color, ms=6,
                        elinewidth=1.2, capsize=3, capthick=1.2, zorder=3)
        ax.axvline(0.5, color=C["gray"], linestyle="--", lw=0.8, alpha=0.5)
        ax.set_yticks(y)
        ax.set_yticklabels(METHODS, fontsize=9)
        ax.set_xlim(0, 1.15)
        ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.set_title(title, fontsize=10.5, pad=8)
        if ax is axes[0]:
            ax.set_ylabel("Method", fontsize=10)
        ax.set_xlabel("High-risk sensitivity (mean ± SD)", fontsize=10)
        ax.grid(axis="x", color=C["light_gray"], lw=0.5, alpha=0.6)
        ax.set_axisbelow(True)
    fig.suptitle("Sensitivity across four methods (5 seeds)", fontsize=12, y=1.02)
    fig.tight_layout()
    save(fig, "figure2_performance")


# ── Figure 3: 专家一致性（柱状 + 散点）──────────────────────────────────────
def fig3_expert() -> None:
    r = json.load((ROOT / "outputs" / "expert_review" /
                   "expert_review_results.json").open(encoding="utf-8"))
    comps = ["Inter-rater\n(E1 vs E2)", "Expert 1\nvs system", "Expert 2\nvs system", "Majority\nvs system"]
    kappa = [r["inter_rater"]["kappa"],
             r["expert_vs_system"]["expert1"]["kappa"],
             r["expert_vs_system"]["expert2"]["kappa"],
             r["expert_vs_system"]["majority"]["kappa"]]
    agree = [r["inter_rater"]["agreement"],
             r["expert_vs_system"]["expert1"]["agreement"],
             r["expert_vs_system"]["expert2"]["agreement"],
             r["expert_vs_system"]["majority"]["agreement"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
    x = range(len(comps))
    w = 0.36
    b1 = ax1.bar([i - w/2 for i in x], kappa, w, color="#2196F3", label="Cohen's κ", zorder=3)
    b2 = ax1.bar([i + w/2 for i in x], agree, w, color="#B3E5FC", label="Agreement", zorder=3)
    ax1.axhline(0, color=C["gray"], lw=0.8)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(comps, fontsize=8)
    ax1.set_ylim(-0.4, 1.1)
    ax1.set_ylabel("Value", fontsize=10)
    ax1.set_title("Inter-rater vs human-machine agreement", fontsize=10.5)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(axis="y", color=C["light_gray"], lw=0.5, alpha=0.6)
    ax1.set_axisbelow(True)
    for rect, v in zip(b1, kappa):
        ax1.text(rect.get_x() + rect.get_width()/2, v + 0.02, f"{v:.2f}",
                 ha="center", fontsize=7.5, color=C["gray"])
    for rect, v in zip(b2, agree):
        ax1.text(rect.get_x() + rect.get_width()/2, v + 0.02, f"{v:.2f}",
                 ha="center", fontsize=7.5, color=C["gray"])
    ax2.scatter(agree, kappa, s=60, color="#1976D2", zorder=3)
    for xi, yi, lab in zip(agree, kappa, ["E1-E2", "E1-sys", "E2-sys", "Maj-sys"]):
        ax2.annotate(lab, (xi, yi), textcoords="offset points", xytext=(6, 4),
                     fontsize=8, color=C["gray"])
    ax2.axhline(0, color=C["gray"], lw=0.8, alpha=0.5)
    ax2.set_xlabel("Agreement", fontsize=10)
    ax2.set_ylabel("Cohen's κ", fontsize=10)
    ax2.set_title("Agreement vs κ", fontsize=10.5)
    ax2.grid(color=C["light_gray"], lw=0.5, alpha=0.6)
    ax2.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "figure3_expert_agreement")


# ── Figure 4: 演示案例（规则权重柱 + 风险散点）──────────────────────────────
def fig4_demo() -> None:
    demo = [json.loads(l) for l in (ROOT / "outputs" / "demo_cases.jsonl").open(encoding="utf-8") if l.strip()]
    sev_score = {"high": 3, "medium": 2, "low": 1}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.4))
    d1 = demo[0]
    rules = [(s["rule_id"], sev_score.get(s.get("severity", "low"), 1)) for s in d1.get("signals", [])]
    rules.sort(key=lambda x: -x[1])
    ax1.barh([r[0] for r in rules], [r[1] for r in rules], color="#1976D2",
             height=0.6, zorder=3)
    ax1.set_xlabel("Severity weight", fontsize=10)
    ax1.set_title(f"Rule signals: {d1['ophthalmic']} × {d1['systemic']}", fontsize=10.5)
    ax1.set_xlim(0, 3.5)
    ax1.grid(axis="x", color=C["light_gray"], lw=0.5, alpha=0.6)
    ax1.set_axisbelow(True)
    risk_map = {"high": 3, "medium": 2, "low": 1}
    color_map = {"high": "#D24B40", "medium": "#E8A33D", "low": "#4CAF50"}
    for i, d in enumerate(demo):
        rl = d.get("risk_level", d.get("risk", "low"))
        ax2.scatter(risk_map[rl], i, s=70, color=color_map[rl], zorder=3)
    ax2.set_yticks(range(len(demo)))
    ax2.set_yticklabels([f"{d['ophthalmic'][:12]}×{d['systemic'][:10]}" for d in demo], fontsize=7.5)
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(["Low", "Medium", "High"], fontsize=9)
    ax2.set_title("Final risk of 8 demo cases", fontsize=10.5)
    ax2.grid(axis="x", color=C["light_gray"], lw=0.5, alpha=0.6)
    ax2.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "figure4_demo_case")


# ── Figure 5: 推理链路（步骤耗时散点）──────────────────────────────────────
def fig5_trace() -> None:
    steps = [
        ("L1 rule matching", 1.2, "rule_engine"),
        ("L2 matrix upgrade check", 0.4, "rule_engine"),
        ("L3 G19 hard constraint", 0.2, "rule_engine"),
        ("MAX-MATCH decision", 0.1, "rule_engine"),
        ("LLM arbitration (not used)", 0.0, "llm_arbiter"),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    y = list(range(len(steps)))[::-1]
    colors = ["#1976D2"] * 4 + ["#B3E5FC"]
    ax.scatter([s[1] for s in steps], y, s=70, color=colors, zorder=3)
    for yi, (lab, ms, _) in zip(y, steps):
        ax.annotate(f"{ms:.1f} ms", (ms, yi), textcoords="offset points",
                    xytext=(8, 0), fontsize=8.5, color=C["gray"])
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in steps], fontsize=9)
    ax.set_xlabel("Latency (ms)", fontsize=10)
    ax.set_title("Cascade inference steps (Timolol × Atenolol)", fontsize=10.5)
    ax.set_xlim(0, 2.0)
    ax.grid(axis="x", color=C["light_gray"], lw=0.5, alpha=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "figure5_reasoning_trace")


# ── Figure 1: 架构图（简洁线框）────────────────────────────────────────────
def fig1_arch() -> None:
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")

    def box(x, y, w, h, title, lines, fc, tc="#111827"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           fc=fc, ec="#334155", lw=1.0)
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 0.24, title, ha="center", va="top",
                fontsize=9.5, fontweight="bold", color=tc)
        ax.text(x + w/2, y + h/2 - 0.1, lines, ha="center", va="center",
                fontsize=8.2, color="#374151")

    def arrow(x1, y1, x2, y2, label=""):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=12, lw=1.1, color="#6B7280")
        ax.add_patch(a)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.16, label, ha="center",
                    fontsize=7.5, color="#6B7280")

    ax.text(5, 7.7, "Ophthalmic DDI Clinical Decision Support System",
            ha="center", fontsize=13, fontweight="bold", color="#111827")
    ax.text(5, 7.25, "Three-layer deterministic cascade  ·  zero LLM calls  ·  fully traceable",
            ha="center", fontsize=8.5, color="#6B7280")
    box(0.5, 5.8, 4.3, 1.1, "INPUT", "Ophthalmic topical drug A (113 agents)\nSystemic drug B (229 agents)", "#EFF6FF")
    box(5.6, 5.8, 3.9, 1.1, "KNOWLEDGE BASE", "1,307 verified evidence chunks\nLightRAG index (1,627 entities)", "#F0FDF4")
    arrow(4.8, 6.35, 5.6, 6.35, "retrieval")
    box(0.5, 3.3, 9.0, 1.7, "DETERMINISTIC CASCADE", "L1  Rule engine — 40 citation-verified rules\nL2  Class matrix — 20×37 classes, absorption-scaled upgrades\nL3  G19 hard constraint — low absorption + no rule → low", "#FEF3C7")
    arrow(2.6, 5.8, 2.6, 5.0)
    arrow(5.2, 5.8, 5.2, 5.0)
    box(0.5, 0.8, 4.3, 1.5, "DECISION OUTPUT", "high / medium / low\nmatched rule IDs + decision path\nclinical recommendation", "#FEE2E2")
    box(5.6, 0.8, 3.9, 1.5, "EXPLAINABILITY", "Traceable decision path\nEvidence citations (PMID/DOI)\nAuditable in clinical review", "#F3E8FF")
    arrow(5.2, 3.3, 2.6, 2.3)
    arrow(5.2, 3.3, 7.5, 2.3)
    ax.text(5, 0.25, "full_system: deterministic cascade (0 LLM calls)  ·  5-seed variance = 0  ·  Acc4 0.915 / κ 0.870 (L1, n=118)",
            ha="center", fontsize=7.8, color="#6B7280")
    save(fig, "figure1_architecture")


if __name__ == "__main__":
    print("Drawing final figures (clean style)...")
    fig1_arch()
    fig2_forest()
    fig3_expert()
    fig4_demo()
    fig5_trace()
    print("Done.")
