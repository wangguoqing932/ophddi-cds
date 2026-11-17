# -*- coding: utf-8 -*-
"""audit_ddinter_denominator.py — regenerate the registry-scale denominator.

The manuscript's 1,933-pair comparison excludes DDInter records whose Level is
`Unknown`. This script computes, from the seed registries and the raw DDInter
tables, the number of registry-matched pairs with any DDInter record, how many
are `Unknown`, and how many have a graded severity (Major/Moderate/Minor).
"""
from __future__ import annotations

import csv
import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    levels: dict[tuple[str, str], str] = {}
    for path in glob.glob(str(ROOT / "data/raw/ddinter/ddinter_code_*.csv")):
        with open(path, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                a = row["Drug_A"].strip().lower()
                b = row["Drug_B"].strip().lower()
                level = row["Level"].strip().lower()
                levels[(a, b)] = level
                levels[(b, a)] = level

    a_names = [r["primary_name"].strip().lower() for r in
               csv.DictReader((ROOT / "data/seed/entities_a.csv").open(encoding="utf-8-sig"))]
    b_names = [r["generic_name"].strip().lower() for r in
               csv.DictReader((ROOT / "data/seed/entities_b.csv").open(encoding="utf-8-sig"))]

    counts = Counter()
    graded = Counter()
    for a in a_names:
        for b in b_names:
            level = levels.get((a, b))
            if level is None:
                continue
            counts["matched"] += 1
            if level == "unknown":
                counts["unknown"] += 1
            elif level in ("major", "moderate", "minor"):
                counts["graded"] += 1
                graded[level] += 1
            else:
                counts["other"] += 1

    result = {
        "registry_a": len(a_names),
        "registry_b": len(b_names),
        "grid": len(a_names) * len(b_names),
        "matched_pairs": counts["matched"],
        "unknown_pairs": counts["unknown"],
        "graded_pairs": counts["graded"],
        "graded_levels": dict(graded),
        "other_pairs": counts["other"],
    }
    out = ROOT / "outputs/audits/ddinter_denominator_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
