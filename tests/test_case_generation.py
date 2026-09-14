from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generate_cases import case_metadata, generate_cases


def test_generated_cases_are_reproducible_and_rule_derived() -> None:
    root = Path(__file__).resolve().parents[1]
    first = generate_cases(root=root, seed=17, max_cases=12)
    second = generate_cases(root=root, seed=17, max_cases=12)
    assert first == second
    assert len(first) == 12
    assert {case["gold_risk"] for case in first} >= {"high", "medium", "low", "unknown"}
    assert all(case["generation_source"] == "rule_engine" for case in first)
    assert all(case["case_id"] == f"{case['a_id']}|{case['b_id']}" for case in first)


def test_case_metadata_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = generate_cases(root=root, seed=3, max_cases=8)
    assert case_metadata(cases, seed=3, max_cases=8) == case_metadata(cases, seed=3, max_cases=8)
