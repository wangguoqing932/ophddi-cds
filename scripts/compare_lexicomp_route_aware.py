# -*- coding: utf-8 -*-
"""compare_lexicomp_route_aware.py — reproduce the Lexicomp route-aware comparison.

Reads the local Lexicomp extraction (proprietary ratings, not for redistribution)
and the case-level DDInter/RA-DDInter/cascade table (Supplementary Table S18),
then computes agreement, high-risk sensitivity/specificity and kappa under the
pre-specified 5-to-3-level mapping and two sensitivity analyses.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "outputs" / "audits" / "lexicomp_route_aware_raw.json"
S18 = ROOT / "outputs" / "tables" / "table_s18_route_aware_cases.md"
OUT_JSON = ROOT / "outputs" / "audits" / "lexicomp_route_aware.json"
OUT_MD = ROOT / "outputs" / "audits" / "lexicomp_route_aware_report.md"

ORDER = ["high", "medium", "low"]
PRIMARY = {"X": "high", "D": "high", "C": "medium", "B": "low", None: "low"}
C_TO_HIGH = {"X": "high", "D": "high", "C": "high", "B": "low", None: "low"}


def parse_s18() -> dict[str, dict[str, str]]:
    rows = {}
    for line in S18.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or "case" in line.split("|")[1]:
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 7:
            continue
        case, oph, sys, ddinter, ra, cascade, reference = parts[:7]
        rows[case] = {
            "ophthalmic": oph,
            "systemic": sys,
            "ddinter": ddinter,
            "ra_ddinter": ra,
            "cascade": cascade,
            "reference": reference,
        }
    return rows


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def kappa(a: list[str], b: list[str], labels: list[str]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def confusion(ref: list[str], pred: list[str]) -> dict[str, dict[str, int]]:
    return {r: {p: sum(1 for x, y in zip(ref, pred) if x == r and y == p) for p in ORDER} for r in ORDER}


def three_level(ref: list[str], pred: list[str]) -> dict:
    cm = confusion(ref, pred)
    n = len(ref)
    exact = sum(cm[r][r] for r in ORDER)
    tp = cm["high"]["high"]
    fn = sum(cm["high"][p] for p in ORDER if p != "high")
    fp = sum(cm[r]["high"] for r in ORDER if r != "high")
    tn = n - tp - fn - fp
    lo, hi = wilson(exact, n)
    return {
        "n": n,
        "confusion": cm,
        "exact": exact,
        "exact_rate": exact / n,
        "exact_wilson": [lo, hi],
        "high_sensitivity": tp / (tp + fn) if tp + fn else float("nan"),
        "high_sensitivity_n": [tp, tp + fn],
        "high_specificity": tn / (tn + fp) if tn + fp else float("nan"),
        "high_specificity_n": [tn, tn + fp],
        "kappa": kappa(ref, pred, ORDER),
    }


def binary_actionable(ref: list[str], action: list[bool]) -> dict:
    n = len(ref)
    ref_nonlow = [r in ("high", "medium") for r in ref]
    tp = sum(a and b for a, b in zip(ref_nonlow, action))
    fn = sum(a and (not b) for a, b in zip(ref_nonlow, action))
    fp = sum((not a) and b for a, b in zip(ref_nonlow, action))
    tn = sum((not a) and (not b) for a, b in zip(ref_nonlow, action))
    correct = tp + tn
    lo, hi = wilson(correct, n)
    return {
        "n": n,
        "actionable": sum(action),
        "reference_nonlow": sum(ref_nonlow),
        "sensitivity": tp / (tp + fn) if tp + fn else float("nan"),
        "sensitivity_n": [tp, tp + fn],
        "specificity": tn / (tn + fp) if tn + fp else float("nan"),
        "specificity_n": [tn, tn + fp],
        "exact": correct,
        "exact_rate": correct / n,
        "exact_wilson": [lo, hi],
        "kappa": kappa([str(x) for x in ref_nonlow], [str(x) for x in action], ["True", "False"]),
    }


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    s18 = parse_s18()
    cases = raw["cases"]
    missing = [c["case"] for c in cases if c["case"] not in s18]
    if missing:
        raise SystemExit(f"cases missing from S18: {missing}")
    if len(cases) != len(s18):
        raise SystemExit(f"case-count mismatch: lexicomp={len(cases)} s18={len(s18)}")

    rows = []
    for c in cases:
        ref = s18[c["case"]]
        rows.append({
            **c,
            "reference": ref["reference"],
            "cascade": ref["cascade"],
            "ddinter": ref["ddinter"],
            "ra_ddinter": ref["ra_ddinter"],
            "lexicomp_primary": PRIMARY[c["risk"]],
            "lexicomp_c_to_high": C_TO_HIGH[c["risk"]],
            "lexicomp_actionable": c["risk"] in ("C", "D", "X"),
        })

    ref = [r["reference"] for r in rows]
    prim = [r["lexicomp_primary"] for r in rows]
    c2h = [r["lexicomp_c_to_high"] for r in rows]
    act = [r["lexicomp_actionable"] for r in rows]
    cascade = [r["cascade"] for r in rows]

    all_primary = three_level(ref, prim)
    all_c2h = three_level(ref, c2h)
    all_binary = binary_actionable(ref, act)
    vs_cascade = three_level(cascade, prim)

    specific = [r for r in rows if r["ophthalmic_specific"]]
    spec_ref = [r["reference"] for r in specific]
    spec_prim = [r["lexicomp_primary"] for r in specific]
    spec_c2h = [r["lexicomp_c_to_high"] for r in specific]
    spec_binary = binary_actionable(spec_ref, [r["lexicomp_actionable"] for r in specific])

    dist = {k: sum(1 for r in rows if r["risk"] == k) for k in ["X", "D", "C", "B", None]}
    dist_specific = {k: sum(1 for r in specific if r["risk"] == k) for k in ["X", "D", "C", "B", None]}

    result = {
        "resource": raw["resource"],
        "url": raw["url"],
        "version": raw["version"],
        "accessed": raw["accessed"],
        "n": len(rows),
        "ophthalmic_specific_n": len(specific),
        "generic_entry_n": len(rows) - len(specific),
        "risk_distribution": {("none" if k is None else k): v for k, v in dist.items()},
        "risk_distribution_ophthalmic_specific": {("none" if k is None else k): v for k, v in dist_specific.items()},
        "primary_mapping": "X/D -> high; C -> medium; B/A/no interaction -> low",
        "all_42_primary": all_primary,
        "all_42_c_to_high": all_c2h,
        "all_42_binary_actionable": all_binary,
        "cascade_vs_lexicomp_primary": vs_cascade,
        "ophthalmic_specific_35_primary": three_level(spec_ref, spec_prim),
        "ophthalmic_specific_35_c_to_high": three_level(spec_ref, spec_c2h),
        "ophthalmic_specific_35_binary": spec_binary,
        "route_comparison": raw["route_comparison"],
        "reference_distribution": {k: ref.count(k) for k in ORDER},
        "cascade_distribution": {k: cascade.count(k) for k in ORDER},
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Markdown report
    def fmt_pct(x: float) -> str:
        return f"{x * 100:.1f}%"

    def cell(cm, r, p):
        return cm[r][p]

    lines = [
        "# Lexicomp route-aware comparison (42 L1 cases)",
        "",
        f"**Resource:** {raw['resource']}  ",
        f"**Version:** {raw['version']}  ",
        f"**URL:** {raw['url']}  ",
        f"**Accessed:** {raw['accessed']}",
        "",
        "## 1. Coverage and rating distribution",
        "",
        f"- Cases: **{len(rows)}**; ophthalmic-specific Lexicomp entry: **{len(specific)}**; generic entry only: **{len(rows) - len(specific)}** (apraclonidine, bromfenac, voriconazole).",
        f"- Lexicomp ratings: " + ", ".join(f"**{('none' if k is None else k)}** {v}" for k, v in dist.items()) + ".",
        f"- Reference labels: " + ", ".join(f"**{k}** {ref.count(k)}" for k in ORDER) + ".",
        f"- Cascade labels: " + ", ".join(f"**{k}** {cascade.count(k)}" for k in ORDER) + ".",
        "",
        "## 2. Five-to-three-level mapping",
        "",
        "Primary mapping: **X/D → high; C → medium; B/A/no interaction → low**. This follows the Lexicomp definitions (X avoid, D consider modification, C monitor, B no action, A no known interaction) and the manuscript's grade definitions. Because C is a broad 'monitor' category that can include severe mechanisms, a sensitivity analysis maps **C → high**.",
        "",
        "### 2.1 Primary mapping, all 42 cases",
        "",
        "| Reference \\ Lexicomp | high | medium | low |",
        "|---|---:|---:|---:|",
    ]
    for r in ORDER:
        lines.append(f"| {r} | {cell(all_primary['confusion'], r, 'high')} | {cell(all_primary['confusion'], r, 'medium')} | {cell(all_primary['confusion'], r, 'low')} |")
    lines += [
        "",
        f"- Exact agreement: **{all_primary['exact']}/{all_primary['n']} ({all_primary['exact_rate']:.3f}; 95% CI {all_primary['exact_wilson'][0]:.3f}–{all_primary['exact_wilson'][1]:.3f})**; κ **{all_primary['kappa']:.3f}**.",
        f"- High-risk sensitivity: **{all_primary['high_sensitivity_n'][0]}/{all_primary['high_sensitivity_n'][1]} ({all_primary['high_sensitivity']:.3f})**; specificity **{all_primary['high_specificity_n'][0]}/{all_primary['high_specificity_n'][1]} ({all_primary['high_specificity']:.3f})**.",
        "",
        "### 2.2 Sensitivity mapping (C → high), all 42 cases",
        "",
        f"- Exact agreement: **{all_c2h['exact']}/{all_c2h['n']} ({all_c2h['exact_rate']:.3f})**; κ **{all_c2h['kappa']:.3f}**.",
        f"- High-risk sensitivity: **{all_c2h['high_sensitivity_n'][0]}/{all_c2h['high_sensitivity_n'][1]} ({all_c2h['high_sensitivity']:.3f})**; specificity **{all_c2h['high_specificity_n'][0]}/{all_c2h['high_specificity_n'][1]} ({all_c2h['high_specificity']:.3f})**.",
        "",
        "### 2.3 Binary 'any actionable interaction' (C/D/X vs A/B/no interaction)",
        "",
        f"- Lexicomp actionable: **{all_binary['actionable']}/42**; reference non-low: **{all_binary['reference_nonlow']}/42**.",
        f"- Sensitivity for non-low: **{all_binary['sensitivity_n'][0]}/{all_binary['sensitivity_n'][1]} ({all_binary['sensitivity']:.3f})**; specificity **{all_binary['specificity_n'][0]}/{all_binary['specificity_n'][1]} ({all_binary['specificity']:.3f})**.",
        f"- Exact: **{all_binary['exact']}/42 ({all_binary['exact_rate']:.3f})**; κ **{all_binary['kappa']:.3f}**.",
        "",
        "### 2.4 Ophthalmic-specific entries only (n = 35)",
        "",
        f"- Exact agreement under the primary mapping: **{result['ophthalmic_specific_35_primary']['exact']}/35 ({result['ophthalmic_specific_35_primary']['exact_rate']:.3f})**; high-risk sensitivity **{result['ophthalmic_specific_35_primary']['high_sensitivity_n'][0]}/{result['ophthalmic_specific_35_primary']['high_sensitivity_n'][1]} ({result['ophthalmic_specific_35_primary']['high_sensitivity']:.3f})**; specificity **{result['ophthalmic_specific_35_primary']['high_specificity_n'][0]}/{result['ophthalmic_specific_35_primary']['high_specificity_n'][1]} ({result['ophthalmic_specific_35_primary']['high_specificity']:.3f})**.",
        f"- Binary actionable: sensitivity **{result['ophthalmic_specific_35_binary']['sensitivity_n'][0]}/{result['ophthalmic_specific_35_binary']['sensitivity_n'][1]} ({result['ophthalmic_specific_35_binary']['sensitivity']:.3f})**; specificity **{result['ophthalmic_specific_35_binary']['specificity_n'][0]}/{result['ophthalmic_specific_35_binary']['specificity_n'][1]} ({result['ophthalmic_specific_35_binary']['specificity']:.3f})**.",
        "",
        "### 2.5 Cascade vs Lexicomp (primary mapping)",
        "",
        f"- Exact agreement: **{vs_cascade['exact']}/42 ({vs_cascade['exact_rate']:.3f})**; κ **{vs_cascade['kappa']:.3f}**.",
        "",
        "## 3. Route-specific versus systemic entries",
        "",
        f"Among **{raw['route_comparison']['n_pairs_with_both_entries']}** pairs with both an ophthalmic and a systemic entry, **{raw['route_comparison']['discordant']}** were discordant. In every discordant pair the ophthalmic entry was lower; **{raw['route_comparison']['ophthalmic_no_interaction_but_systemic_alert']}** had no interaction at the ophthalmic entry but C/D/X at the systemic entry, and **{raw['route_comparison']['ophthalmic_C_but_systemic_D']}** were C vs D.",
        "",
        "| Case | Ophthalmic entry | Risk | Systemic entry | Risk |",
        "|---|---|---|---|---|",
    ]
    for ex in raw["route_comparison"]["examples"]:
        lines.append(f"| {ex['case']} | {ex['ophthalmic_entry']} | {ex['ophthalmic_risk'] or 'none'} | {ex['systemic_entry']} | {ex['systemic_risk']} |")
    lines += [
        "",
        "## 4. Interpretation",
        "",
        "The comparison has three implications. First, Lexicomp's product-level entries are genuinely route-aware: in 21 of 35 pairs the ophthalmic entry returned a lower rating than the systemic entry, and in 18 pairs it returned no interaction at all where the systemic entry returned C, D or X. This direction is consistent with the exposure premise of the manuscript.",
        "",
        "Second, Lexicomp's five-level scale is not a severity-equivalent gold standard for the three-level grade. Its C category ('monitor therapy') spans both reference-high and reference-medium pairs: 8 of 13 reference-high pairs and 7 of 19 reference-medium pairs were rated C. Under the pre-specified mapping, exact agreement is therefore modest, and high-risk sensitivity is low; under a binary 'any actionable interaction' definition, Lexicomp flags 16 of 42 pairs and captures 16 of 32 reference non-low pairs without flagging any of the 10 reference-low pairs.",
        "",
        "Third, the direction of the discordance is informative. For topical NSAID + anticoagulant pairs (ketorolac or flurbiprofen with warfarin), Lexicomp's ophthalmic entry returns no interaction while its systemic entry returns D. That is exactly the product-level blind spot the manuscript is designed to address: absence of an interaction in a product-level database is not evidence of absent systemic exposure. The cascade flags these pairs as medium, and the reference labels two of them as high; the disagreement should be read as a difference in exposure modelling, not as proof that either resource is wrong.",
        "",
        "## 5. Caveats",
        "",
        "- The accessible instance is **UpToDate 2018 via OpenMed**, not a current licensed Lexicomp subscription. Ratings may have changed since 2018.",
        "- Seven cases (apraclonidine, bromfenac, voriconazole) had no ophthalmic-specific entry; the generic ingredient entry was used and flagged. A sensitivity analysis restricted to the 35 ophthalmic-specific cases is reported above.",
        "- Lexicomp ratings are proprietary and are not redistributed in the public release; the raw extraction is retained locally for audit.",
        "- The 42-case reference labels are a subset of the frozen author-derived L1 reference set and were not separately adjudicated; they are not an independent gold standard. Agreement with them measures alignment with the manuscript's exposure model, not clinical truth.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Table S18b (body only; the supplement builder adds the heading).
    s18b = f"""| Item | Result |
|---|---|
| Cases | 42 L1 cases with a DDInter record (Table S18) |
| Ophthalmic-specific entry | 35; generic entry for apraclonidine (3), bromfenac (3), voriconazole (1) |
| Lexicomp ratings | X 1; D 0; C 15; B 1; A/no interaction 25 |
| Reference / cascade labels | high 13/9; medium 19/18; low 10/15 |

**Mapping.** Primary: X/D → high; C → medium; B/A/no interaction → low (Lexicomp definitions: X avoid, D consider modification, C monitor, B no action, A no known interaction). Because C is a broad monitoring category, C → high is a sensitivity analysis.

| Reference vs Lexicomp (primary) | high | medium | low |
|---|---:|---:|---:|
| high | 0 | 8 | 5 |
| medium | 1 | 7 | 11 |
| low | 0 | 0 | 10 |

| Three-level analysis | Exact | High-risk sensitivity | High-risk specificity | κ |
|---|---:|---:|---:|---:|
| All 42, primary | 17/42 (0.405) | 0/13 (0.000) | 28/29 (0.966) | 0.129 |
| All 42, C → high | 18/42 (0.429) | 8/13 (0.615) | 21/29 (0.724) | 0.222 |
| Ophthalmic-specific (35), primary | 15/35 (0.429) | 0/10 (0.000) | 25/25 (1.000) | 0.136 |
| Ophthalmic-specific (35), C → high | 16/35 (0.457) | 8/10 (0.800) | 18/25 (0.720) | 0.273 |

| Binary analysis (C/D/X actionable) | Exact | Non-low sensitivity | Non-low specificity | κ |
|---|---:|---:|---:|---:|
| All 42 | 26/42 (0.619) | 16/32 (0.500) | 10/10 (1.000) | 0.323 |
| Ophthalmic-specific (35) | 23/35 (0.657) | 15/27 (0.556) | 8/8 (1.000) | 0.364 |

**Route-specific entries.** Among 35 pairs with both entries, 21 were discordant; all 21 were lower for the ophthalmic entry, 18 had no interaction at the ophthalmic entry but C/D/X at the systemic entry, and 3 were C versus D (e.g., timolol ophthalmic C versus systemic D). The cascade and Lexicomp agreed exactly on 21/42 (0.500; κ 0.195).

Lexicomp was queried on 11 November 2026 through the 2018 UpToDate interface (application version 1.1) provided by OpenMed (http://167.99.184.127/d/di.htm); the 2018 interface is not a current licensed release. Each pair was queried by drug name only; no cascade grade or reference label was sent to the interface. Ratings are proprietary. Reference labels are a subset of the frozen author-derived L1 reference set, not a separate adjudication; agreement measures alignment with our exposure model, not clinical truth.
"""
    (ROOT / "outputs" / "tables" / "table_s18b_lexicomp.md").write_text(s18b, encoding="utf-8")

    print(json.dumps({
        "primary": {k: all_primary[k] for k in ["exact", "exact_rate", "high_sensitivity", "high_sensitivity_n", "high_specificity", "high_specificity_n", "kappa"]},
        "c_to_high": {k: all_c2h[k] for k in ["exact", "exact_rate", "high_sensitivity", "high_sensitivity_n", "high_specificity", "high_specificity_n", "kappa"]},
        "binary": all_binary,
        "specific_35": {k: result["ophthalmic_specific_35_primary"][k] for k in ["exact", "exact_rate", "high_sensitivity", "high_sensitivity_n", "high_specificity", "high_specificity_n", "kappa"]},
        "vs_cascade": {k: vs_cascade[k] for k in ["exact", "exact_rate", "kappa"]},
        "dist": result["risk_distribution"],
    }, indent=2))


if __name__ == "__main__":
    main()
