#!/usr/bin/env python3
"""Tag evidence chunks with usage_scope per Tier 0 v0.1 rules."""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds")
MATRIX = ROOT / "outputs" / "tier0_edge_matrix.json"
INPUT = ROOT / "data" / "seed" / "evidence_chunks_tier0.jsonl"
OUTPUT = ROOT / "data" / "seed" / "evidence_chunks_tier0_tagged.jsonl"
MANIFEST = ROOT / "outputs" / "phase4_evidence_manifest.json"

matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
chunks = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]

# Build tier lookup
tier_map = {}
for e in matrix["edges"]:
    tier_map[e["rule_id"]] = e["tier"]

# 0A rules
tier0a_rules = {rid for rid, tier in tier_map.items() if tier == "0A"}
# 0B rules
tier0b_rules = {rid for rid, tier in tier_map.items() if tier == "0B"}
# Patient factors
pf_ids = {"patient_factor:elderly", "patient_factor:renal_impairment", "patient_factor:polypharmacy"}

# Tag each chunk
tagged = []
tag_counts = Counter()
rule_doc_counts = defaultdict(lambda: {"tier0_direct_alert": 0, "tier0_exposure_support": 0, "tier1_conditional_review": 0, "patient_factor_support": 0})
needs_review = []

for c in chunks:
    rule_ids = set(c.get("rule_ids", []))
    level = c.get("evidence_level", "?")
    source_type = c.get("source_type", "")
    title = c.get("title", "").lower()
    
    # Determine primary tier from rule_ids
    matched_0a = rule_ids & tier0a_rules
    matched_0b = rule_ids & tier0b_rules
    matched_pf = rule_ids & pf_ids
    
    usage_tags = []
    
    # ---- Tag 0A direct alert ----
    if matched_0a:
        # Direct alert: A/B level + rule is 0A
        if level in ("A", "B"):
            usage_tags.append("tier0_direct_alert")
            for r in matched_0a:
                rule_doc_counts[r]["tier0_direct_alert"] += 1
    
    # ---- Tag 0A exposure support ----
    if matched_0a:
        # Exposure support: FDA label, absorption data, regulatory source
        is_exposure = (
            source_type == "regulatory_label" or
            "systemic absorption" in title or
            "bioavailability" in title or
            "fda" in title or
            "label" in title or
            level == "A"
        )
        if is_exposure and "tier0_direct_alert" not in usage_tags:
            usage_tags.append("tier0_exposure_support")
            for r in matched_0a:
                rule_doc_counts[r]["tier0_exposure_support"] += 1
        elif not is_exposure and "tier0_direct_alert" not in usage_tags:
            # Falls to 0B if it's 0A rule but not direct/exposure evidence
            usage_tags.append("tier1_conditional_review")
            for r in matched_0a:
                rule_doc_counts[r]["tier1_conditional_review"] += 1
    
    # ---- Tag 0B conditional review ----
    if matched_0b:
        usage_tags.append("tier1_conditional_review")
        for r in matched_0b:
            rule_doc_counts[r]["tier1_conditional_review"] += 1
    
    # ---- Tag patient factor support ----
    if matched_pf:
        usage_tags.append("patient_factor_support")
        for r in matched_pf:
            rule_doc_counts[r]["patient_factor_support"] += 1
    
    # Deduplicate tags
    usage_tags = list(set(usage_tags))
    
    # If somehow no tag assigned, mark for review
    if not usage_tags:
        usage_tags = ["needs_review"]
        needs_review.append(c["evidence_id"])
    
    for tag in usage_tags:
        tag_counts[tag] += 1
    
    c["usage_scope"] = usage_tags
    tagged.append(c)

# Write tagged output
with open(OUTPUT, "w", encoding="utf-8") as f:
    for c in tagged:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

# Build manifest
manifest = {
    "phase": "Phase 4",
    "version": "0.1",
    "tier0_version": "0.1",
    "total_docs": len(tagged),
    "usage_scope_counts": dict(tag_counts),
    "by_evidence_level": dict(Counter(c["evidence_level"] for c in tagged)),
    "docs_per_rule": {rid: counts for rid, counts in rule_doc_counts.items()},
    "needs_review": len(needs_review),
    "gate_criteria": {
        "all_docs_have_usage_scope": len(needs_review) == 0,
        "all_docs_have_rule_or_pf_binding": all(
            bool(set(c.get("rule_ids",[])) & (tier0a_rules | tier0b_rules | pf_ids))
            for c in tagged
        ),
        "each_0A_has_direct_alert": all(
            rule_doc_counts[r]["tier0_direct_alert"] >= 1
            for r in tier0a_rules
        ),
        "each_0B_has_conditional_review": all(
            rule_doc_counts[r]["tier1_conditional_review"] >= 1
            for r in tier0b_rules
        ),
        "each_PF_has_support": all(
            rule_doc_counts[r]["patient_factor_support"] >= 1
            for r in pf_ids
        ),
    },
    "retrieval_limits": {
        "tier0_direct_alert": "3-8 docs per rule",
        "tier0_exposure_support": "combined with direct_alert evidence",
        "tier1_conditional_review": "2-5 docs per rule",
        "patient_factor_support": "2-4 docs per factor",
    }
}

with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("=== USAGE SCOPE TAGGING COMPLETE ===")
print(f"Total docs: {len(tagged)}")
print(f"\nTag distribution:")
for tag, count in tag_counts.most_common():
    print(f"  {tag}: {count} ({count*100//len(tagged)}%)")
print(f"\nNeeds review: {len(needs_review)}")

# Gate check
print(f"\n=== GATE CRITERIA ===")
for k, v in manifest["gate_criteria"].items():
    status = "PASS" if v else "FAIL"
    print(f"  [{status}] {k}")

# Per-rule summary
print(f"\n=== PER-RULE EVIDENCE ===")
for rid, counts in sorted(rule_doc_counts.items()):
    tier = tier_map.get(rid, "??")
    total = sum(counts.values())
    parts = [f"{k}={v}" for k, v in counts.items() if v > 0]
    print(f"  [{tier}] {rid}: {total} docs ({', '.join(parts)})")
