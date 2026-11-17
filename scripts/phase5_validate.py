#!/usr/bin/env python3
"""Phase 5 v3.0: Corrected validation — triggered-subset metrics, silent-case analysis."""
from __future__ import annotations

import argparse, csv, json, os, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.risk_rules import RuleEngine

# ── helpers ──────────────────────────────────────────────
def load_cases(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def load_entity_flags():
    """Load entity_a and entity_b flag maps from CSVs."""
    import csv as csv_mod
    a_map, b_map = {}, {}
    with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8", newline="") as f:
        for row in csv_mod.DictReader(f):
            a_map[row["topical_ophthalmic_medications_id"]] = row["flags"].split("|") if row["flags"] else []
    with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8", newline="") as f:
        for row in csv_mod.DictReader(f):
            b_map[row["entity_b_id"]] = row["flags"].split("|") if row["flags"] else []
    return a_map, b_map

def rule_risk(engine: RuleEngine, a_flags: list[str], b_flags: list[str], pf: list[str] = None) -> tuple[str, list[str]]:
    """Return (risk_level, [matched_rule_ids])."""
    class E:
        def __init__(self, flags): self.flags = flags
    result = engine.evaluate(E(a_flags), E(b_flags), patient_factors=pf or [])
    risk = result.risk_level.value if hasattr(result.risk_level, 'value') else str(result.risk_level)
    rule_ids = [s.rule_id for s in result.signals]
    return risk, rule_ids

def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict:
    levels = ["high", "medium", "low"]
    cm = defaultdict(lambda: defaultdict(int))
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1

    metrics = {}
    for level in levels:
        tp = cm[level][level]
        fn = sum(cm[level][l] for l in levels if l != level)
        fp = sum(cm[l][level] for l in levels if l != level)
        tn = sum(cm[l][m] for l in levels if l != level for m in levels if m != level)

        sens = tp / (tp + fn) if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics[f"sensitivity_{level}"] = round(sens, 3)
        metrics[f"specificity_{level}"] = round(spec, 3)
        metrics[f"f1_{level}"] = round(2 * tp / (2 * tp + fp + fn), 3) if (2 * tp + fp + fn) > 0 else 0

    exact = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    metrics["accuracy_4level"] = round(exact / len(y_true), 3) if y_true else 0

    n = len(y_true)
    obs = exact / n if n else 0
    exp = sum((sum(1 for t in y_true if t == l) / n) * (sum(1 for p in y_pred if p == l) / n) for l in levels)
    metrics["cohens_kappa"] = round((obs - exp) / (1 - exp), 3) if (1 - exp) > 0 else 0

    return metrics

# ── main ──────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, default=ROOT)
    args = ap.parse_args()
    root = args.project_root.resolve()

    print("=" * 60)
    print("PHASE 5 v3.0: Corrected Validation")
    print("=" * 60)

    # ── Load ──────────────────────────────────────────────
    a_map, b_map = load_entity_flags()
    engine = RuleEngine(root / "configs" / "rules.yaml")
    print(f"\n✅ Rule engine: {len(engine.config['rules'])} rules loaded")

    # Load all cases
    all_cases = []
    for ds_id in ["dev-ddinter", "int-pubmed"]:
        path = root / "data" / "datasets" / ds_id / "cases.jsonl"
        if path.exists():
            cases = load_cases(path)
            for c in cases:
                c["_dataset"] = ds_id
            all_cases.extend(cases)
            print(f"   {ds_id}: {len(cases)} cases")

    # ═══════════════════════════════════════════════════════
    # STEP 1: Run all cases → split triggered vs silent
    # ═══════════════════════════════════════════════════════
    triggered = []
    silent = []
    all_results = []

    for c in all_cases:
        a_id = c.get("entity_a_id", "")
        b_id = c.get("entity_b_id", "")
        a_flags = a_map.get(a_id, [])
        b_flags = b_map.get(b_id, [])
        gold = c.get("gold_risk_level", "unknown")

        if not a_flags or not b_flags:
            continue

        risk, rules = rule_risk(engine, a_flags, b_flags)
        c["_pred_risk"] = risk
        c["_matched_rules"] = rules

        if rules:
            triggered.append(c)
        else:
            silent.append(c)

    print(f"\n📊 All cases: {len(all_cases)}")
    print(f"   🟢 Triggered (≥1 rule): {len(triggered)}")
    print(f"   🔕 Silent (no rule):    {len(silent)}")

    # ═══════════════════════════════════════════════════════
    # STEP 2: Metrics on triggered subset
    # ═══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("STEP 2: Metrics on TRIGGERED subset")
    print("=" * 60)

    for ds_id in ["dev-ddinter", "int-pubmed"]:
        ds_triggered = [c for c in triggered if c["_dataset"] == ds_id]
        if not ds_triggered:
            continue

        y_true = [c["gold_risk_level"] for c in ds_triggered]
        y_pred = [c["_pred_risk"] for c in ds_triggered]
        metrics = compute_metrics(y_true, y_pred)

        print(f"\n   {ds_id} ({len(ds_triggered)} triggered cases):")
        print(f"     Accuracy:  {metrics['accuracy_4level']:.3f}")
        print(f"     Sens (high): {metrics.get('sensitivity_high', 0):.3f}")
        print(f"     Spec (high): {metrics.get('specificity_high', 0):.3f}")
        print(f"     Sens (med):  {metrics.get('sensitivity_medium', 0):.3f}")
        print(f"     κ:          {metrics['cohens_kappa']:.3f}")

        # Per-dataset distribution
        dist = Counter((c["gold_risk_level"], c["_pred_risk"]) for c in ds_triggered)
        print(f"     Confusion: ", end="")
        for (t, p), n in sorted(dist.items(), key=lambda x: -x[1])[:8]:
            print(f"{t}→{p}={n} ", end="")
        print()

    # Rule consistency on triggered subset only
    run1 = [c["_pred_risk"] for c in triggered]
    run2 = [rule_risk(engine, a_map.get(c["entity_a_id"], []), b_map.get(c["entity_b_id"], []))[0] for c in triggered]
    consistent = sum(1 for a, b in zip(run1, run2) if a == b)
    print(f"\n   Rule consistency (triggered): {consistent}/{len(triggered)} = {consistent/len(triggered):.1%}" if triggered else "N/A")

    # ═══════════════════════════════════════════════════════
    # STEP 3: Silent case analysis
    # ═══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("STEP 3: Silent case analysis (no rule triggered)")
    print("=" * 60)

    # Cases where DDInter says medium/high but system says low (no rule)
    missed = [c for c in silent if c["gold_risk_level"] in ("high", "medium")]
    print(f"\n   🔕 Silent + DDInter medium/high: {len(missed)} cases")
    print(f"      → These are potential coverage gaps")

    if missed:
        # Sample to show patterns
        print(f"\n   Sample missed cases (showing 10):")
        for c in missed[:10]:
            a_flags = a_map.get(c["entity_a_id"], [])
            b_flags = b_map.get(c["entity_b_id"], [])
            print(f"     {c['_dataset']} {c['case_id']}: "
                  f"A={c['entity_a_id']}({','.join(a_flags[:3])}) × "
                  f"B={c['entity_b_id']}({','.join(b_flags[:3])}) "
                  f"gold={c['gold_risk_level']} pred=low")

        # Flag patterns
        a_flag_gaps = Counter()
        b_flag_gaps = Counter()
        for c in missed:
            for f in a_map.get(c["entity_a_id"], []):
                a_flag_gaps[f] += 1
            for f in b_map.get(c["entity_b_id"], []):
                b_flag_gaps[f] += 1

        print(f"\n   Top Entity A flags in missed cases:")
        for flag, n in a_flag_gaps.most_common(10):
            print(f"     {flag}: {n}")
        print(f"\n   Top Entity B flags in missed cases:")
        for flag, n in b_flag_gaps.most_common(10):
            print(f"     {flag}: {n}")

    # Truly low-risk silent cases (DDInter says low, system says low)
    ok_silent = [c for c in silent if c["gold_risk_level"] == "low"]
    print(f"\n   ✅ Silent + DDInter low: {len(ok_silent)} cases (correctly silent)")

    # ═══════════════════════════════════════════════════════
    # OUTPUT
    # ═══════════════════════════════════════════════════════
    tables_dir = root / "outputs" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # dataset_summary.csv
    with open(tables_dir / "dataset_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "role", "source_type", "n_total", "n_triggered", "n_silent",
                    "n_missed_high_med", "n_ok_low"])
        for ds_id in ["dev-ddinter", "int-pubmed"]:
            ds_cases = [c for c in all_cases if c["_dataset"] == ds_id]
            t = [c for c in triggered if c["_dataset"] == ds_id]
            s = [c for c in silent if c["_dataset"] == ds_id]
            m = [c for c in missed if c["_dataset"] == ds_id]
            ok = [c for c in ok_silent if c["_dataset"] == ds_id]
            w.writerow([ds_id, "dev" if ds_id == "dev-ddinter" else "internal_validation",
                        "DDInter" if ds_id == "dev-ddinter" else "PubMed",
                        len(ds_cases), len(t), len(s), len(m), len(ok)])

    # performance_by_dataset.csv
    with open(tables_dir / "performance_by_dataset.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "subset", "n", "accuracy", "sens_high", "spec_high",
                    "sens_medium", "spec_medium", "cohens_kappa"])
        for ds_id in ["dev-ddinter", "int-pubmed"]:
            for subset_name, subset in [("triggered", [c for c in triggered if c["_dataset"] == ds_id]),
                                         ("all", [c for c in all_cases if c["_dataset"] == ds_id])]:
                if not subset:
                    continue
                y_true = [c["gold_risk_level"] for c in subset]
                y_pred = [c["_pred_risk"] for c in subset]
                m = compute_metrics(y_true, y_pred)
                w.writerow([ds_id, subset_name, len(subset), m["accuracy_4level"],
                           m.get("sensitivity_high", 0), m.get("specificity_high", 0),
                           m.get("sensitivity_medium", 0), m.get("specificity_medium", 0),
                           m["cohens_kappa"]])

    print(f"\n📄 Tables written to {tables_dir}")

    # Report
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "phase": "5",
        "version": "v3.0",
        "summary": {
            "total_cases": len(all_cases),
            "triggered": len(triggered),
            "silent": len(silent),
            "missed_high_medium": len(missed),
            "correctly_silent_low": len(ok_silent),
        },
        "rule_consistency_triggered": consistent / len(triggered) if triggered else 1.0,
    }
    (root / "outputs" / "phase5_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n📄 Report: outputs/phase5_report.json")
    print("\n" + "=" * 60)
    print("PHASE 5 DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
