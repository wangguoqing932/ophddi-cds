"""Generate deterministic, rule-derived evaluation cases without network access."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.risk_rules import RuleEngine
from ophthalmic_ddi_cds_agent.schemas import EntityA, EntityB


def _split(value: str | None) -> list[str]:
    return [item for item in (value or "").split("|") if item]


def load_entities(root: Path = ROOT) -> tuple[list[EntityA], list[EntityB]]:
    """Load only the local seed registries required to construct cases."""
    with (root / "data" / "seed" / "entities_a.csv").open(encoding="utf-8", newline="") as handle:
        entities_a = [
            EntityA(
                entity_a_id=row["topical_ophthalmic_medications_id"], primary_name=row["primary_name"],
                canonical_name=row["primary_name"], aliases=_split(row.get("aliases")), category=row["category"],
                active_mechanisms=_split(row.get("active_mechanisms")), flags=_split(row.get("flags")),
                evidence_sources=_split(row.get("evidence_sources")),
            )
            for row in csv.DictReader(handle)
        ]
    with (root / "data" / "seed" / "entities_b.csv").open(encoding="utf-8", newline="") as handle:
        entities_b = [
            EntityB(
                entity_b_id=row["entity_b_id"], generic_name=row["generic_name"], canonical_name=row["generic_name"],
                aliases=_split(row.get("aliases")), drug_class=row["drug_class"], flags=_split(row.get("flags")),
            )
            for row in csv.DictReader(handle)
        ]
    return entities_a, entities_b


def generate_cases(*, root: Path = ROOT, seed: int = 0, max_cases: int | None = None, include_unknown: bool = True) -> list[dict]:
    """Create reproducible positive rule cases plus optional unmatched negative cases."""
    entities_a, entities_b = load_entities(root)
    engine = RuleEngine(root / "configs" / "rules.yaml")
    rng = random.Random(seed)
    candidates: list[dict] = []
    for entity_a in sorted(entities_a, key=lambda item: item.entity_a_id):
        for entity_b in sorted(entities_b, key=lambda item: item.entity_b_id):
            assessment = engine.evaluate(entity_a, entity_b)
            if assessment.risk_level.value == "unknown" and not include_unknown:
                continue
            candidates.append({
                "case_id": f"{entity_a.entity_a_id}|{entity_b.entity_b_id}",
                "a_id": entity_a.entity_a_id, "a_name": entity_a.primary_name,
                "b_id": entity_b.entity_b_id, "b_name": entity_b.generic_name,
                "patient_factors": [], "gold_risk": assessment.risk_level.value,
                "rule_ids": [signal.rule_id for signal in assessment.signals],
                "generation_source": "rule_engine", "rules_yaml_sha256": engine.sha256,
            })
    # Preserve class coverage while selecting a reproducible, randomized subset.
    by_level: dict[str, list[dict]] = {level: [] for level in ("high", "medium", "low", "unknown")}
    for case in candidates:
        by_level[case["gold_risk"]].append(case)
    for cases in by_level.values():
        rng.shuffle(cases)
    selected = [cases.pop() for cases in by_level.values() if cases]
    remainder = [case for cases in by_level.values() for case in cases]
    rng.shuffle(remainder)
    if max_cases is not None:
        selected = selected[:max_cases]
        selected.extend(remainder[: max(0, max_cases - len(selected))])
    else:
        selected.extend(remainder)
    return sorted(selected, key=lambda case: case["case_id"])


def case_metadata(cases: list[dict], *, seed: int, max_cases: int | None) -> dict:
    payload = "\n".join(json.dumps(case, sort_keys=True) for case in cases).encode()
    return {
        "generator": "rule_engine", "seed": seed, "max_cases": max_cases,
        "case_count": len(cases), "sha256": hashlib.sha256(payload).hexdigest(),
        "offline": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Destination case JSONL")
    parser.add_argument("--metadata-output", type=Path, help="Destination generation metadata JSON")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--exclude-unknown", action="store_true")
    args = parser.parse_args()
    cases = generate_cases(seed=args.seed, max_cases=args.max_cases, include_unknown=not args.exclude_unknown)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(case, sort_keys=True) + "\n" for case in cases), encoding="utf-8")
    metadata = case_metadata(cases, seed=args.seed, max_cases=args.max_cases)
    if args.metadata_output:
        args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
        args.metadata_output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
