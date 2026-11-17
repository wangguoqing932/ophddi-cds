#!/usr/bin/env python3
"""draw_figure2.py — 参考图风格分组柱状图（论文主图，Figure 2）。

4 指标（Sensitivity/Specificity/F1/Cohen's kappa）× 4 方法分组柱状图，
柱顶数值标注，y 轴 0.0-1.0 刻度，浅灰水平网格，左上图例，Arial。
字号按出版尺寸设计：figsize 8.2×4.2 in（出版约 180mm 宽），
正文 11pt、数值 10pt、标题 12pt —— 出版后 ≥ 7-8pt。

运行: 系统 python（有 matplotlib）: python scripts/draw_figure2.py
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
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "legend.fontsize": 9.5,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_palette import METHOD as METHOD_COLOUR, INK, RULE

COLORS = [METHOD_COLOUR[m] for m in ["pure_llm", "naive_rag", "lightrag", "full_system"]]
METHOD_LABELS = {
    "pure_llm": "Pure LLM",
    "naive_rag": "Naive RAG",
    "lightrag": "Rule-context",
    "full_system": "Full system",
}
METHODS = ["pure_llm", "naive_rag", "lightrag", "full_system"]
METRICS = [("Sensitivity (HIGH)", "sens"), ("Specificity (HIGH)", "spec"),
           ("F1 (HIGH)", "f1"), ("Cohen's kappa", "kappa")]


def frozen_l1_metrics() -> dict:
    """Mean over the five temperature conditions under the frozen (pre-errata) labels."""
    import csv
    import statistics as st
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    per = {m: [] for m in METHODS}
    for seed in range(5):
        rows = {}
        for line in (ROOT / f"outputs/multiseed_per_dataset/blind_l1__seed{seed}.jsonl").open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            rows.setdefault(r["method"], []).append(r)
        for m in METHODS:
            y, p = [], []
            for r in rows[m]:
                cid = r["case_id"]
                y.append(prov[cid]["gold_pre_errata"] or prov[cid]["gold_current"])
                p.append(r["predicted"])
            n = len(y)
            acc = sum(a == b for a, b in zip(y, p)) / n
            hi = [i for i, g in enumerate(y) if g == "high"]
            tp = sum(p[i] == "high" for i in hi)
            non = [i for i, g in enumerate(y) if g != "high"]
            tn = sum(p[i] != "high" for i in non)
            prec = tp / (tp + sum(1 for i, g in enumerate(y) if g != "high" and p[i] == "high")) if tp else 0.0
            sens = tp / len(hi) if hi else 0.0
            f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0.0
            pe = sum((y.count(lv) / n) * (p.count(lv) / n) for lv in ("low", "medium", "high"))
            kap = (acc - pe) / (1 - pe) if pe != 1 else 0.0
            per[m].append({"sens": sens, "spec": tn / len(non) if non else 0.0, "f1": f1, "kappa": kap})
    return {m: {k: {"mean": st.mean(x[k] for x in per[m]),
                    "sd": st.pstdev(x[k] for x in per[m])}
                for k in ("sens", "spec", "f1", "kappa")} for m in METHODS}


def main() -> None:
    """两面板：左=原设置（10-token），右=充分预算（推理模型 + 3000 token + 5 次多数票）。

    右面板的敏感性暴跌是本图要传达的关键信息：放开预算后基线退化为"极少报警"的
    保守策略，Acc3 上升但敏感性崩塌。
    """
    old_m = json.load((ROOT / "outputs" / "multiseed_per_dataset" /
                       "multiseed_per_dataset_metrics.json").open(encoding="utf-8"))
    new_m = json.load((ROOT / "outputs" / "glm53_baselines" /
                       "metrics_majority.json").open(encoding="utf-8"))
    ds = "blind_l1"
    frozen = frozen_l1_metrics()

    fig, axes = plt.subplots(1, 2, figsize=(7.09, 2.84))
    x = range(len(METRICS))
    w = 0.19
    metric_name = {"sens": "sensitivity_high", "spec": "specificity_high",
                   "f1": "f1_high", "kappa": "cohen_kappa"}
    source_rows = []

    for panel, (ax, title) in enumerate(zip(axes, [
            "(a) Primary: frozen labels, 10-token",
            "(b) Second configuration: corrected labels"])):
        for i, (mth, color) in enumerate(zip(METHODS, COLORS)):
            if panel == 0:
                mm = frozen[mth]
                vals = [mm[METRICS[j][1]]["mean"] for j in range(len(METRICS))]
                sds = [mm[METRICS[j][1]]["sd"] for j in range(len(METRICS))]
            else:
                if mth == "full_system":
                    mm = old_m["per_dataset"][ds][mth]     # 确定性，两设置相同
                    vals = [mm[METRICS[j][1]]["mean"] for j in range(len(METRICS))]
                    sds = [mm[METRICS[j][1]]["std"] for j in range(len(METRICS))]
                else:
                    nm = new_m[ds][mth]
                    vals = [nm[METRICS[j][1]] for j in range(len(METRICS))]
                    sds = [0.0 for _ in METRICS]
            label = "L1_frozen" if panel == 0 else "L1_config2"
            for j, v in enumerate(vals):
                source_rows.append([label, ds, mth, metric_name[METRICS[j][1]], v, sds[j]])
            bars = ax.bar([xi + (i - 1.5) * w for xi in x], vals, w, color=color,
                          label=METHOD_LABELS[mth] if panel == 0 else None, zorder=3)
            for rect, v in zip(bars, vals):
                ax.text(rect.get_x() + rect.get_width() / 2, v + 0.02, f"{v:.2f}",
                        ha="center", va="bottom", fontsize=8.0, color=INK,
                        rotation=90)

        ax.set_xticks(list(x))
        ax.set_xticklabels([mt[0].replace(" (HIGH)", "").replace("Cohen's ", "") for mt in METRICS],
                           fontsize=9.5)
        ax.set_ylim(0, 1.20)
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_title(title, fontsize=11.0, pad=10)
        ax.axhline(1.0, color=RULE, lw=0.6, zorder=1)
    axes[0].set_ylabel("Metric value", fontsize=11.0)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False,
               fontsize=8.6, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("L1 author-derived reference set (118 cases): two configurations",
                 fontsize=10.0, y=1.02)

    fig.tight_layout(rect=(0, 0.10, 1, 0.97))
    for ext, fmt, kw in [("png", "png", {"dpi": 300}), ("pdf", "pdf", {}),
                         ("svg", "svg", {}),
                         ("tiff", "tiff", {"dpi": 300, "pil_kwargs": {"compression": "tiff_lzw"}})]:
        fig.savefig(FIG / f"figure2_performance.{ext}", format=fmt,
                    bbox_inches="tight", **kw)
    plt.close(fig)
    import csv
    src = FIG / "source_data" / "figure2_source.csv"
    src.parent.mkdir(parents=True, exist_ok=True)
    with src.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["labels", "dataset_id", "method", "metric", "value", "std"])
        writer.writerows(source_rows)
    print("figure2_performance saved (two-panel grouped bar: 10-token vs adequate budget)")
    print(f"source data written: {src} ({len(source_rows)} rows)")


if __name__ == "__main__":
    main()
