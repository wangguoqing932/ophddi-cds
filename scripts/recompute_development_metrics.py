# -*- coding: utf-8 -*-
"""recompute_development_metrics.py — gated vs ungated development-gate metrics.

Reads the deposited case files and the current engine, so the numbers reported in
Section 3.2 can be regenerated without model access.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402


def metrics(kg: PreciseKG, path: Path) -> dict:
    a_id = {v["id"]: v["name"] for v in kg.a_registry.values()}
    b_id = {v["id"]: v["name"] for v in kg.b_registry.values()}
    rows = [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]
    y, pred, missing = [], [], []
    for r in rows:
        a = r.get("ophthalmic") or a_id.get(r.get("entity_a_id"))
        b = r.get("systemic") or b_id.get(r.get("entity_b_id"))
        if not a or not b:
            missing.append(r["case_id"])
            continue
        level = kg.deterministic_level_v2(a, b)[0]
        y.append(r["gold_risk_level"])
        pred.append(level)
    n = len(y)
    correct = sum(a == b for a, b in zip(y, pred))
    high = [i for i, g in enumerate(y) if g == "high"]
    non = [i for i, g in enumerate(y) if g != "high"]
    tp = sum(pred[i] == "high" for i in high)
    tn = sum(pred[i] != "high" for i in non)
    return {
        "n": n,
        "high_n": len(high),
        "exact_agreement": round(correct / n, 4),
        "sensitivity_high": round(tp / len(high), 4),
        "specificity_high": round(tn / len(non), 4),
        "tp": tp,
        "missing": missing,
    }


def main() -> None:
    kg = PreciseKG()
    ungated = copy.deepcopy(kg)
    for rule in ungated.rules.get("rules", []):
        rule.pop("absorption_gated", None)

    sets = {
        "internal_validation_78": ROOT / "data/datasets/internal_validation/cases.jsonl",
        "dev_ddinter_200": ROOT / "data/datasets/dev-ddinter/cases.jsonl",
        "external_co_mention_70": ROOT / "data/datasets/external_validation/cases.jsonl",
    }
    out = {"gated": {}, "ungated": {}}
    for name, path in sets.items():
        out["gated"][name] = metrics(kg, path)
        out["ungated"][name] = metrics(ungated, path)

    dest = ROOT / "outputs/recomputed/development_gate_metrics.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key in ("gated", "ungated"):
        print(key, json.dumps(out[key], ensure_ascii=False))


if __name__ == "__main__":
    main()
