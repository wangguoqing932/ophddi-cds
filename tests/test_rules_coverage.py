"""
Test: Verify all 14 rules + 3 patient factor rules have:
1. Valid rule definitions
2. At least one triggerable A×B entity pair
3. SHA256 matches citation verification report
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_entity_flags_a() -> dict[str, set[str]]:
    """Load Entity A flags from CSV. Returns {id: {flag1, flag2, ...}}."""
    result = {}
    path = PROJECT_ROOT / "data" / "seed" / "entities_a.csv"
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eid = row.get("topical_ophthalmic_medications_id", "")
            flags = set()
            for f_val in row.get("flags", "").split("|"):
                f_val = f_val.strip()
                if f_val:
                    flags.add(f_val)
            result[eid] = flags
    return result


def load_entity_flags_b() -> dict[str, set[str]]:
    """Load Entity B flags from CSV. Returns {id: {flag1, flag2, ...}}."""
    result = {}
    path = PROJECT_ROOT / "data" / "seed" / "entities_b.csv"
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eid = row.get("entity_b_id", "")
            flags_text = row.get("flags", "")
            nti = row.get("narrow_therapeutic_index", "low")
            flags = set()
            for f_val in flags_text.split("|"):
                f_val = f_val.strip()
                if f_val:
                    flags.add(f_val)
            if nti and nti.strip().lower() == "high":
                flags.add("narrow_therapeutic_index")
            result[eid] = flags
    return result


def load_rules() -> dict:
    path = PROJECT_ROOT / "configs" / "rules.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_report() -> dict:
    path = PROJECT_ROOT / "outputs" / "citation_verification_report.json"
    with open(path) as f:
        return json.load(f)


class TestRulesCoverage:
    """Verify all rules have valid definitions and triggerable entity pairs."""

    def setup_method(self):
        self.rules_data = load_rules()
        self.report = load_report()
        self.a_flags = load_entity_flags_a()
        self.b_flags = load_entity_flags_b()
        self.rules = self.rules_data.get("rules", [])
        self.pf_rules = self.rules_data.get("patient_factor_rules", {})
        self.rules_path = PROJECT_ROOT / "configs" / "rules.yaml"
        self.current_sha = hashlib.sha256(self.rules_path.read_bytes()).hexdigest()

    def test_report_sha256_matches(self):
        """Citation verification report SHA256 must match current rules.yaml."""
        report_sha = self.report.get("rules_yaml_sha256", "")
        assert self.current_sha == report_sha, (
            f"SHA256 mismatch: current={self.current_sha[:16]}... "
            f"report={report_sha[:16]}..."
        )

    def test_report_overall_pass(self):
        """Citation verification must pass in strict mode."""
        assert self.report.get("overall") == "pass", "Report overall != pass"
        assert self.report.get("mode") == "strict-policy-cache-replay", "Report mode != strict policy replay"

    def test_all_rules_defined(self):
        """All 40 rules must be present (14 original + DDInter-expanded + absorption-gated additions)."""
        assert len(self.rules) == 40, f"Expected 40 rules, got {len(self.rules)}"
        rids = [r["id"] for r in self.rules]
        expected = [
            "additive_beta_blockade", "additive_alpha2_cns_depression",
            "additive_anticholinergic_effects", "additive_corticosteroid_iop",
            "additive_nsaid_bleeding", "sympathomimetic_alpha_interaction",
            "qt_prolongation_risk", "pga_antiplatelet_bleeding",
            "cai_diuretic_metabolic_acidosis", "cai_topiramate_acidosis",
            "topical_corticosteroid_cyp3a4_induction",
            "systemic_absorption_high_risk", "systemic_absorption_moderate_risk",
            "p_gp_mediated_absorption",
            "beta_blocker_ccb_additive", "beta_blocker_digoxin_additive",
        ]
        for e in expected:
            assert e in rids, f"Missing rule: {e}"

    def test_all_patient_factor_rules_defined(self):
        """All 3 patient factor rules must be present."""
        assert len(self.pf_rules) == 3, f"Expected 3 PF rules, got {len(self.pf_rules)}"
        for name in ("elderly", "renal_impairment", "polypharmacy"):
            assert name in self.pf_rules, f"Missing PF rule: {name}"

    def test_each_rule_has_citations(self):
        """Every rule must have at least 1 citation."""
        for rule in self.rules:
            cits = rule.get("citations", [])
            assert len(cits) > 0, f"Rule '{rule['id']}' has no citations"

    def test_each_pf_rule_has_citations(self):
        """Every patient factor rule must have at least 1 citation."""
        for name, pf in self.pf_rules.items():
            cits = pf.get("citations", [])
            assert len(cits) > 0, f"PF rule '{name}' has no citations"

    def test_each_rule_has_tiggerable_a_entity(self):
        """Each rule's entity_a_flags must each exist in at least one Entity A record."""
        for rule in self.rules:
            a_flags = set(rule.get("entity_a_flags", []) or [])
            if not a_flags:
                continue
            all_flags_union = set()
            for flags in self.a_flags.values():
                all_flags_union |= flags
            missing = a_flags - all_flags_union
            assert not missing, (
                f"Rule '{rule['id']}' flags {missing} not found in any Entity A record"
            )

    def test_each_rule_has_tiggerable_b_entity(self):
        """Each rule's entity_b_flags must each exist in at least one Entity B record."""
        for rule in self.rules:
            b_flags = set(rule.get("entity_b_flags", []) or [])
            if not b_flags:
                continue
            all_flags_union = set()
            for flags in self.b_flags.values():
                all_flags_union |= flags
            missing = b_flags - all_flags_union
            assert not missing, (
                f"Rule '{rule['id']}' flags {missing} not found in any Entity B record"
            )

    def test_dual_source_verified_citations(self):
        """All DOI/PMID citations in the report must be 'verified' (not 'single_source' or 'retracted')."""
        for rule_entry in self.report.get("rules", []):
            for cit in rule_entry.get("citations", []):
                status = cit.get("status", "")
                assert status in ("verified", "report_ok", "db_ok"), (
                    f"Rule '{rule_entry['id']}' citation '{cit.get('raw','')[:50]}...' "
                    f"has status '{status}' (must be verified/report_ok/db_ok)"
                )

    def test_sha256_blocking_condition(self):
        """The blocking condition must be resolved: SHA256 match + overall pass."""
        report_sha = self.report.get("rules_yaml_sha256", "")
        sha_match = self.current_sha == report_sha
        overall_pass = self.report.get("overall") == "pass"
        strict_mode = self.report.get("mode") == "strict-policy-cache-replay"
        assert sha_match and overall_pass and strict_mode, (
            f"Blocking condition not met: "
            f"SHA256_match={sha_match} overall={self.report.get('overall')} mode={self.report.get('mode')}"
        )
