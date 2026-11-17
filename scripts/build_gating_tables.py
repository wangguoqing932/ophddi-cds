# -*- coding: utf-8 -*-
"""build_gating_tables.py — gated (primary) vs ungated (sensitivity) comparison.

Writes Table S19 and refreshes the machine-readable gating experiment JSON.
"""
from __future__ import annotations

import copy
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low"}
LOW = {"systemic_absorption_low", "systemic_absorption_very_low",
       "minimal_systemic_absorption", "systemic_absorption_none"}
SEV = {"high": 3, "medium": 2, "low": 1}


def l1_metrics(kg):
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    rows = [json.loads(l) for l in (ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl").open(encoding="utf-8")
            if json.loads(l)["method"] == "full_system"]
    out = {}
    for label in ("frozen", "corrected"):
        y, p = [], []
        for r in rows:
            g = (prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"]) if label == "frozen" else prov[r["case_id"]]["gold_current"]
            y.append(g)
            p.append(kg.deterministic_level_v2(r["a_name"], r["b_name"])[0])
        n = len(y)
        ok = sum(a == b for a, b in zip(y, p))
        hi = [i for i, g in enumerate(y) if g == "high"]
        tp = sum(p[i] == "high" for i in hi)
        out[label] = {"correct": ok, "n": n, "agreement": round(ok / n, 4),
                      "sensitivity": round(tp / len(hi), 4), "tp": tp, "high_n": len(hi)}
    return out


def grid_metrics(kg):
    dd = {}
    for code in ["A", "B", "C", "N", "S"]:
        for row in csv.DictReader((ROOT / f"data/raw/ddinter/ddinter_code_{code}.csv").open(encoding="utf-8-sig")):
            a, b = row["Drug_A"].strip().lower(), row["Drug_B"].strip().lower()
            dd[(a, b)] = row["Level"]
            dd[(b, a)] = row["Level"]
    n = down = up = lowdown = 0
    for an in kg.a_registry:
        for bn in kg.b_registry:
            dl = LEVEL_MAP.get((dd.get((an.lower(), bn.lower())) or "").lower())
            if not dl:
                continue
            lvl = kg.deterministic_level_v2(an, bn)[0]
            n += 1
            if SEV[lvl] < SEV[dl]:
                down += 1
                tier = next((f for f in kg.a_registry[an]["flags"]
                             if f.startswith("systemic_absorption_") or f == "minimal_systemic_absorption"), "none")
                if tier in LOW:
                    lowdown += 1
            elif SEV[lvl] > SEV[dl]:
                up += 1
    return {"n": n, "downgrade": down, "upgrade": up,
            "downgrade_share": round(down / n, 4),
            "low_absorption_downgrades": lowdown,
            "share_of_downgrades": round(lowdown / down, 4)}


def ungated(kg):
    kg2 = copy.deepcopy(kg)
    for rule in kg2.rules.get("rules", []):
        rule.pop("absorption_gated", None)
    return kg2


def main() -> None:
    kg = PreciseKG()
    kg_u = ungated(kg)
    data = {"gated": {"l1": l1_metrics(kg), "grid": grid_metrics(kg)},
            "ungated": {"l1": l1_metrics(kg_u), "grid": grid_metrics(kg_u)}}
    dest = ROOT / "outputs/recomputed/rule_gating_experiment.json"
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out = ["**Supplementary Table S19. Gated primary analysis versus ungated sensitivity analysis.**", "",
           "| Analysis | L1 frozen | L1 corrected | 1,933 downgrade | Low-tier share of downgrades | Upgrades |",
           "|---|---|---|---|---|---|"]
    for name, key in [("Gated (primary)", "gated"), ("Ungated (sensitivity)", "ungated")]:
        e = data[key]
        out.append(f"| {name} | {e['l1']['frozen']['correct']}/118 ({e['l1']['frozen']['agreement']:.3f}); "
                   f"sens {e['l1']['frozen']['sensitivity']:.3f} | "
                   f"{e['l1']['corrected']['correct']}/118 ({e['l1']['corrected']['agreement']:.3f}); "
                   f"sens {e['l1']['corrected']['sensitivity']:.3f} | "
                   f"{e['grid']['downgrade']} ({e['grid']['downgrade_share']:.3f}) | "
                   f"{e['grid']['low_absorption_downgrades']} ({e['grid']['share_of_downgrades']:.3f}) | "
                   f"{e['grid']['upgrade']} |")
    out += ["", "The gate applies to `nsaid_antihypertensive_antagonism`: it cannot fire when the ophthalmic "
                "tier is low or lower. The ungated analysis restores the rule for those tiers. The lower agreement "
                "under the gate is expected because 47 of the 58 guideline labels encode the rule's own severity; "
                "the gate is retained as the primary behaviour because it is consistent with the absorption model.", ""]
    (ROOT / "outputs/tables/table_s19_gating_sensitivity.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("gating tables written", data["gated"]["l1"]["frozen"], data["ungated"]["l1"]["frozen"])


if __name__ == "__main__":
    main()
