# -*- coding: utf-8 -*-
"""draw_figure3.py — 专家一致性（论文 Figure 3），从重算结果生成。

数据来源：outputs/recomputed/expert_review_recomputed.json
（由 scripts/expert_review_analysis.py 生成；二次加权 kappa 用修正后的序数实现）。

左：五组对比的 Cohen kappa（未加权）、二次加权 kappa 与一致率。
右：逐例评级 — gold（与引擎判定完全一致）、问卷展示值（R10/R11 为类级提示）、两位专家。
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
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

LV = {"low": 1, "medium": 2, "high": 3}
NL = chr(10)


def main() -> None:
    r = json.load((ROOT / "outputs" / "recomputed" /
                   "expert_review_recomputed.json").open(encoding="utf-8"))

    comps = ["Inter-rater" + NL + "(E1 vs E2)", "E1 vs" + NL + "shown",
             "E2 vs" + NL + "shown", "E1 vs" + NL + "gold", "E2 vs" + NL + "gold"]
    keys = ["inter_rater", "e1_vs_system_shown", "e2_vs_system_shown",
            "e1_vs_gold_shown", "e2_vs_gold_shown"]
    kappa = [r[k]["kappa"] for k in keys]
    agree = [r[k]["agreement"] for k in keys]
    wq = [r[k]["kappa_weighted_quadratic"] for k in keys]

    per = r["per_case"]
    ids = [p["case_id"] for p in per]
    gold_n = [LV[p["gold_shown"]] for p in per]
    shown_n = [LV[p["system_shown"]] for p in per]
    e1_n = [LV[p["expert_1"]] for p in per]
    e2_n = [LV[p["expert_2"]] for p in per]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    x = range(len(comps))
    w = 0.27
    b1 = ax1.bar([i - w / 2 for i in x], kappa, w, color="#2196F3",
                 label="Cohen kappa (unweighted)", zorder=3)
    b3 = ax1.bar(list(x), wq, w, color="#7E57C2",
                 label="kappa quadratic-weighted (ordinal)", zorder=3)
    b2 = ax1.bar([i + w / 2 for i in x], agree, w, color="#B3E5FC",
                 label="Agreement", zorder=3)
    ax1.axhline(0, color="#333333", lw=1.2)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(comps, fontsize=8.2)
    ax1.set_ylim(-0.45, 1.2)
    ax1.set_ylabel("Value", fontsize=11)
    ax1.set_title("Expert agreement: inter-rater, vs displayed grade, vs gold", fontsize=10.5)
    ax1.legend(loc="upper right", fontsize=7.8)
    for rect, v in zip(list(b1) + list(b3), kappa + wq):
        off = -0.05 if v < 0 else 0.02
        ax1.text(rect.get_x() + rect.get_width() / 2, v + off, f"{v:.2f}",
                 ha="center", fontsize=7.2, color="#333333",
                 va="top" if v < 0 else "bottom")
    for rect, v in zip(list(b2), agree):
        ax1.text(rect.get_x() + rect.get_width() / 2, v + 0.02, f"{v:.2f}",
                 ha="center", fontsize=7.2, color="#333333")

    xs = list(range(1, 13))
    ax2.plot(xs, shown_n, "^-", color="#E8A33D", ms=6, lw=1.4,
             label="Grade shown on form (R10/R11: class-level hint)", zorder=3)
    ax2.plot(xs, gold_n, "o--", color="#1976D2", ms=7, lw=1.6,
             label="Gold (= engine grade, all 12)", zorder=4)
    ax2.plot(xs, e1_n, "s", color="#43A047", ms=5.5, label="Expert 1", zorder=5)
    ax2.plot(xs, e2_n, "D", color="#8D6E63", ms=4.5, label="Expert 2", zorder=5)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(ids, fontsize=7.5, rotation=45)
    ax2.set_yticks([1, 2, 3])
    ax2.set_yticklabels(["Low", "Medium", "High"], fontsize=9)
    ax2.set_ylim(0.5, 3.9)
    ax2.set_xlabel("Case", fontsize=11)
    ax2.set_title("Per-case judgment: gold vs displayed vs experts", fontsize=10.5)
    ax2.legend(loc="upper right", fontsize=7.2, ncol=1)

    fig.tight_layout()
    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("svg", "svg", {}),
                         ("pdf", "pdf", {}), ("tiff", "tiff", {"dpi": 300})]:
        fig.savefig(FIG / f"figure3_expert_agreement.{ext}", format=fmt,
                    bbox_inches="tight", **kw)
    plt.close(fig)

    # 真实源数据
    sd = FIG / "source_data"
    sd.mkdir(parents=True, exist_ok=True)
    with (sd / "figure3_source.csv").open("w", newline="", encoding="utf-8") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["comparison", "agreement", "kappa_unweighted",
                       "kappa_weighted_quadratic"])
        for c, a, k, q in zip(
                ["inter_rater", "e1_vs_shown", "e2_vs_shown", "e1_vs_gold", "e2_vs_gold"],
                agree, kappa, wq):
            wcsv.writerow([c, round(a, 4), round(k, 4), round(q, 4)])
    with (sd / "figure3_expert_agreement.csv").open("w", newline="", encoding="utf-8") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["case", "gold_shown", "engine_grade", "system_shown",
                       "expert_1", "expert_2"])
        for p in per:
            engine = "low" if p["case_id"] in ("R10", "R11") else p["gold_shown"]
            wcsv.writerow([p["case_id"], p["gold_shown"], engine,
                           p["system_shown"], p["expert_1"], p["expert_2"]])
    print("figure3_expert_agreement saved (+ source data)")


if __name__ == "__main__":
    main()
