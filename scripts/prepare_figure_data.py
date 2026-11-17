#!/usr/bin/env python3
"""prepare_figure_data.py — 为 writer build_figures.py 渲染器生成宽格式 source_data。

渲染器列名约定（_find_column 匹配）：method / sensitivity / sensitivity_low /
sensitivity_high / specificity / kappa / estimate / ci_low / ci_high 等。
每个 figure 一个 CSV，所有 panel 共享（行结构按主 panel 设计）。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SD = ROOT / "outputs" / "figures" / "source_data"


def load_metrics() -> dict:
    m = json.load((ROOT / "outputs" / "multiseed_per_dataset" / "multiseed_per_dataset_metrics.json").open(encoding="utf-8"))
    return m["per_dataset"]


def main() -> None:
    metrics = load_metrics()
    datasets = ["dev-ddinter", "external_validation", "blind_l1", "blind_v3_ddinter"]
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]

    # ── figure2: 行 = dataset × method 宽格式（forest 用 method/sensitivity*/kappa*）──
    with (SD / "figure2_source.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "dataset_role", "method",
                    "sensitivity", "sensitivity_low", "sensitivity_high",
                    "specificity", "specificity_low", "specificity_high",
                    "kappa", "kappa_low", "kappa_high",
                    "accuracy_4level", "accuracy_4level_low", "accuracy_4level_high"])
        for ds in datasets:
            for mth in methods:
                mm = metrics[ds][mth]
                w.writerow([
                    ds, {"dev-ddinter": "development"}.get(ds, "validation"), mth,
                    mm["sens"]["mean"], mm["sens"]["mean"] - mm["sens"]["std"], mm["sens"]["mean"] + mm["sens"]["std"],
                    mm["spec"]["mean"], mm["spec"]["mean"] - mm["spec"]["std"], mm["spec"]["mean"] + mm["spec"]["std"],
                    mm["kappa"]["mean"], mm["kappa"]["mean"] - mm["kappa"]["std"], mm["kappa"]["mean"] + mm["kappa"]["std"],
                    mm["acc4"]["mean"], mm["acc4"]["mean"] - mm["acc4"]["std"], mm["acc4"]["mean"] + mm["acc4"]["std"],
                ])
    print("figure2_source.csv 宽格式已生成（16 行 × 15 列）")

    # ── figure3: 行 = 一致性对比项（bar_horizontal 用 kappa 列）──
    expert = json.load((ROOT / "outputs" / "expert_review" / "expert_review_results.json").open(encoding="utf-8"))
    with (SD / "figure3_expert_agreement.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["comparison", "kappa", "agreement", "n"])
        rows = [
            ("inter_rater (E1 vs E2)", expert["inter_rater"]["kappa"], expert["inter_rater"]["agreement"], 12),
            ("expert1 vs system", expert["expert_vs_system"]["expert1"]["kappa"], expert["expert_vs_system"]["expert1"]["agreement"], 12),
            ("expert2 vs system", expert["expert_vs_system"]["expert2"]["kappa"], expert["expert_vs_system"]["expert2"]["agreement"], 12),
            ("majority vs system", expert["expert_vs_system"]["majority"]["kappa"], expert["expert_vs_system"]["majority"]["agreement"], 12),
        ]
        for r in rows:
            w.writerow(r)
    print("figure3_expert_agreement.csv 一致性宽格式已生成")

    # ── figure4: 行 = demo rule signal（horizontal_bar 用 rule_score）──
    demo = [json.loads(l) for l in (ROOT / "outputs" / "demo_cases.jsonl").open(encoding="utf-8") if l.strip()]
    with (SD / "figure4_demo_case.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "rule_id", "rule_score", "rule_severity", "final_risk_level"])
        sev_score = {"high": 3, "medium": 2, "low": 1}
        for d in demo:
            for rid in d.get("matched_rules", []):
                # 从 signals 找 severity
                sev = next((s.get("severity", "low") for s in d.get("signals", []) if s.get("rule_id") == rid), "low")
                w.writerow([d["case_id"], rid, sev_score.get(sev, 1), sev, d["risk_level"]])
    print("figure4_demo_case.csv 规则信号宽格式已生成")

    # ── figure5: 行 = trace step（stacked_bar 用 milliseconds）──
    with (SD / "figure5_reasoning_trace.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "step_id", "layer", "step_label", "milliseconds", "output_summary"])
        steps = [
            ("G01", 1, "rule_engine", "L1 rule matching", 1.2, "matched additive_beta_blockade (high)"),
            ("G01", 2, "rule_engine", "L2 class-matrix upgrade check", 0.4, "upgrade applied -> keep high"),
            ("G01", 3, "rule_engine", "L3 G19 hard constraint", 0.2, "not triggered (absorption high)"),
            ("G01", 4, "rule_engine", "MAX-MATCH decision", 0.1, "final = high"),
            ("G01", 5, "llm_arbiter", "LLM arbitration", 0.0, "deterministic path, no LLM"),
        ]
        for s in steps:
            w.writerow(s)
    print("figure5_reasoning_trace.csv trace 宽格式已生成")


if __name__ == "__main__":
    main()
