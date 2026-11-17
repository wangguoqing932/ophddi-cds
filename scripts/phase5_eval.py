#!/usr/bin/env python3
"""phase5_eval.py — Run rule engine against internal_validation, compute all skill-required metrics."""

import csv, json, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.risk_rules import RuleEngine
from ophthalmic_ddi_cds_agent.schemas import EntityA, EntityB

# ── Load registries ──
def load_a():
    ent = {}
    with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            flags = [f.strip() for f in row["flags"].split("|") if f.strip()]
            mechs = [m.strip() for m in row.get("active_mechanisms","").split("|") if m.strip()] if row.get("active_mechanisms") else []
            ent[row["topical_ophthalmic_medications_id"]] = EntityA(
                entity_a_id=row["topical_ophthalmic_medications_id"],
                primary_name=row["primary_name"], category=row.get("category",""),
                flags=flags, active_mechanisms=mechs, evidence_sources=[])
    return ent

def load_b():
    ent = {}
    with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            flags = [f.strip() for f in row["flags"].split("|") if f.strip()]
            paths = [p.strip() for p in row.get("metabolic_pathways","").split("|") if p.strip()] if row.get("metabolic_pathways") else []
            ent[row["entity_b_id"]] = EntityB(
                entity_b_id=row["entity_b_id"],
                generic_name=row["generic_name"], drug_class=row.get("drug_class",""),
                flags=flags, metabolic_pathways=paths, transporter_substrates=[])
    return ent

ent_a = load_a()
ent_b = load_b()
engine = RuleEngine(ROOT / "configs" / "rules.yaml")

# ── Evaluate ──
def eval_dataset(cases_path, dataset_name):
    cases = []
    with open(cases_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    
    results = []
    for c in cases:
        a = ent_a.get(c["entity_a_id"])
        b = ent_b.get(c["entity_b_id"])
        if not a or not b:
            continue
        
        assessment = engine.evaluate(a, b, c.get("patient_factors", []))
        system_level = assessment.risk_level.value
        gold_level = c.get("gold_risk_level", "unknown")
        
        results.append({
            "case_id": c["case_id"],
            "ophthalmic": a.primary_name,
            "systemic": b.generic_name,
            "gold": gold_level,
            "predicted": system_level,
            "triggered": len(assessment.signals) > 0,
            "signals": [s.rule_id for s in assessment.signals],
        })
    
    return results

# ── Metrics ──
def compute_metrics(results, dataset_name):
    n = len(results)
    level_map = {"low": 1, "medium": 2, "high": 3, "unknown": 0}
    
    # Binary: high vs rest
    def binary_metrics(pos_levels):
        tp = sum(1 for r in results if r["gold"] in pos_levels and r["predicted"] in pos_levels)
        fp = sum(1 for r in results if r["gold"] not in pos_levels and r["predicted"] in pos_levels)
        fn = sum(1 for r in results if r["gold"] in pos_levels and r["predicted"] not in pos_levels)
        tn = sum(1 for r in results if r["gold"] not in pos_levels and r["predicted"] not in pos_levels)
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0
        return sens, spec, f1, tp, fp, fn, tn
    
    sens_h, spec_h, f1_h, *_ = binary_metrics(["high"])
    sens_mh, spec_mh, f1_mh, *_ = binary_metrics(["medium", "high"])
    
    # 4-level exact accuracy
    exact = sum(1 for r in results if r["predicted"] == r["gold"] and r["gold"] != "unknown")
    acc_4 = exact / sum(1 for r in results if r["gold"] != "unknown") if n > 0 else 0
    
    # Cohen's κ
    valid = [(level_map[r["gold"]], level_map[r["predicted"]]) for r in results 
             if r["gold"] != "unknown" and r["predicted"] != "unknown"]
    if valid:
        # Observed agreement
        po = sum(1 for g, p in valid if g == p) / len(valid)
        # Expected agreement
        gold_counts = Counter(g for g, _ in valid)
        pred_counts = Counter(p for _, p in valid)
        pe = sum(gold_counts.get(k, 0) * pred_counts.get(k, 0) for k in range(1,4)) / (len(valid) ** 2)
        kappa = (po - pe) / (1 - pe) if (1 - pe) > 0 else 0
    else:
        po = pe = kappa = 0
    
    # Level distribution
    pred_dist = Counter(r["predicted"] for r in results)
    gold_dist = Counter(r["gold"] for r in results)
    
    print(f"\n{'='*60}")
    print(f"  {dataset_name} (n={n})")
    print(f"{'='*60}")
    print(f"  Gold distribution:     H={gold_dist.get('high',0)} M={gold_dist.get('medium',0)} L={gold_dist.get('low',0)} U={gold_dist.get('unknown',0)}")
    print(f"  Predicted distribution: H={pred_dist.get('high',0)} M={pred_dist.get('medium',0)} L={pred_dist.get('low',0)} U={pred_dist.get('unknown',0)}")
    print(f"  Triggered: {sum(1 for r in results if r['triggered'])}/{n} ({sum(1 for r in results if r['triggered'])/n*100:.0f}%)")
    print(f"")
    print(f"  Sensitivity (high):     {sens_h:.3f}")
    print(f"  Specificity (high):     {spec_h:.3f}")
    print(f"  F1 (high):              {f1_h:.3f}")
    print(f"  Sensitivity (med+high): {sens_mh:.3f}")
    print(f"  Specificity (med+high): {spec_mh:.3f}")
    print(f"  F1 (med+high):          {f1_mh:.3f}")
    print(f"  4-level accuracy:       {acc_4:.3f}")
    print(f"  Cohen's κ:              {kappa:.3f}")
    
    return {
        "dataset": dataset_name, "n": n,
        "sens_high": round(sens_h, 3), "spec_high": round(spec_h, 3), "f1_high": round(f1_h, 3),
        "sens_medhigh": round(sens_mh, 3), "spec_medhigh": round(spec_mh, 3), "f1_medhigh": round(f1_mh, 3),
        "acc_4level": round(acc_4, 3), "cohens_kappa": round(kappa, 3),
        "triggered_rate": round(sum(1 for r in results if r['triggered'])/n, 3),
    }

# ── Main ──
all_metrics = []

# 1. Internal validation (newly built)
iv_path = ROOT / "data" / "datasets" / "internal_validation" / "cases.jsonl"
if iv_path.exists():
    iv_results = eval_dataset(iv_path, "internal_validation")
    m = compute_metrics(iv_results, "internal_validation")
    all_metrics.append(m)

# 2. int-pubmed (label_guideline)
ip_path = ROOT / "data" / "datasets" / "int-pubmed" / "cases.jsonl"
if ip_path.exists():
    ip_results = eval_dataset(ip_path, "int-pubmed")
    m = compute_metrics(ip_results, "int-pubmed")
    all_metrics.append(m)

# 3. dev-ddinter (development)
dd_path = ROOT / "data" / "datasets" / "dev-ddinter" / "cases.jsonl"
if dd_path.exists():
    dd_results = eval_dataset(dd_path, "dev-ddinter")
    m = compute_metrics(dd_results, "dev-ddinter")
    all_metrics.append(m)

# ── Combined summary ──
print(f"\n{'='*60}")
print(f"  COMBINED (all 3 datasets)")
print(f"{'='*60}")
all_n = sum(m["n"] for m in all_metrics)
print(f"  Total cases: {all_n}")
print(f"")
for key in ["sens_high","spec_high","f1_high","acc_4level","cohens_kappa"]:
    vals = [m[key] for m in all_metrics]
    avg = sum(vals) / len(vals)
    print(f"  {key}: mean={avg:.3f}  per_dataset={vals}")

# Save
out_path = ROOT / "output" / "phase5_metrics.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump({"generated": "2026-07-30", "metrics": all_metrics}, f, indent=2)
print(f"\nSaved: {out_path}")
