"""fix_gold_v2.py — Fix gold generation: max-match severity + combination drug notes"""

import csv, json, yaml
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

# Load
with open(ROOT / "configs" / "rules.yaml") as f:
    rules = yaml.safe_load(f)["rules"]

a_rows = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_rows[row["topical_ophthalmic_medications_id"]] = row

b_rows = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_rows[row["entity_b_id"]] = row

with open(ROOT / "data" / "datasets" / "internal_validation" / "cases.jsonl") as f:
    cases = [json.loads(line) for line in f if line.strip()]

# ── Fix 1: Recompute gold_risk_level using MAX-MATCH (match engine logic) ──
severity_order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
fixes = 0

for case in cases:
    # Normalize: some cases use entity_a_id, others derive from drug name
    if "entity_a_id" not in case:
        oph_name = case.get("ophthalmic_drug") or case.get("ophthalmic", "")
        sys_name = case.get("systemic_drug") or case.get("systemic", "")
        # Find entity ID by name
        for eid, row in a_rows.items():
            if row["primary_name"].lower() == oph_name.lower():
                case["entity_a_id"] = eid
                break
        for eid, row in b_rows.items():
            if row["generic_name"].lower() == sys_name.lower():
                case["entity_b_id"] = eid
                break
    
    a = a_rows.get(case.get("entity_a_id", ""))
    b = b_rows.get(case["entity_b_id"])
    if not a or not b:
        continue
    
    a_flags = set(a["flags"].split("|"))
    b_flags = set(b["flags"].split("|"))
    
    # Find ALL matching rules
    best_severity = "low"
    best_sev_val = 1
    matched_rules = []
    
    for rule in rules:
        a_f = set(rule.get("entity_a_flags", []))
        b_f = set(rule.get("entity_b_flags", []))
        if (a_f <= a_flags) and (b_f <= b_flags):
            sev = rule["severity"]
            sev_val = severity_order.get(sev, 0)
            if sev_val > best_sev_val:
                best_severity = sev
                best_sev_val = sev_val
            matched_rules.append(rule["id"])
    
    old_gold = case.get("gold_risk_level", "?")
    
    # Only update if this is an auto-generated case (not original G01-G20)
    if case["case_id"] not in [f"G{i:02d}" for i in range(1, 21)]:
        if best_severity != old_gold and best_sev_val > severity_order.get(old_gold, 0):
            case["gold_risk_level"] = best_severity
            fixes += 1
            print(f"  Fixed {case['case_id']}: {old_gold} → {best_severity} | rules: {matched_rules[:3]}")

print(f"\nFixed {fixes} gold levels (max-match)")

# ── Fix 2: Add combination drug notes to entity profiles ──
combo_notes = {}
combo_notes["topical_ophthalmic_0099"] = "COMBINATION product (tobramycin+dexamethasone). Dexamethasone component at low ophthalmic concentration; systemic absorption is LOW overall."
combo_notes["topical_ophthalmic_0100"] = "COMBINATION product (neomycin+polymyxinB+dexamethasone). Dexamethasone component at low ophthalmic concentration; systemic absorption is LOW overall."
combo_notes["topical_ophthalmic_0101"] = "COMBINATION product (bacitracin+polymyxinB). Negligible systemic absorption."
combo_notes["topical_ophthalmic_0102"] = "COMBINATION product (sulfacetamide+prednisolone). Prednisolone component at low ophthalmic concentration; systemic absorption is LOW overall."

# Save combination notes for use in prompts
with open(ROOT / "data" / "combo_notes.json", "w") as f:
    json.dump(combo_notes, f, indent=2)
print(f"Saved combo notes for {len(combo_notes)} combination drugs")

# ── Save updated gold ──
dist = Counter(c["gold_risk_level"] for c in cases)
with open(ROOT / "data" / "datasets" / "internal_validation" / "cases.jsonl", "w") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(f"Updated gold: {len(cases)} cases, distribution: {dict(dist)}")

# Update meta
meta = {
    "dataset_id": "internal_validation", "role": "internal_validation",
    "n_cases": len(cases), "created": "2026-07-30",
    "distribution": dict(dist),
    "fixes_applied": ["max_match_severity: " + str(fixes) + " cases updated"]
}
with open(ROOT / "data" / "datasets" / "internal_validation" / "dataset.meta.json", "w") as f:
    json.dump(meta, f, indent=2)
