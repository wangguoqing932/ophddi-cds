#!/usr/bin/env python3
"""export_final_tables.py — Regenerate outputs/tables/* from the final ablation run.

Fully reproducible: reads ablation_classify.jsonl + consensus_validation/cases.jsonl
+ rules.yaml and writes the final validation tables used in the paper.
"""

import csv, json
from pathlib import Path
from collections import Counter

import yaml

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

# ── Load ──
recs = [json.loads(l) for l in (ROOT / "output" / "ablation_classify.jsonl").open(encoding="utf-8")]
golds = [json.loads(l) for l in
         (ROOT / "data" / "datasets" / "consensus_validation" / "cases.jsonl").open(encoding="utf-8")]
rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").open(encoding="utf-8"))["rules"]
methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]

gmap = {g["case_id"]: g for g in golds}
tier_of = lambda cid: {"expert": "T1", "fda_label": "T2"}.get(
    gmap[cid]["gold_source"], "T3" if "DDInter" in gmap[cid]["gold_source"] else "T4")

# ── Metrics (same code as ablation_classify.py) ──
def metrics(pairs):
    lm = {"low": 1, "medium": 2, "high": 3}
    valid = [(lm[p["gold"]], lm[p["pred"]]) for p in pairs if p["pred"] != "unparseable"]
    tp = sum(1 for p in pairs if p["gold"] == "high" and p["pred"] == "high")
    fp = sum(1 for p in pairs if p["gold"] != "high" and p["pred"] == "high")
    fn = sum(1 for p in pairs if p["gold"] == "high" and p["pred"] != "high")
    tn = sum(1 for p in pairs if p["gold"] != "high" and p["pred"] != "high")
    sens = tp / (tp + fn) if (tp + fn) else 0
    spec = tn / (tn + fp) if (tn + fp) else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0
    exact = sum(1 for p in pairs if p["gold"] == p["pred"])
    po = sum(1 for g, p in valid if g == p) / len(valid) if valid else 0
    gc, pc = Counter(g for g, _ in valid), Counter(p for _, p in valid)
    pe = sum(gc.get(k, 0) * pc.get(k, 0) for k in (1, 2, 3)) / (len(valid) ** 2) if valid else 0
    kappa = (po - pe) / (1 - pe) if (1 - pe) else 0
    return {"n": len(pairs), "sens": sens, "spec": spec, "f1": f1,
            "acc4": exact / len(pairs) if pairs else 0, "kappa": kappa}

# ── 1. performance_matrix.csv (overall, 84-case tiered gold) ──
with open(TABLES / "performance_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["method", "n", "sensitivity_high", "specificity_high", "f1_high",
                "accuracy_4level", "cohens_kappa", "pass"])
    for m in methods:
        pairs = [{"gold": r["gold"], "pred": r["predicted"]} for r in recs if r["method"] == m]
        mm = metrics(pairs)
        passes = sum([mm["sens"] >= 0.70, mm["spec"] >= 0.60, mm["acc4"] >= 0.50, mm["kappa"] >= 0.40])
        w.writerow([m, mm["n"], round(mm["sens"], 3), round(mm["spec"], 3), round(mm["f1"], 3),
                    round(mm["acc4"], 3), round(mm["kappa"], 3), f"{passes}/4"])

# ── 2. performance_by_dataset.csv (per tier) ──
with open(TABLES / "performance_by_dataset.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tier", "gold_source", "method", "n", "sensitivity_high", "specificity_high",
                "f1_high", "accuracy_4level"])
    for tier in ("T1", "T2", "T3", "T4"):
        cids = {g["case_id"] for g in golds if tier_of(g["case_id"]) == tier}
        for m in methods:
            pairs = [{"gold": r["gold"], "pred": r["predicted"]} for r in recs
                     if r["method"] == m and r["case_id"] in cids]
            mm = metrics(pairs)
            src = next(g["gold_source"] for g in golds if g["case_id"] in cids)
            w.writerow([tier, src, m, mm["n"], round(mm["sens"], 3), round(mm["spec"], 3),
                        round(mm["f1"], 3), round(mm["acc4"], 3)])

# ── 3. dataset_summary.csv ──
with open(TABLES / "dataset_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tier", "gold_source", "n_cases", "n_high", "n_medium", "n_low", "ground_truth_method"])
    for tier in ("T1", "T2", "T3", "T4"):
        gs = [g for g in golds if tier_of(g["case_id"]) == tier]
        dist = Counter(g["gold_risk_level"] for g in gs)
        src = "DDInter ∩ Rules consensus" if tier == "T3" else gs[0]["gold_source"]
        w.writerow([tier, src, len(gs), dist.get("high", 0),
                    dist.get("medium", 0), dist.get("low", 0), gs[0]["ground_truth_method"]])

# ── 4. validation_distribution.csv (confusion matrix, full_system) ──
fs = [r for r in recs if r["method"] == "full_system"]
with open(TABLES / "validation_distribution.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gold_level", "predicted_level", "count"])
    for g in ("high", "medium", "low"):
        for p in ("high", "medium", "low"):
            n = sum(1 for r in fs if r["gold"] == g and r["predicted"] == p)
            if n:
                w.writerow([g, p, n])

# ── 5. rule_list.csv ──
with open(TABLES / "rule_list.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rule_id", "severity", "risk_type", "entity_a_flags", "entity_b_flags", "match"])
    for r in rules:
        w.writerow([r["id"], r["severity"], r.get("risk_type", ""),
                    "|".join(r.get("entity_a_flags", [])),
                    "|".join(r.get("entity_b_flags", [])),
                    r.get("match", "any")])

print("Tables written to", TABLES)
for t in TABLES.glob("*.csv"):
    print(f"  {t.name}: {sum(1 for _ in t.open(encoding='utf-8')) - 1} rows")
