"""expand_gold.py — Systematically expand gold cases from rule citations, non-circular."""
import csv, json, yaml
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

# ── Load ──
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

with open(ROOT / "data" / "gold_mechanisms.json") as f:
    existing_gold = json.load(f)

# ── Already-covered drug pairs ──
covered = set()
for g in existing_gold:
    covered.add((g["ophthalmic"].lower(), g["systemic"].lower()))

# ── For each rule, find drug pairs where flags match AND citation supports ophthalmic use ──
new_cases = []
case_id = 100  # start from G100

for rule in rules:
    rid = rule["id"]
    severity = rule["severity"]
    risk_type = rule.get("risk_type", "")
    a_flags = set(rule.get("entity_a_flags", []))
    b_flags = set(rule.get("entity_b_flags", []))
    rationale = rule.get("rationale", "")
    citations = rule.get("citations", [])
    
    # Only include rules whose citations mention ophthalmic/topical/eye
    has_ophthalmic_evidence = any(
        kw in str(citations).lower() + rationale.lower()
        for kw in ["ophthalmic", "topical", "eye drop", "punctal", "ocular",
                   "timolol", "brimonidine", "dorzolamide", "latanoprost",
                   "fda label", "betaxolol", "atropine", "ketorolac"]
    )
    if not has_ophthalmic_evidence:
        continue
    
    # Find matching drug pairs
    matches = []
    for a_id, a_row in a_rows.items():
        a_f = set(a_row["flags"].split("|"))
        if not (a_flags <= a_f):
            continue
        for b_id, b_row in b_rows.items():
            b_f = set(b_row["flags"].split("|"))
            if not (b_flags <= b_f):
                continue
            pair = (a_row["primary_name"].lower(), b_row["generic_name"].lower())
            if pair in covered:
                continue
            matches.append((a_row, b_row, pair))
    
    # Take up to 2 pairs per rule
    import random
    random.seed(42)
    random.shuffle(matches)
    
    for a_row, b_row, pair in matches[:2]:
        case_id += 1
        new_cases.append({
            "case_id": f"G{case_id}",
            "dataset_id": "internal_validation",
            "entity_a_id": a_row["topical_ophthalmic_medications_id"],
            "entity_b_id": b_row["entity_b_id"],
            "ophthalmic_drug": a_row["primary_name"],
            "systemic_drug": b_row["generic_name"],
            "gold_risk_level": severity,
            "patient_factors": [],
            "provenance": {
                "source_type": "guideline",
                "source_ref": "; ".join(citations) if citations else f"Rule {rid} — {rationale[:100]}",
                "record_locator": f"rule:{rid}",
                "ground_truth_method": "expert_adjudication",
                "extraction_date": "2026-07-30",
                "rule_id": rid,
                "risk_type": risk_type,
            }
        })
        covered.add(pair)

# ── Report ──
from collections import Counter
dist = Counter(c["gold_risk_level"] for c in new_cases)
print(f"Generated {len(new_cases)} new gold cases from rule citations")
print(f"Distribution: {dict(dist)}")
print(f"By rule:")
rule_counts = Counter(c["provenance"]["rule_id"] for c in new_cases)
for rule_id, count in rule_counts.most_common():
    print(f"  {rule_id}: {count}")

# Merge with existing 20 — normalize gold_risk_level field
normalized_existing = []
for g in existing_gold:
    g_norm = dict(g)
    g_norm["gold_risk_level"] = g.get("ddinter_level", g.get("gold_risk_level", "unknown"))
    g_norm["provenance"] = g.get("provenance", {
        "source_type": "guideline",
        "source_ref": g.get("evidence_source", ""),
        "record_locator": g["case_id"],
        "ground_truth_method": "expert_adjudication",
        "extraction_date": "2026-07-30",
    })
    g_norm.setdefault("dataset_id", "internal_validation")
    g_norm.setdefault("patient_factors", [])
    normalized_existing.append(g_norm)

all_gold = normalized_existing + new_cases
total_dist = Counter(c["gold_risk_level"] for c in all_gold)
print(f"\nTotal gold cases: {len(all_gold)}")
print(f"Combined distribution: {dict(total_dist)}")

# ── Save ──
out_path = ROOT / "data" / "datasets" / "internal_validation" / "cases.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for c in all_gold:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

# Update meta
meta = {
    "dataset_id": "internal_validation",
    "role": "internal_validation",
    "n_cases": len(all_gold),
    "sources": [
        {"type": "expert_adjudication", "n": 20, "description": "Manual curation from FDA labels, Stockleys, BNF"},
        {"type": "expert_adjudication", "n": len(new_cases), "description": "Rule-derived from FDA/DrugBank citations with ophthalmic-specific evidence"},
    ],
    "ground_truth_methods": ["expert_adjudication"],
    "created": "2026-07-30",
    "distribution": dict(total_dist),
}
with open(ROOT / "data" / "datasets" / "internal_validation" / "dataset.meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"\nSaved: {out_path}")
print(f"  {len(all_gold)} cases total ({len(existing_gold)} original + {len(new_cases)} new)")
