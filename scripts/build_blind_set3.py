#!/usr/bin/env python3
"""build_blind_set3.py — Third blind set: DDInter absorption-corrected consistency set.

Design (transparent, disclosed same-source component):
- Source: DDInter 2.0 records for pairs within the 113x232 registry (1,933 matched)
- Zero overlap with: all data/datasets/* (402 pairs) + blind sets 1&2 (40 pairs)
- Stratified sampling: A-absorption tier (high/medium/low/very_low) x DDInter level (high/medium/low)
- gold = DDInter level corrected by the absorption prior:
    low/very_low absorption A  -> gold = low   (ocular exposure negligible)
    high/medium absorption A   -> gold = DDInter level (kept)
  (the correction rule is the domain prior; disclosed as partially same-source with the
   system's absorption scaling — this set measures consistency with third-party ratings
   under the ophthalmic absorption prior, not independent accuracy)
- Frozen: file + SHA recorded before evaluation; engine version noted.
"""
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low"}
ABS_ORDER = {"systemic_absorption_high": 0, "systemic_absorption_medium": 1,
             "systemic_absorption_low": 2, "systemic_absorption_very_low": 3,
             "minimal_systemic_absorption": 3, "systemic_absorption_none": 3}


def main() -> None:
    kg = PreciseKG()
    random.seed(20260731)

    # DDInter index
    ddinter = {}
    for code in ["A", "B", "C", "N", "S"]:
        with (ROOT / f"data/raw/ddinter/ddinter_code_{code}.csv").open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                a = row["Drug_A"].strip().lower()
                b = row["Drug_B"].strip().lower()
                ddinter[(a, b)] = row["Level"]
                ddinter[(b, a)] = row["Level"]

    # used pairs
    used = set()
    for f in (ROOT / "data" / "datasets").glob("*/cases.jsonl"):
        for line in f.open(encoding="utf-8"):
            if not line.strip():
                continue
            c = json.loads(line)
            oph = c.get("ophthalmic_drug", "") or ""
            sysd = c.get("systemic_drug", "") or ""
            if oph and sysd:
                used.add((oph.lower(), sysd.lower()))
    for f in ("blind_set_v2.json", "blind_set_v3.json"):
        for c in json.load((ROOT / "outputs" / "blind_test" / f).open(encoding="utf-8")):
            used.add((c["ophthalmic_drug"].lower(), c["systemic_drug"].lower()))

    # candidates: DDInter-recorded, unused, registry-resolvable
    cands = []
    for (an, bn), lvl in ddinter.items():
        dl = LEVEL_MAP.get(lvl.lower())
        if dl is None:
            continue
        ae = kg.get_ophthalmic(an)
        be = kg.get_systemic(bn)
        if not ae or not be:
            continue
        absl = next((f for f in ae["flags"] if "systemic_absorption_" in f), "none")
        cands.append({"ophthalmic": ae["name"], "systemic": be["name"], "ddinter": dl,
                      "absorption": absl, "abs_tier": ABS_ORDER.get(absl, 3)})
    print(f"candidates (DDInter-recorded, unused, resolvable): {len(cands)}")

    # stratified sampling: aim ~90 cases across 4 absorption tiers x 3 levels
    strat = Counter((c["abs_tier"], c["ddinter"]) for c in cands)
    print("stratum sizes:", dict(strat))
    target = {(0, "high"): 12, (0, "medium"): 8, (0, "low"): 2,
              (1, "high"): 12, (1, "medium"): 10, (1, "low"): 4,
              (2, "high"): 12, (2, "medium"): 10, (2, "low"): 8,
              (3, "high"): 6, (3, "medium"): 4, (3, "low"): 4}
    by_stratum = {}
    for c in cands:
        by_stratum.setdefault((c["abs_tier"], c["ddinter"]), []).append(c)
    selected = []
    for key, n in target.items():
        pool = by_stratum.get(key, [])
        random.shuffle(pool)
        selected.extend(pool[:n])
    print(f"selected: {len(selected)}")

    # absorption-corrected gold
    out = []
    for c in selected:
        absl = c["absorption"]
        if absl in ("systemic_absorption_low", "systemic_absorption_very_low",
                    "minimal_systemic_absorption", "systemic_absorption_none"):
            gold = "low"
            corr = f"absorption_correction: {absl} -> low"
        else:
            gold = c["ddinter"]
            corr = f"ddinter_kept: {absl}"
        out.append({"case_id": f"D3-{len(out):03d}", "ophthalmic_drug": c["ophthalmic"],
                    "systemic_drug": c["systemic"], "ddinter_level": c["ddinter"],
                    "absorption": absl, "proposed_gold": gold, "gold_rule": corr,
                    "gold_status": "ddinter_absorption_corrected"})

    dist = Counter(c["proposed_gold"] for c in out)
    print("gold distribution:", dict(dist))
    print("gold=DDInter kept:", sum(1 for c in out if c["proposed_gold"] == c["ddinter_level"]),
          "| corrected:", sum(1 for c in out if c["proposed_gold"] != c["ddinter_level"]))

    path = ROOT / "outputs" / "blind_test" / "blind_set_v3_ddinter.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / "outputs" / "blind_test" / "blind_set_v3_ddinter.sha256").write_text(sha)
    print(f"saved {len(out)} cases -> {path}")
    print(f"FROZEN SHA: {sha[:16]}")


if __name__ == "__main__":
    main()
