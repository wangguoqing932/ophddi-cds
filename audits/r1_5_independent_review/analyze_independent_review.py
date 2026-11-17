# -*- coding: utf-8 -*-
"""analyze_independent_review.py — score the blinded R1-5 adjudication.

Reads the reviewer-returned `cases_blinded.csv` and the hidden `author_key.csv`,
then reports exact agreement, Cohen's kappa and the confusion matrix for the
three author classes. `supported_upgrade` and `uncertain` are outside the
three-class key and are reported separately.

Usage:
  python outputs/audits/r1_5_independent_review/analyze_independent_review.py
  python ... --reviewed path/to/filled.csv --out path/to/results
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALID = {
    "route_consistent_downgrade",
    "unsupported_undergrading",
    "system_overgrading",
    "supported_upgrade",
    "uncertain",
}
KEY_CLASSES = ["route_consistent_downgrade", "unsupported_undergrading", "system_overgrading"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in KEY_CLASSES) / (n * n)
    return (po - pe) / (1 - pe) if pe != 1 else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviewed", default=str(HERE / "cases_blinded.csv"))
    ap.add_argument("--key", default=str(HERE / "author_key.csv"))
    ap.add_argument("--out", default=str(HERE / "independent_review_results"))
    args = ap.parse_args()

    reviewed = {r["case_id"]: r for r in read_csv(Path(args.reviewed))}
    key = {r["case_id"]: r["author_class"] for r in read_csv(Path(args.key))}
    if set(reviewed) != set(key):
        raise SystemExit(f"case sets differ: reviewed={len(reviewed)} key={len(key)}")

    invalid = {c: r.get("your_class", "") for c, r in reviewed.items()
               if r.get("your_class", "").strip() not in VALID}
    if invalid:
        raise SystemExit("missing/invalid your_class for: " + ", ".join(sorted(invalid)))

    pairs = [(key[c], reviewed[c]["your_class"].strip()) for c in sorted(key)
             if reviewed[c]["your_class"].strip() in KEY_CLASSES]
    n = len(pairs)
    agree = sum(a == b for a, b in pairs)
    exact = agree / n if n else float("nan")
    k = kappa(pairs)

    matrix = defaultdict(Counter)
    for a, b in pairs:
        matrix[a][b] += 1
    off_key = {c: reviewed[c]["your_class"].strip() for c in sorted(key)
               if reviewed[c]["your_class"].strip() not in KEY_CLASSES}

    result = {
        "n_cases": len(key),
        "n_scored_three_class": n,
        "n_exact": agree,
        "exact_agreement": round(exact, 4),
        "cohen_kappa": round(k, 4) if k == k else None,
        "confusion_author_rows_reviewer_cols": {a: dict(matrix[a]) for a in KEY_CLASSES},
        "outside_three_class_key": off_key,
        "reviewer_class_counts": dict(Counter(reviewed[c]["your_class"].strip() for c in reviewed)),
    }
    out = Path(args.out)
    out.with_suffix(".json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lines = [
        "# R1-5 independent adjudication — results",
        "",
        f"- Cases returned: **{result['n_cases']}**",
        f"- Exact agreement over all returned cases: **{agree}/{result['n_cases']} = {agree/result['n_cases']:.3f}** "
        "(counting supported_upgrade as a disagreement with the author over-grade)",
        f"- Scored on the three-class key: **{n}**",
        f"- Exact agreement on the three-class key: **{agree}/{n} = {exact:.3f}**",
        f"- Cohen's kappa: **{k:.3f}**" if k == k else "- Cohen's kappa: not estimable",
        "",
        "## Confusion matrix (author rows × reviewer columns)",
        "",
        "| author \\ reviewer | route-consistent | unsupported | over-grade |",
        "|---|---:|---:|---:|",
    ]
    for a in KEY_CLASSES:
        lines.append(f"| {a} | {matrix[a]['route_consistent_downgrade']} | "
                     f"{matrix[a]['unsupported_undergrading']} | {matrix[a]['system_overgrading']} |")
    lines += ["", "## Cases outside the three-class key", ""]
    if off_key:
        for c, v in off_key.items():
            lines.append(f"- {c}: {v}")
    else:
        lines.append("- None")
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=1))
    print(f"wrote {out.with_suffix('.json')} and {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
