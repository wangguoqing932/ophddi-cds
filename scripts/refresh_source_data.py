# -*- coding: utf-8 -*-
"""refresh_source_data.py — regenerate figure source CSVs from the current engine state."""
from __future__ import annotations

import csv
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SD = ROOT / "outputs/figures/source_data"
sys.path.insert(0, str(ROOT / "src"))

T = ["systemic_absorption_high", "systemic_absorption_medium", "systemic_absorption_low",
     "systemic_absorption_very_low", "minimal_systemic_absorption", "systemic_absorption_none"]


def tier_counts():
    rows = list(csv.DictReader((ROOT / "data/seed/entities_a.csv").open(encoding="utf-8-sig")))
    counts = {t: 0 for t in T}
    for r in rows:
        flags = set(r["flags"].split("|"))
        for t in T:
            if t in flags:
                counts[t] += 1
                break
    with (SD / "figure1_absorption_tiers.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tier", "n_agents", "source"])
        for t in T:
            w.writerow([t, counts[t], "data/seed/entities_a.csv"])
    print("tiers", counts)


def path_components():
    p = json.load((ROOT / "outputs/audits/path_attribution.json").open(encoding="utf-8"))["paths"]
    with (SD / "figure1_source.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["component", "share_pct", "n_pairs", "source"])
        for key, name in [("rule", "rule_engine"), ("matrix", "class_matrix"),
                          ("g19", "g19_hard_constraint"), ("default_low", "default_low_path")]:
            e = p[key]
            w.writerow([name, e["pct"], e["n"], "outputs/audits/path_attribution.json"])
    print("path components written")


def l1_frozen_metrics():
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    out = {}
    for m in methods:
        per = []
        for seed in range(5):
            y, p = [], []
            for line in (ROOT / f"outputs/multiseed_per_dataset/blind_l1__seed{seed}.jsonl").open(encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                if r["method"] != m:
                    continue
                y.append(prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"])
                p.append(r["predicted"])
            n = len(y)
            acc = sum(a == b for a, b in zip(y, p)) / n
            hi = [i for i, g in enumerate(y) if g == "high"]
            tp = sum(p[i] == "high" for i in hi)
            non = [i for i, g in enumerate(y) if g != "high"]
            tn = sum(p[i] != "high" for i in non)
            per.append({"acc": acc, "sens": tp / len(hi), "spec": tn / len(non)})
        out[m] = {k: st.mean(x[k] for x in per) for k in ("acc", "sens", "spec")}
    return out


def figure2():
    # per-case rows with frozen gold
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    rows = [json.loads(l) for l in (ROOT / "outputs/baseline_predictions.jsonl").open(encoding="utf-8") if l.strip()]
    with (SD / "figure2_performance.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "dataset_id", "dataset_role", "seed", "baseline",
                    "risk_true", "risk_true_frozen", "risk_pred"])
        for r in sorted(rows, key=lambda x: (x["dataset_id"], x["seed"], x["case_id"])):
            frozen = (prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"]) if r["dataset_id"] == "blind_l1" else r["gold_risk"]
            w.writerow([r["case_id"], r["dataset_id"], r["dataset_role"], r["seed"],
                        r["method"], r["gold_risk"], frozen, r["predicted"]])
    print("figure2_performance rows", len(rows))

    # summary rows: L1 frozen + corrected, audit applied/rederived
    metrics = json.load((ROOT / "outputs/multiseed_per_dataset/multiseed_per_dataset_metrics.json").open(encoding="utf-8"))["per_dataset"]
    frozen = l1_frozen_metrics()
    with (SD / "figure2_source.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["labels", "dataset_id", "method", "metric", "value", "std"])
        for m in ["pure_llm", "naive_rag", "lightrag", "full_system"]:
            for metric, key in [("accuracy", "acc"), ("sensitivity_high", "sens"), ("specificity_high", "spec")]:
                w.writerow(["L1_frozen", "blind_l1", m, metric, frozen[m][key], 0.0])
        for m in ["pure_llm", "naive_rag", "lightrag", "full_system"]:
            for metric, key in [("accuracy", "acc4"), ("sensitivity_high", "sens"), ("specificity_high", "spec"), ("cohen_kappa", "kappa")]:
                w.writerow(["L1_corrected", "blind_l1", m, metric,
                            metrics["blind_l1"][m][key]["mean"], metrics["blind_l1"][m][key]["std"]])
    print("figure2_source written")


if __name__ == "__main__":
    tier_counts()
    path_components()
    figure2()
