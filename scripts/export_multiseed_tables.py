#!/usr/bin/env python3
"""export_multiseed_tables.py — v3.0-format tables from the real-LLM 5-seed run.

Writes:
  outputs/tables/performance_by_dataset.csv   (dataset_id x method, mean±std over 5 seeds)
  outputs/tables/dataset_summary.csv          (dataset_id, role, n, gold distribution)
  outputs/figures/source_data/figure2_performance.csv  (per-case rows, all seeds)
  outputs/figures/source_data/figure2_source.csv       (figure2 summary for plotting)
  outputs/multiseed_per_dataset/REPORT.md              (full narrative report)
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "outputs" / "multiseed_per_dataset"

ROLES = {
    "dev-ddinter": "development",
    "external_validation": "external_validation",
    "blind_l1": "external_validation",
    "blind_v3_ddinter": "external_validation",
}
METHODS = ["pure_llm", "naive_rag", "lightrag", "full_system"]


def main() -> None:
    metrics = json.load((RAW / "multiseed_per_dataset_metrics.json").open(encoding="utf-8"))
    all_rows = []
    with (RAW / "predictions_all.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_rows.append(json.loads(line))

    # ── performance_by_dataset.csv (v3.0) ──
    perf_path = ROOT / "outputs" / "tables" / "performance_by_dataset.csv"
    with perf_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "dataset_role", "method", "n",
                    "sensitivity_high_mean", "sensitivity_high_std",
                    "specificity_high_mean", "specificity_high_std",
                    "f1_high_mean", "f1_high_std",
                    "accuracy_4level_mean", "accuracy_4level_std",
                    "cohen_kappa_mean", "cohen_kappa_std"])
        for ds in ROLES:
            for method in METHODS:
                mm = metrics["per_dataset"][ds][method]
                w.writerow([ds, ROLES[ds], method, mm["n"],
                            mm["sens"]["mean"], mm["sens"]["std"],
                            mm["spec"]["mean"], mm["spec"]["std"],
                            mm["f1"]["mean"], mm["f1"]["std"],
                            mm["acc4"]["mean"], mm["acc4"]["std"],
                            mm["kappa"]["mean"], mm["kappa"]["std"]])
    print(f"wrote {perf_path}")

    # ── dataset_summary.csv ──
    sum_path = ROOT / "outputs" / "tables" / "dataset_summary.csv"
    with sum_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "dataset_role", "n_cases", "n_high", "n_medium", "n_low", "gold_source"])
        # gold sources (from the loader knowledge)
        gold_sources = {
            "dev-ddinter": "DDInter 2.0 original levels (not ophthalmic-adjusted)",
            "external_validation": "PubMed cases + guidelines (not ophthalmic-adjusted)",
            "blind_l1": "literature-consensus 20 (FDA/Stockley's/BNF) + blind-frozen 40 (proposed, SHA-locked) + guideline 58; NO human expert yet",
            "blind_v3_ddinter": "DDInter stratified sample, absorption-corrected",
        }
        for ds in ROLES:
            golds = Counter(r["gold_risk"] for r in all_rows if r["dataset_id"] == ds)
            # each case appears 4 methods x 5 seeds = 20 rows
            rows_per_case = len(METHODS) * 5
            w.writerow([ds, ROLES[ds], sum(golds.values()) // rows_per_case,
                        golds.get("high", 0) // rows_per_case,
                        golds.get("medium", 0) // rows_per_case,
                        golds.get("low", 0) // rows_per_case, gold_sources[ds]])
    print(f"wrote {sum_path}")

    # ── figure2_performance.csv (per-case rows, all seeds) ──
    fig2p = ROOT / "outputs" / "figures" / "source_data" / "figure2_performance.csv"
    with fig2p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "dataset_id", "dataset_role", "seed", "baseline", "risk_true", "risk_pred"])
        for r in sorted(all_rows, key=lambda x: (x["dataset_id"], x["seed"], x["case_id"])):
            w.writerow([r["case_id"], r["dataset_id"], ROLES[r["dataset_id"]], r["seed"],
                        r["method"], r["gold_risk"], r["predicted"]])
    print(f"wrote {fig2p} ({len(all_rows)} rows)")

    # ── figure2_source.csv (summary for plotting) ──
    fig2s = ROOT / "outputs" / "figures" / "source_data" / "figure2_source.csv"
    with fig2s.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["figure_id", "dataset_id", "dataset_role", "method", "metric", "value", "std"])
        for ds in ROLES:
            for method in METHODS:
                mm = metrics["per_dataset"][ds][method]
                for metric, key in [("accuracy_4level", "acc4"), ("sensitivity_high", "sens"),
                                    ("specificity_high", "spec"), ("cohen_kappa", "kappa")]:
                    w.writerow(["figure2", ds, ROLES[ds], method, metric,
                                mm[key]["mean"], mm[key]["std"]])
    print(f"wrote {fig2s}")

    # ── REPORT.md ──
    lines = []
    lines.append("# Multiseed Per-Dataset Evaluation (v4-flash era → deepseek-chat final)\n")
    lines.append(f"- Run: 4 datasets x 4 methods x 5 seeds = **{metrics['n_predictions']} predictions**")
    lines.append(f"- LLM: `deepseek-chat` (OpenAI-compatible, temperature schedule {metrics['temperature_schedule']})")
    lines.append(f"- API failures: **{metrics['n_api_failures']}** (0)")
    lines.append(f"- Engine: deterministic v2 cascade (L1 rules → L2 class matrix → L3 G19 → default low), 0 LLM calls")
    lines.append(f"- Generated: {metrics['generated_at']}\n")
    lines.append("## Per-dataset 4-method results (5-seed mean ± std)\n")
    lines.append("| dataset | role | method | Acc4 | Sens | Spec | κ |")
    lines.append("|---|---|---|---|---|---|---|")
    for ds in ROLES:
        for method in METHODS:
            mm = metrics["per_dataset"][ds][method]
            lines.append(f"| {ds} | {ROLES[ds]} | {method} | "
                         f"{mm['acc4']['mean']:.3f}±{mm['acc4']['std']:.3f} | "
                         f"{mm['sens']['mean']:.3f}±{mm['sens']['std']:.3f} | "
                         f"{mm['spec']['mean']:.3f}±{mm['spec']['std']:.3f} | "
                         f"{mm['kappa']['mean']:.3f}±{mm['kappa']['std']:.3f} |")
    lines.append("")
    lines.append("## L1 per-subset (blind_l1) full_system\n")
    lines.append("| subset | n | Acc4 |")
    lines.append("|---|---|---|")
    for sub, methods in metrics["per_subset_l1"].items():
        fs = methods["full_system"]
        lines.append(f"| {sub} | {fs['n']} | {fs['acc4']['mean']:.3f}±{fs['acc4']['std']:.3f} |")
    lines.append("")
    lines.append("## Reading notes (honest caveats)\n")
    lines.append("- **blind_l1** = primary table (gold independent; 66% of cases overlap development-phase internal_validation; blind-frozen 40 = strictest, 1.000)")
    lines.append("- **blind_v3_ddinter** = external audit (DDInter levels independent; absorption correction shares the absorption table with the system — semi-independent)")
    lines.append("- **external_validation** = gold NOT ophthalmic-adjusted (PubMed case levels); LLM high scores there reflect coincidence with unadjusted gold, not true superiority (see report)")
    lines.append("- **dev-ddinter** = protocol reference only (DDInter original levels, not adjusted)")
    lines.append("- consensus_validation excluded: rule-derived gold (tautology), see validation audit")
    report_path = RAW / "REPORT.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
