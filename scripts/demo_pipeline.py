#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_pipeline.py — end-to-end smoke test of the deterministic cascade.

Runs the production screening path (full_system) over the bundled mock cases and
checks that every case reproduces the risk level recorded at release. The
deterministic path makes no LLM calls and needs no API key or network access, so a
reviewer can verify that the pipeline executes and behaves as documented.

Usage:
    python scripts/demo_pipeline.py            # run all mock cases
    python scripts/demo_pipeline.py --verbose  # also print the decision trace
    python scripts/demo_pipeline.py --case MOCK01

Exit code 0 if every case matches its expected level, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MOCK_CASES = ROOT / "data" / "mock" / "mock_cases.jsonl"


def load_cases(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true", help="print the full decision trace per case")
    ap.add_argument("--case", help="run a single case by its id")
    args = ap.parse_args()

    from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

    kg = PreciseKG()
    print(f"Registry loaded: {len(kg.a_registry)} ophthalmic agents, "
          f"{len(kg.b_registry)} systemic agents, "
          f"{len(kg.rules.get('rules', []))} mechanism rules")
    print(f"Absorption scaling: {kg._matrix_scale}")
    print()

    cases = load_cases(MOCK_CASES)
    if args.case:
        cases = [c for c in cases if c["case_id"] == args.case]
        if not cases:
            print(f"no mock case with id {args.case!r}")
            return 1

    header = f"{'case':8s} {'ophthalmic':16s} {'systemic':14s} {'expected':9s} {'got':9s} {'path':13s} result"
    print(header)
    print("-" * len(header))

    failures = []
    for c in cases:
        level, rule_ids, info = kg.deterministic_level_v2(c["ophthalmic_drug"], c["systemic_drug"])
        ok = level == c["expected_level"]
        if not ok:
            failures.append(c["case_id"])
        print(f"{c['case_id']:8s} {c['ophthalmic_drug']:16s} {c['systemic_drug']:14s} "
              f"{str(c['expected_level']):9s} {str(level):9s} {str(info.get('path')):13s} "
              f"{'PASS' if ok else 'FAIL'}")

        if args.verbose:
            print(f"    matched rules : {rule_ids or '(none)'}")
            for key in ("reason", "detail", "matrix_cell", "absorption"):
                if info.get(key):
                    print(f"    {key:14s}: {info[key]}")

    print()
    print(f"{len(cases) - len(failures)}/{len(cases)} mock cases reproduced their expected level")

    # Fail-safe behaviour: an out-of-coverage medication must not receive a score.
    print()
    print("Fail-safe check (out-of-coverage medication):")
    level, _, info = kg.deterministic_level_v2("NonexistentDrug", "Aspirin")
    print(f"  'NonexistentDrug' + 'Aspirin' -> level={level!r}, path={info.get('path')!r}")
    if level is None and info.get("path") == "unknown_drug":
        print("  PASS: no risk grade is assigned to an unknown drug")
    else:
        print("  FAIL: an unknown drug did not take the documented unknown-drug path")
        failures.append("fail-safe")

    if failures:
        print(f"\nFAILED: {failures}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
