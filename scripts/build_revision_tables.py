# -*- coding: utf-8 -*-
"""build_revision_tables.py — regenerate the tables used by the R1 revision.

Writes:
  outputs/tables/table3_performance.md
  outputs/tables/table5_audit_strata.md
  outputs/tables/table_s9_rule_provenance.md
  outputs/tables/table_s10_tier_resolution.md
  outputs/tables/table_s11_path_attribution.md
  outputs/tables/table_s12_route_scope.md
  outputs/tables/table_s13_retrieval_overlap.md
"""
from __future__ import annotations

import csv
import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

LEVELS = ["low", "medium", "high"]
TABLES = ROOT / "outputs" / "tables"


def kappa(a, b):
    n = len(a)
    obs = sum(x == y for x, y in zip(a, b)) / n
    exp = sum((a.count(lv) / n) * (b.count(lv) / n) for lv in LEVELS)
    return (obs - exp) / (1 - exp) if exp != 1 else 0.0


def metrics(y, p):
    n = len(y)
    correct = sum(a == b for a, b in zip(y, p))
    hi = [i for i, g in enumerate(y) if g == "high"]
    tp = sum(p[i] == "high" for i in hi)
    non = [i for i, g in enumerate(y) if g != "high"]
    tn = sum(p[i] != "high" for i in non)
    prec = tp / (tp + sum(1 for i, g in enumerate(y) if g != "high" and p[i] == "high")) if tp else 0.0
    sens = tp / len(hi) if hi else 0.0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0.0
    return {"n": n, "correct": correct, "acc": correct / n, "sens": sens,
            "spec": tn / len(non) if non else 0.0, "f1": f1, "kappa": kappa(y, p)}


def load_l1():
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    out = {}
    for seed in range(5):
        for line in (ROOT / f"outputs/multiseed_per_dataset/blind_l1__seed{seed}.jsonl").open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            out.setdefault(r["method"], {}).setdefault(r["case_id"], []).append(r)
    return prov, out


def fmt(x, d=3):
    return f"{x:.{d}f}"


def table3():
    prov, l1 = load_l1()
    rows = ["| Dataset | Label set n | Method | n | Sensitivity (high) | Specificity (high) | F1 (high) | Agree. | Cohen's kappa |",
            "|---|---|---|---|---|---|---|---|---|"]
    for label, lab_name in [("frozen", "L1, frozen (primary)"), ("corrected", "L1, corrected (sensitivity)")]:
        for m in ["pure_llm", "naive_rag", "rule_context", "full_system"]:
            mid = "lightrag" if m == "rule_context" else m
            per = []
            for seed in range(5):
                y, p = [], []
                for cid, recs in l1[mid].items():
                    r = next(x for x in recs if x["seed"] == seed)
                    g = (prov[cid]["gold_pre_errata"] or prov[cid]["gold_current"]) if label == "frozen" else prov[cid]["gold_current"]
                    y.append(g)
                    p.append(r["predicted"])
                per.append(metrics(y, p))
            rows.append(f"| {lab_name} | 118 | {m} | 118 | "
                        f"{fmt(st.mean(x['sens'] for x in per))} | {fmt(st.mean(x['spec'] for x in per))} | "
                        f"{fmt(st.mean(x['f1'] for x in per))} | {fmt(st.mean(x['acc'] for x in per))} | "
                        f"{fmt(st.mean(x['kappa'] for x in per))} |")
    # no-development subset, frozen labels
    for m in ["pure_llm", "naive_rag", "rule_context", "full_system"]:
        mid = "lightrag" if m == "rule_context" else m
        per = []
        for seed in range(5):
            y, p = [], []
            for cid, recs in l1[mid].items():
                if not any(x["subset"] == "blind_frozen" for x in recs):
                    continue
                g = prov[cid]["gold_pre_errata"] or prov[cid]["gold_current"]
                y.append(g)
                p.append(next(x for x in recs if x["seed"] == seed)["predicted"])
            per.append(metrics(y, p))
        rows.append(f"| L1, frozen blind (40) | 40 | {m} | 40 | {fmt(st.mean(x['sens'] for x in per))} | "
                    f"{fmt(st.mean(x['spec'] for x in per))} | {fmt(st.mean(x['f1'] for x in per))} | "
                    f"{fmt(st.mean(x['acc'] for x in per))} | {fmt(st.mean(x['kappa'] for x in per))} |")
    # audit, applied and re-derived
    audit = {c["case_id"]: c for c in json.load(
        (ROOT / "outputs/blind_test/blind_set_v3_ddinter.json").open(encoding="utf-8"))}
    rederived = {c["case_id"]: c["gold_rederived"] for c in json.load(
        (ROOT / "outputs/recomputed/audit_gold_rederived.json").open(encoding="utf-8"))["changed_cases"]}
    ap = {}
    for seed in range(5):
        for line in (ROOT / f"outputs/multiseed_per_dataset/blind_v3_ddinter__seed{seed}.jsonl").open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            ap.setdefault(r["method"], {}).setdefault(r["case_id"], []).append(r)
    for label, lab_name in [("applied", "DDInter audit, applied"), ("rederived", "DDInter audit, re-derived")]:
        for m in ["pure_llm", "naive_rag", "rule_context", "full_system"]:
            mid = "lightrag" if m == "rule_context" else m
            per = []
            for seed in range(5):
                y, p = [], []
                for cid, recs in ap[mid].items():
                    r = next(x for x in recs if x["seed"] == seed)
                    g = audit[cid]["proposed_gold"] if label == "applied" else rederived.get(cid, audit[cid]["proposed_gold"])
                    y.append(g)
                    p.append(r["predicted"])
                per.append(metrics(y, p))
            rows.append(f"| {lab_name} | 92 | {m} | 92 | {fmt(st.mean(x['sens'] for x in per))} | "
                        f"{fmt(st.mean(x['spec'] for x in per))} | {fmt(st.mean(x['f1'] for x in per))} | "
                        f"{fmt(st.mean(x['acc'] for x in per))} | {fmt(st.mean(x['kappa'] for x in per))} |")
    # configuration 2
    glm = json.load((ROOT / "outputs/glm53_baselines/metrics.json").open(encoding="utf-8"))
    for ds, lab_name, n in [("blind_l1", "Configuration 2, L1 (corrected)", 118),
                            ("blind_v3_ddinter", "Configuration 2, audit (applied)", 92)]:
        for m in ["pure_llm", "naive_rag", "rule_context"]:
            mid = "lightrag" if m == "rule_context" else m
            mv = glm[ds][mid]["majority_vote"]
            rows.append(f"| {lab_name} | {n} | {m} | {n} | {fmt(mv['sens'])} | {fmt(mv['spec'])} | "
                        f"{fmt(mv['f1'])} | {fmt(mv['acc3'])} | {fmt(mv['kappa'])} |")
    note = ("\nNote: 10-token rows (L1 and audit) are means over the five temperature conditions; "
            "full_system is deterministic (SD = 0). Configuration 2 rows use the majority vote over five "
            "repeats at temperature 0.0 with the reasoning model (glm-5.3-flash, max_tokens 3000). "
            "The frozen-label rows are the primary analysis; corrected-label rows are the sensitivity "
            "analysis (frozen labels: `gold_pre_errata` in `outputs/recomputed/l1_gold_provenance.csv`, falling back to `gold_current` when empty; the `gold_risk` field in the prediction files stores the corrected labels). The frozen blind row is the 40-case subset; both B01-B20 and C01-C20 were reviewed during development "
            "(C entered the class-matrix loop in v2.1-v2.3; B informed rule-gap diagnosis and matrix design), so neither half is development-free. `rule_context` is the method stored as "
            "`lightrag` in the deposited code. Configuration 1 rule_context was re-run with corrected "
            "exposure bands and absorption gate; pure_llm and naive_rag were not re-run and share the "
            "original system prompt, which lists dexamethasone as >50%. Configuration 2 rule_context "
            "uses the pre-correction prompt and is not directly comparable to the corrected configuration-1 rule_context.\n")
    (TABLES / "table3_performance.md").write_text("\n".join(rows) + "\n" + note, encoding="utf-8")
    print('table3 rows', len(rows) - 2)


def table5():
    stats = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_5_audit"]
    rows = ["| Reference labels | Subset | n | Agreement | Sensitivity (high) | Specificity (high) | Kappa |",
            "|---|---|---|---|---|---|---|"]
    for label in ["applied", "rederived"]:
        for sub, key in [("all", label), ("kept at DDInter (label-independent)", f"kept62_{label}"),
                         ("26 retrievable cases excluded", f"excl26_{label}")]:
            e = stats[key]["full_system"]
            rows.append(f"| {label} | {sub} | {e['n']} | {e['agreement']:.3f} ({e['correct']}/{e['n']}) | "
                        f"{e['sensitivity']:.3f} ({e['high_tp']}/{e['high_n']}) | {e['specificity']:.3f} | {e['kappa']:.3f} |")
    d = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_5_disagreements"]
    rows += ["", "**Disagreement classification (applied labels).**", "",
             "| Class | n | Cases |", "|---|---|---|"]
    for cls, name in [("route_consistent_downgrade", "Route-consistent downgrade"),
                      ("unsupported_undergrading", "Unsupported undergrading"),
                      ("system_overgrading", "System over-grading")]:
        cases = [c["case_id"] for c in d["cases"] if c["class"] == cls]
        rows.append(f"| {name} | {len(cases)} | {', '.join(cases)} |")
    # Independent review of the same 30 cases (one non-author ophthalmologist).
    rev_path = ROOT / "outputs/audits/r1_5_independent_review/cases_blinded_reviewed.csv"
    ir_path = ROOT / "outputs/audits/r1_5_independent_review/independent_review_results.json"
    if rev_path.exists() and ir_path.exists():
        rev = {r["case_id"]: r["your_class"] for r in csv.DictReader(rev_path.open(encoding="utf-8-sig"))}
        ir = json.load(ir_path.open(encoding="utf-8"))
        rows += ["", "**Independent review of the 30 disagreements (one non-author ophthalmologist, 14 November 2026).**", "",
                 "| Class | Author | Independent |", "|---|---:|---:|"]
        for cls, name in [("route_consistent_downgrade", "Route-consistent downgrade"),
                          ("unsupported_undergrading", "Unsupported undergrading"),
                          ("system_overgrading", "System over-grading"),
                          ("supported_upgrade", "Supported upgrade")]:
            a = sum(1 for c in d["cases"] if c["class"] == cls)
            b = sum(1 for v in rev.values() if v == cls)
            rows.append(f"| {name} | {a if a else '—'} | {b if b else '—'} |")
        rows += ["", f"Note: Exact agreement: {ir['n_exact']}/{ir['n_cases']} "
                     f"({ir['n_exact']/ir['n_cases']:.1%}); on the {ir['n_scored_three_class']} cases within the "
                     f"author's three classes, {ir['n_exact']}/{ir['n_scored_three_class']} "
                     f"({ir['n_exact']/ir['n_scored_three_class']:.1%}, kappa {ir['cohen_kappa']:.3f}). "
                     "The reviewer classified 14 of the 21 author route-consistent cases as unsupported, "
                     "kept all five author unsupported cases as unsupported, and considered two author "
                     "over-grades to be supported upgrades. The `class` column above is the author "
                     "classification; the independent classification is in Supplementary Table S2."]
    leak = json.load((ROOT / "outputs/recomputed/naive_rag_leakage.json").open(encoding="utf-8"))
    rows += ["", "**Retrieval overlap (naive_rag, top-3).**", "",
             "| Subset | n | Cases with the pair's own DDInter statement | Rate |", "|---|---|---|---|"]
    for s in leak["subsets"]:
        label = s["subset"].replace("gold source", "reference source").replace("gold is low", "reference label is low")
        rows.append(f"| {label} | {s['n']} | {s['leaked']} | {s['rate']:.3f} |")
    (TABLES / "table5_audit_strata.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print('table5 rows', len(rows))


def table_s9():
    rows = list(csv.DictReader((ROOT / "data/curation/rule_provenance_audit.csv").open(encoding="utf-8")))
    out = ["**A. Rule identifier, severity and evidence grade.**", "",
           "| Rule | Severity | Evidence grade |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {r['rule_id'].replace('_', ' ')} | {r['severity']} | {r['evidence_grade'].replace('_', ' ')} |")
    out += ["", "**B. Route support, severity support and source record.**", "",
            "| Rule | Route support | Severity support | Source record |", "|---|---|---|---|"]
    for r in rows:
        src = re.sub(r"https?://\S+", "", r["source_record"]).replace("|", "/")
        src = src.replace("DrugBank:", "DrugBank ").replace("  ", " ").strip()
        out.append(f"| {r['rule_id'].replace('_', ' ')} | {r['route_support'].replace('_', ' ')} | {r['severity_support']} | {src} |")
    counts = Counter(r["evidence_grade"] for r in rows)
    out.append("")
    out.append("Counts: " + ", ".join(f"{k} = {v}" for k, v in counts.items()) + ".")
    (TABLES / "table_s9_rule_provenance.md").write_text(chr(10).join(out) + chr(10), encoding="utf-8")
    print('table S9 rows', len(out))


def table_s10():
    rows = list(csv.DictReader((ROOT / "data/curation/absorption_tier_evidence.csv").open(encoding="utf-8")))
    out = ["**A. The 13 resolved registry-versus-curation discrepancies.**", "",
           "| Agent | Prior registry tier | Prior curation tier | Final tier | Basis |", "|---|---|---|---|---|"]
    prior_cur = {
        "Dorzolamide": "medium", "Brinzolamide": "medium", "Timolol/Latanoprost": "medium",
        "Timolol/Travoprost": "medium", "Timolol/Bimatoprost": "medium", "Timolol/Brimonidine": "medium",
        "Timolol/Dorzolamide": "medium", "Dexamethasone": "medium", "Atropine": "medium",
        "Tobramycin/Dexamethasone": "low", "Neomycin/Polymyxin B/Dexamethasone": "low",
        "Sulfacetamide/Prednisolone": "low", "Accelidine": "medium"}
    # registry values before this revision; three agents were re-tiered high -> medium
    prior_registry = {"Dexamethasone": "systemic_absorption_high",
                      "Tobramycin/Dexamethasone": "systemic_absorption_high",
                      "Neomycin/Polymyxin B/Dexamethasone": "systemic_absorption_high",
                      "Dorzolamide": "systemic_absorption_low",
                      "Brinzolamide": "systemic_absorption_low"}
    for r in rows:
        if r["primary_name"] in prior_cur:
            prior = prior_registry.get(r["primary_name"], r["absorption_tier"])
            basis = r["resolution_note"] or r["exposure_evidence"]
            out.append(f"| {r['primary_name']} | {prior} | {prior_cur[r['primary_name']]} | "
                       f"{r['absorption_tier']} | {basis} |")
    out += ["", "**B. Fixed combinations: component tiers and product assignment.**", "",
            "| Product | Component tiers | Product tier |", "|---|---|---|"]
    comp = {
        "Timolol/Latanoprost": "timolol high + latanoprost low",
        "Timolol/Travoprost": "timolol high + travoprost low",
        "Timolol/Bimatoprost": "timolol high + bimatoprost low",
        "Timolol/Brimonidine": "timolol high + brimonidine medium",
        "Timolol/Dorzolamide": "timolol high + dorzolamide very low",
        "Brimonidine/Brinzolamide": "brimonidine medium + brinzolamide very low",
        "Brimonidine/Dorzolamide": "brimonidine medium + dorzolamide very low",
        "Netarsudil/Latanoprost": "netarsudil low + latanoprost low",
        "Tobramycin/Dexamethasone": "tobramycin low + dexamethasone medium",
        "Neomycin/Polymyxin B/Dexamethasone": "neomycin low + polymyxin B very low + dexamethasone medium",
        "Bacitracin/Polymyxin B": "bacitracin very low + polymyxin B very low",
        "Sulfacetamide/Prednisolone": "sulfacetamide low + prednisolone medium",
    }
    tier = {r["primary_name"]: r["absorption_tier"] for r in rows}
    for name, comps in comp.items():
        out.append(f"| {name} | {comps} | {tier.get(name, 'n/a')} |")
    out += ["", "**C. Certainty of the 113 tier assignments.**", "",
            "| Certainty | n | Meaning |", "|---|---|---|",
            "| measured | 13 | A reported plasma concentration, bioavailability or AUC after topical dosing; six single agents and seven fixed combinations (five timolol, two dexamethasone) use the measured component |",
            "| label_statement | 11 | The product label states systemic absorption or a low-exposure claim without a value |",
            "| class_inference | 89 | Assigned from class pharmacology and label warnings; marked uncertain |"]
    (TABLES / "table_s10_tier_resolution.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print('table S10 rows', len(out))


def table_s11():
    p = json.load((ROOT / "outputs/audits/path_attribution.json").open(encoding="utf-8"))
    out = ["**A. Decision paths across the full 113 x 232 grid (26,216 graded pairs).**", "",
           "| Path | n | Share | high | medium | low |", "|---|---|---|---|---|---|"]
    for path, e in p["paths"].items():
        lv = e["levels"]
        out.append(f"| {path} | {e['n']} | {e['pct']}% | {lv.get('high', 0)} | {lv.get('medium', 0)} | {lv.get('low', 0)} |")
    st = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_3_paths_1933"]
    out += ["", "**B. Decision paths among the 1,933 graded-severity pairs.**", "",
            "| Path | n |", "|---|---|"]
    for k, v in st["by_path"].items():
        out.append(f"| {k} | {v} |")
    out += ["", f"Assessed-only: {st['assessed_only']['n']} pairs, {st['assessed_only']['downgrade']} downgrades "
                f"({st['assessed_only']['downgrade_share']:.3f}).", "",
            f"**C. The {len(st['default_low_pairs'])} pairs on the default (unassessed) path.**", "",
            "| Ophthalmic | Systemic | DDInter level |", "|---|---|---|"]
    for pair in st["default_low_pairs"]:
        out.append(f"| {pair['a']} | {pair['b']} | {pair['ddinter']} |")
    over = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_3_low_tier_overrides"]
    out += ["", "**D. Low-tier pairs that received medium or high grades through a rule (1,933 graded-severity pairs).**", "",
            "| Level | n |", "|---|---|"]
    for k, v in over["by_level"].items():
        out.append(f"| {k} | {v} |")
    out += ["", "Rules involved: " + ", ".join(
        f"`{k}` ({v})" for k, v in over["by_rule"].items()) + ".", ""]
    (TABLES / "table_s11_path_attribution.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print('table S11 rows', len(out))


def table_s12():
    st = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_4_route"]
    out = ["| Scope | n | Downgrade | Share | From high | Low-absorption downgrades | Share of downgrades |",
           "|---|---|---|---|---|---|---|"]
    for name, key in [("104 topical agents", "topical"), ("9 non-topical agents", "non_topical")]:
        e = st[key]
        out.append(f"| {name} | {e['n']} | {e['downgrade']} | {e['downgrade_share']:.3f} | {e['from_high']} | "
                   f"{e['low_absorption_downgrades']} | {e['low_absorption_downgrades']/e['downgrade']:.3f} |")
    out += ["", "The three non-topical pairs all involve aflibercept: aflibercept + azathioprine (DDInter moderate), "
                "aflibercept + leflunomide (major) and aflibercept + clozapine (major); all three were downgraded, "
                "two from high. The remaining eight non-topical agents have no DDInter record against the 232-agent "
                "systemic registry.", ""]
    (TABLES / "table_s12_route_scope.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print('table S12 rows', len(out))


def table_s13():
    leak = json.load((ROOT / "outputs/recomputed/naive_rag_leakage.json").open(encoding="utf-8"))
    audit = {c["case_id"]: c for c in json.load(
        (ROOT / "outputs/blind_test/blind_set_v3_ddinter.json").open(encoding="utf-8"))}
    rederived = {c["case_id"]: c["gold_rederived"] for c in json.load(
        (ROOT / "outputs/recomputed/audit_gold_rederived.json").open(encoding="utf-8"))["changed_cases"]}
    leak26 = set(leak["subsets"][2]["cases"])
    preds = {}
    for seed in range(5):
        for line in (ROOT / f"outputs/multiseed_per_dataset/blind_v3_ddinter__seed{seed}.jsonl").open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            preds.setdefault(r["method"], {}).setdefault(r["case_id"], {})[seed] = r["predicted"]
    out = ["**A. Retrieval overlap (naive_rag, top-3).**", "",
           "| Subset | n | Cases with the pair's own DDInter statement | Rate |", "|---|---|---|---|"]
    for s in leak["subsets"]:
        label = s["subset"].replace("gold source", "reference source").replace("gold is low", "reference label is low")
        out.append(f"| {label} | {s['n']} | {s['leaked']} | {s['rate']:.3f} |")
    out += ["", "**B. All methods with and without the 26 retrievable cases (mean over five temperature conditions).**", "",
            "| Labels | Subset | Method | n | Agreement | Sensitivity (high) | Specificity (high) |",
            "|---|---|---|---|---|---|---|"]
    for label in ("applied", "rederived"):
        for subset, ids in (("all 92", set(audit)), ("26 excluded", set(audit) - leak26)):
            for method in ("full_system", "pure_llm", "naive_rag", "lightrag"):
                disp = "rule_context" if method == "lightrag" else method
                per = []
                for seed in range(5):
                    y, p = [], []
                    for cid in sorted(ids):
                        g = audit[cid]["proposed_gold"] if label == "applied" else rederived.get(cid, audit[cid]["proposed_gold"])
                        y.append(g)
                        p.append(preds[method][cid][seed])
                    per.append(metrics(y, p))
                n = per[0]["n"]
                out.append(f"| {label} | {subset} | {disp} | {n} | {st.mean(x['acc'] for x in per):.3f} | "
                           f"{st.mean(x['sens'] for x in per):.3f} | {st.mean(x['spec'] for x in per):.3f} |")
    out += ["", "`pure_llm` and `rule_context` have no DDInter-statement retrieval channel; their rows are reported "
                "for consistency. The 26 cases are those whose own DDInter statement appears in the naive_rag top-3.", ""]
    (TABLES / "table_s13_retrieval_overlap.md").write_text(chr(10).join(out) + chr(10), encoding="utf-8")
    print('table S13 rows', len(out))


if __name__ == "__main__":
    table3()
    table5()
    table_s9()
    table_s10()
    table_s11()
    table_s12()
    table_s13()
