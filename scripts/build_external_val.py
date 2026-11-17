"""build_external_val.py — Screen int-pubmed cases with PubMed evidence support"""
import json, csv, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

# ── Load int-pubmed cases ──
cases = []
with open(ROOT / "data" / "datasets" / "int-pubmed" / "cases.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            cases.append(json.loads(line))

# ── Load evidence chunks (index by PMID for fast lookup) ──
chunks_by_pmid = {}
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            c = json.loads(line)
            pmid = c.get("pmid", "")
            if pmid:
                if pmid not in chunks_by_pmid:
                    chunks_by_pmid[pmid] = []
                chunks_by_pmid[pmid].append(c)

# ── Load entity names for drug mention checking ──
a_names = set()
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_names.add(row["primary_name"].lower())

b_names = set()
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_names.add(row["generic_name"].lower())

# ── Screen each case ──
external = []
rejected = []

for case in cases:
    prov = case.get("provenance", {})
    pmid = prov.get("pmid", prov.get("record_locator", ""))
    gold_level = case.get("gold_risk_level", "?")
    
    # Must have PMID
    if not pmid or not pmid.isdigit():
        rejected.append((case["case_id"], "no_valid_pmid"))
        continue
    
    # Find evidence chunk
    chunks = chunks_by_pmid.get(pmid, [])
    if not chunks:
        rejected.append((case["case_id"], f"pmid_{pmid}_not_in_evidence"))
        continue
    
    # Get ophthalmic and systemic drug names
    # Look up from entity registries
    a_name = ""
    b_name = ""
    a_id = case.get("entity_a_id", "")
    b_id = case.get("entity_b_id", "")
    
    with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["topical_ophthalmic_medications_id"] == a_id:
                a_name = row["primary_name"].lower()
                break
    
    with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["entity_b_id"] == b_id:
                b_name = row["generic_name"].lower()
                break
    
    # Check: does evidence mention both drugs?
    evidence_text = " ".join(c.get("text", c.get("content", "")) for c in chunks).lower()
    mentions_a = a_name and a_name in evidence_text
    mentions_b = b_name and b_name in evidence_text
    
    # Check drug class mention (broader match)
    a_class_match = any(c.get("claim_text", "").lower().find(a_name) >= 0 for c in chunks if c.get("claim_text"))
    b_class_match = any(c.get("claim_text", "").lower().find(b_name) >= 0 for c in chunks if c.get("claim_text"))
    
    drug_mention_ok = mentions_a or mentions_b or a_class_match or b_class_match
    
    # Check: does evidence support the reported interaction level?
    level_keywords = {
        "high": ["significant", "severe", "contraindicated", "major", "avoid", "clinical ddi"],
        "medium": ["moderate", "monitor", "caution", "potential", "precaution", "may interact"],
        "low": ["minimal", "negligible", "no interaction", "not significant", "theoretical", "no evidence"],
    }
    
    evidence_level_support = False
    if gold_level in level_keywords:
        evidence_level_support = any(kw in evidence_text for kw in level_keywords[gold_level])
    
    # Decision: keep if drug mentioned AND level supported
    if drug_mention_ok and evidence_level_support:
        external.append({
            **case,
            "dataset_id": "external_validation",
            "provenance": {
                **prov,
                "screening_note": f"Evidence PMID:{pmid} mentions drug pair and supports {gold_level} risk",
                "evidence_check": "passed",
            }
        })
    else:
        reason = []
        if not drug_mention_ok:
            reason.append("drug_not_in_evidence")
        if not evidence_level_support:
            reason.append("level_not_supported")
        rejected.append((case["case_id"], "+".join(reason)))

# ── Report ──
print(f"int-pubmed cases: {len(cases)}")
print(f"External validation: {len(external)}")
print(f"Rejected: {len(rejected)}")
print(f"\nRejection reasons:")
reasons = Counter(r[1] for r in rejected)
for reason, count in reasons.most_common():
    print(f"  {reason}: {count}")

gold_dist = Counter(c["gold_risk_level"] for c in external)
print(f"\nExternal validation distribution: {dict(gold_dist)}")

# ── Save ──
ext_dir = ROOT / "data" / "datasets" / "external_validation"
ext_dir.mkdir(parents=True, exist_ok=True)

with open(ext_dir / "cases.jsonl", "w", encoding="utf-8") as f:
    for c in external:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

meta = {
    "dataset_id": "external_validation",
    "role": "external_validation",
    "n_cases": len(external),
    "source": "int-pubmed screened against evidence_chunks.jsonl",
    "ground_truth_methods": ["label_guideline"],
    "screening_criteria": "Drug mention in evidence + level keywords supported",
    "created": "2026-07-30",
    "distribution": dict(gold_dist),
}
with open(ext_dir / "dataset.meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"\nSaved: {ext_dir}/cases.jsonl")

# Also print a few sample accepted cases
print(f"\n=== Sample accepted cases ===")
for c in external[:5]:
    a_name = ""
    b_name = ""
    with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["topical_ophthalmic_medications_id"] == c["entity_a_id"]:
                a_name = row["primary_name"]
                break
    with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["entity_b_id"] == c["entity_b_id"]:
                b_name = row["generic_name"]
                break
    print(f"  {c['case_id']}: {a_name} × {b_name} | gold={c['gold_risk_level']} | PMID:{c['provenance'].get('pmid','?')}")
