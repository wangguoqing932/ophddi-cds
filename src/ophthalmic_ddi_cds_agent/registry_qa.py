"""Registry integrity checks and machine-readable reconciliation reports."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "error"


def load_catalog(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_records(records: Iterable[object], side: str, catalog: dict) -> list[Finding]:
    records = list(records)
    findings: list[Finding] = []
    ids = [getattr(item, f"entity_{side.lower()}_id") for item in records]
    names = [getattr(item, "canonical_name") for item in records]
    for value, count in Counter(ids).items():
        if count > 1: findings.append(Finding("duplicate_local_id", f"{side}:{value}"))
    for value, count in Counter(names).items():
        if value and count > 1: findings.append(Finding("duplicate_canonical_name", f"{side}:{value}"))
    allowed_admin = {"topical", "intravitreal", "intraocular", "diagnostic", "surgical"}
    allowed_flags = catalog["flags"]
    for item in records:
        item_id = getattr(item, f"entity_{side.lower()}_id")
        for flag in item.flags:
            spec = allowed_flags.get(flag)
            if not spec: findings.append(Finding("unknown_flag", f"{item_id}:{flag}"))
            elif side not in spec["sides"]: findings.append(Finding("wrong_flag_side", f"{item_id}:{flag}"))
        if side == "A" and item.ophthalmic_administration not in allowed_admin:
            findings.append(Finding("invalid_ophthalmic_administration", item_id))
        if side == "B" and item.route != "systemic": findings.append(Finding("invalid_systemic_route", item_id))
        if not item.provenance: findings.append(Finding("missing_provenance", item_id))
        if not item.canonical_name: findings.append(Finding("missing_canonical_name", item_id))
    return findings


def write_report(path: Path, entities_a: list[object], entities_b: list[object], catalog: dict) -> dict:
    findings = validate_records(entities_a, "A", catalog) + validate_records(entities_b, "B", catalog)
    report = {"status": "pass" if not findings else "fail", "counts": {"entity_a": len(entities_a), "entity_b": len(entities_b)}, "findings": [asdict(item) for item in findings]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
