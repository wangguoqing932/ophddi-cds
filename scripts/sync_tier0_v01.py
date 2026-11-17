#!/usr/bin/env python3
"""Phase 3→4 gate: Freeze Tier 0 v0.1, sync rules.yaml, re-verify citations."""
import json, yaml, hashlib, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds")
MATRIX = ROOT / "outputs" / "tier0_edge_matrix.json"
RULES_PATH = ROOT / "configs" / "rules.yaml"
PROGRESS = ROOT / ".executor" / "progress.json"

def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

# ---- 1. Load Tier 0 matrix ----
matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

# Build tier lookup from matrix
tier_lookup = {}
for e in matrix["edges"]:
    tier_lookup[e["rule_id"]] = {
        "tier": e["tier"],
        "output_class": e["output_class"],
        "risk_behavior": e["risk_behavior"],
        "evidence_tier": e["evidence_tier"],
        "source_role": e["source_role"],
        "entity_scope": e.get("entity_scope", ""),
        "clinical_outcome": e["clinical_outcome"],
        "action": e["action"],
    }

# ---- 2. Sync rules.yaml ----
rules = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))

for rule in rules["rules"]:
    rid = rule["id"]
    cls = tier_lookup.get(rid, {})
    tier = cls.get("tier", "exclude")
    
    ep = rule.get("evidence_policy", {})
    
    if tier == "0A":
        ep["output_class"] = "clinical_ddi"
        ep["support_tier"] = "direct_clinical"
        ep["action_behavior"] = "scoped_clinical_review"
        ep["claim_scope"] = f"direct_ophthalmic: {cls.get('entity_scope', '')}"
    elif tier == "0B":
        ep["output_class"] = "precaution"
        ep["support_tier"] = "contextual_clinical"
        ep["action_behavior"] = "precautionary_review"
        ep["claim_scope"] = f"{cls.get('evidence_tier', 'class_extrapolated')}: {cls.get('entity_scope', '')}"
    else:  # exclude
        ep["output_class"] = "theoretical_mechanism"
        ep["support_tier"] = "mechanism_candidate"
        ep["action_behavior"] = "informational_only"
        ep["claim_scope"] = "excluded from Tier 0 — theoretical or no ophthalmic DDI evidence"
    
    ep["tier"] = tier
    rule["evidence_policy"] = ep

# Patient factors → 0B
for pf_id, pf in rules.get("patient_factor_rules", {}).items():
    if "evidence_policy" not in pf:
        pf["evidence_policy"] = {}
    pf["evidence_policy"]["output_class"] = "precaution"
    pf["evidence_policy"]["support_tier"] = "contextual_clinical"
    pf["evidence_policy"]["action_behavior"] = "precautionary_review"
    pf["evidence_policy"]["claim_scope"] = "contextual patient-vulnerability medication review"
    pf["evidence_policy"]["tier"] = "0B"

# Backup original
bak = RULES_PATH.with_suffix(".yaml.bak.v0.1")
shutil.copy(RULES_PATH, bak)

# Write updated rules
RULES_PATH.write_text(yaml.dump(rules, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(f"Step 2: rules.yaml synced with Tier 0 v0.1 (backup: {bak.name})")

# ---- 3. Update matrix version ----
matrix["version"] = "0.1"
matrix["frozen_date"] = "2026-07-27"
matrix["rules_yaml_sha256"] = sha256(RULES_PATH)
MATRIX.write_text(json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Step 3: Matrix frozen as v0.1 (SHA: {matrix['rules_yaml_sha256'][:16]}...)")

# ---- 4. Summary ----
counts = {"0A": 0, "0B": 0, "exclude": 0}
for e in matrix["edges"]:
    counts[e["tier"]] = counts.get(e["tier"], 0) + 1
print(f"\nTier 0 v0.1 frozen:")
print(f"  0A (clinical_ddi):    {counts['0A']}")
print(f"  0B (precaution):      {counts['0B']}")
print(f"  Excluded:             {counts['exclude']}")
print(f"  Patient factors:      3 (all 0B/precaution)")
print(f"\nNext: python scripts/verify_rule_citations.py --project-root . --refresh")
