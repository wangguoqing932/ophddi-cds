"""The default-low path must be distinguishable from an assessed low risk."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402


def test_default_low_is_flagged_unassessed():
    kg = PreciseKG()
    level, _, info = kg.deterministic_level_v2("Timolol", "Warfarin")
    assert level == "low"
    assert info["path"] == "default_low"
    assert info["assessment_status"] == "unassessed"


def test_defined_none_cell_is_assessed_low():
    kg = PreciseKG()
    level, _, info = kg.deterministic_level_v2("Timolol", "Sildenafil")
    assert level == "low"
    assert info["path"] == "matrix"
    assert info["assessment_status"] == "assessed"


def test_absorption_gated_rule_skips_low_tier():
    kg = PreciseKG()
    level, rules, info = kg.deterministic_level_v2("Bromfenac", "Enalapril")
    assert "nsaid_antihypertensive_antagonism" not in rules


def test_assessed_paths_are_flagged_assessed():
    kg = PreciseKG()
    level, rules, info = kg.deterministic_level_v2("Timolol", "Atenolol")
    assert level == "high"
    assert rules
    assert info["assessment_status"] == "assessed"


def test_service_propagates_unassessed_status():
    try:
        from ophthalmic_ddi_cds_agent.safety_agent import SafetyAgent, SafetyAgentConfig
    except ImportError:
        import pytest
        pytest.skip("SafetyAgent requires Python 3.11 (enum.StrEnum)")
    agent = SafetyAgent(SafetyAgentConfig(ROOT))
    report = agent.assess("Timolol", "Warfarin")
    assert report.risk_assessment.assessment_status == "unassessed"
    assert "not evidence of safety" in report.risk_assessment.assessment_note
