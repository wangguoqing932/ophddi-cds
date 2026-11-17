# -*- coding: utf-8 -*-
"""build_r2_tables.py — tables added for the Reviewer 2 revision."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "tables"
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low"}
LOW = {"systemic_absorption_low", "systemic_absorption_very_low",
       "minimal_systemic_absorption", "systemic_absorption_none"}
SEV = {"high": 3, "medium": 2, "low": 1}


def load_ddinter() -> dict:
    out = {}
    for code in ["A", "B", "C", "N", "S"]:
        with (ROOT / f"data/raw/ddinter/ddinter_code_{code}.csv").open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                a, b = row["Drug_A"].strip().lower(), row["Drug_B"].strip().lower()
                out[(a, b)] = row["Level"]
                out[(b, a)] = row["Level"]
    return out


def tier(kg, name: str) -> str | None:
    ent = kg.get_ophthalmic(name)
    if not ent:
        return None
    return next((f for f in ent["flags"] if "absorption" in f), None)


def grade_definitions() -> None:
    rows = [
        "| Grade | Operational definition | Clinical significance | Expected management | Illustrative pair |",
        "|---|---|---|---|---|",
        "| **High** | A mechanism with potential for severe harm at plausible ophthalmic exposure, or a narrow-therapeutic-index victim drug with a substantial exposure change. | Could cause hospitalisation or death if unrecognised. | Do not start without prescriber or pharmacist review. If already combined, monitor the relevant parameter (HR/BP/ECG, drug level) and consider an alternative. | Timolol + verapamil |",
        "| **Medium** | A mechanism likely to produce a measurable but usually non-severe effect, or a severe mechanism at low exposure. | May require monitoring or dose adjustment; harm is plausible but uncommon. | Review the combination, monitor the relevant parameter, and consider an alternative if monitoring is not feasible. | Ketorolac + warfarin |",
        "| **Low** | No mechanism expected to be clinically significant at ophthalmic exposure, or a mechanism with a wide therapeutic index and low exposure. | Unlikely to require action beyond usual care. | No specific action; document the review if the pair is retained. | Latanoprost + atorvastatin |",
        "| **Unassessed** | No rule and no matrix cell covers the pair. | Unknown; **not** evidence of safety. | Do not interpret as low. Refer for manual medication review or specialist consultation. | Timolol + warfarin (default path) |",
        "",
        "Grades are screening categories, not probabilities of harm. They describe the expected clinical consequence of a mechanism at the modelled exposure, not the probability that an event will occur in a given patient. The management column is the action the engine's rule or matrix advice supports; it is not a prescription.",
    ]
    (OUT / "table6_grade_definitions.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("table6 written")


def route_aware_table() -> None:
    kg = PreciseKG()
    dd = load_ddinter()
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    rows = [json.loads(l) for l in (ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl").open(encoding="utf-8")
            if json.loads(l)["method"] == "full_system"]
    common = []
    for r in rows:
        dl = LEVEL_MAP.get((dd.get((r["a_name"].lower(), r["b_name"].lower())) or "").lower())
        if dl:
            common.append((r, dl))
    methods = [
        ("DDInter (no absorption correction)", lambda r, dl: dl),
        ("RA-DDInter (route-aware filter)", lambda r, dl: "low" if tier(kg, r["a_name"]) in LOW else dl),
        ("OphDDI-CDS (full cascade)", lambda r, dl: r["predicted"]),
    ]
    out = ["| Method | n | Exact agreement | Sensitivity (high) | Specificity (high) |",
           "|---|---|---|---|---|"]
    for name, fn in methods:
        y, p = [], []
        for r, dl in common:
            y.append(prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"])
            p.append(fn(r, dl))
        n = len(y)
        ok = sum(a == b for a, b in zip(y, p))
        hi = [i for i, g in enumerate(y) if g == "high"]
        tp = sum(p[i] == "high" for i in hi)
        non = [i for i, g in enumerate(y) if g != "high"]
        tn = sum(p[i] != "high" for i in non)
        out.append(f"| {name} | {n} | {ok}/{n} ({ok/n:.3f}) | {tp}/{len(hi)} ({tp/len(hi):.3f}) | {tn}/{len(non)} ({tn/len(non):.3f}) |")
    out += ["", "Note: Restricted to the 42 L1 cases with a DDInter record; RA-DDInter retains the DDInter severity "
                "unless the ophthalmic tier is low or lower. The Lexicomp comparison, including its 2018 interface "
                "and access date, is in Supplementary Table S18b.", ""]
    (OUT / "table7_route_aware.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    # 1,933 comparison
    n = agree = 0
    diff = Counter()
    for an in kg.a_registry:
        for bn in kg.b_registry:
            dl = LEVEL_MAP.get((dd.get((an.lower(), bn.lower())) or "").lower())
            if not dl:
                continue
            ra = "low" if tier(kg, an) in LOW else dl
            lvl, _, _ = kg.deterministic_level_v2(an, bn)
            n += 1
            if ra == lvl:
                agree += 1
            else:
                diff[("cascade_higher" if SEV[lvl] > SEV[ra] else "cascade_lower")] += 1
    (OUT / "table7_route_aware_1933.json").write_text(json.dumps(
        {"n": n, "agree": agree, "agree_share": round(agree / n, 4),
         "discordant": dict(diff)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("table7 written", n, agree)


def route_aware_cases() -> None:
    kg = PreciseKG()
    dd = load_ddinter()
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    rows = [json.loads(l) for l in (ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl").open(encoding="utf-8")
            if json.loads(l)["method"] == "full_system"]
    out = ["| case | ophthalmic | systemic | DDInter | RA-DDInter | cascade | reference |",
           "|---|---|---|---|---|---|---|"]
    n = 0
    for r in rows:
        dl = LEVEL_MAP.get((dd.get((r["a_name"].lower(), r["b_name"].lower())) or "").lower())
        if not dl:
            continue
        ra = "low" if tier(kg, r["a_name"]) in LOW else dl
        g = prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"]
        n += 1
        out.append(f"| {r['case_id']} | {r['a_name']} | {r['b_name']} | {dl} | {ra} | {r['predicted']} | {g} |")
    out += ["", f"n = {n}. RA-DDInter = low if the ophthalmic tier is low or lower, otherwise the DDInter level. This table is the case-level source for Table 7.", ""]
    (OUT / "table_s18_route_aware_cases.md").write_text(chr(10).join(out) + chr(10), encoding="utf-8")
    print("S18 written", n)


def matrix_table() -> None:
    m = yaml.safe_load((ROOT / "configs/class_matrix.yaml").open(encoding="utf-8"))["matrix"]
    rows = []
    for a, cols in m.items():
        for b, c in cols.items():
            if c is None:
                continue
            rows.append((a, b, c.get("level", ""),
                         str(c.get("mechanism", "")).replace("_", " "),
                         str(c.get("advice", "")).replace("_", " "),
                         str(c.get("evidence", "")).replace("_", " ")))
    def short_ev(x: str) -> str:
        x = x.lower()
        if x.startswith("rule_") or x.startswith("rule ") or x.startswith("low_abs") or x.startswith("low abs"):
            return "rule"
        if "class" in x:
            return "class extrapolation"
        if "consensus" in x:
            return "consensus"
        if "textbook" in x or "pharmacology" in x:
            return "pharmacology"
        return x.replace("_", " ")

    out = ["**Supplementary Table S14. Class-matrix cells (n = 104): level, mechanism and evidence type.**", "",
           "| Ophthalmic row key | Systemic column key | Level | Mechanism | Evidence type |",
           "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {short_ev(str(r[5]))} |")
    counts = Counter(r[2] for r in rows)
    out += ["", "Level counts: " + ", ".join(f"{k} = {v}" for k, v in counts.items()) +
            ". `none` marks a defined cell with no established interaction; it is not a default-low path. "
            "Evidence type records whether the cell is anchored to a rule, a class extrapolation, a textbook "
            "statement, expert consensus or a pharmacological inference.", ""]
    (OUT / "table_s14_matrix_cells.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("S14 written", len(rows))


def patient_factors() -> None:
    rows = [
        "| Patient factor | How it is represented | Effect on the output | Gap |",
        "|---|---|---|---|",
        "| Age | No age input. An `elderly` patient-factor policy (≥65 years) exists as a contextual advisory; paediatric susceptibility is captured only through agent flags and evidence (e.g., alpha-2 agonists). | The pair grade is unchanged; the advisory is returned separately. | Age is not a modifier of the grade; no paediatric dosing or age-specific threshold is modelled. |",
        "| Renal function | A `renal_impairment` policy links medium-absorption agents to narrow-therapeutic-index systemic drugs; no eGFR or creatinine input. | Contextual advisory only; the pair grade is unchanged. | Renal clearance is not quantified; dialysis and acute kidney injury are not represented. |",
        "| Hepatic function | Not modelled. | No effect. | No hepatic flag, policy or dose adjustment. |",
        "| QT risk | `qt_prolonging` flags and the two QT rules; no QTc value or patient-level QT history. | Can raise the grade through a rule; no patient-specific QT risk. | QTc, electrolytes, congenital long-QT and concurrent QT drugs are not integrated. |",
        "| Dose and duration | Not modelled; the system assumes labelled ophthalmic dosing. | No effect. | Cumulative exposure, duration, adherence and overdosing are not represented. |",
        "| CYP phenotype | `cyp2d6_substrate` and `cyp3a4_substrate` flags and the CYP rules; no genotype input. | Can raise the grade through a rule; no phenotype-specific effect. | Metaboliser status, CYP2D6 inhibitors and genotype-guided dosing are not integrated. |",
        "| Instillation technique | Not modelled. Punctal occlusion and nasolacrimal drainage are cited in the evidence and recommendations. | No effect. | Technique, punctal occlusion, drop size and patient adherence are not inputs; they are discussed as exposure modifiers. |",
        "",
        "The system is therefore pair-level with three contextual patient-factor advisories, not a patient-level risk model. This is stated in the Intended use section and in the Limitations.",
    ]
    (OUT / "table_s15_patient_factors.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("S15 written")


def source_tiers() -> None:
    rows = [
        "| Tier | Source type | What it can support | What it cannot support |",
        "|---|---|---|---|",
        "| A | Regulatory product label (FDA, EMA, NMPA) | Approved indications, labelled warnings, route-specific systemic-absorption statements and labelled interactions. | A negative statement is not proof of absence; labels are not systematic reviews. |",
        "| B | Systematic review or meta-analysis | Pooled effect estimates for a defined question and population. | Often systemic-route only; may not address ophthalmic exposure or a specific pair. |",
        "| C | Original clinical study or case report | A measured exposure, a reported event or a tested hypothesis. | Single studies may be underpowered, confounded or not generalisable. |",
        "| D | In vitro, animal or pharmacokinetic first-principles evidence | Mechanistic plausibility, direction of an effect and approximate exposure. | Does not establish clinical severity or event probability in humans. |",
        "| E | Class-level mechanism inference | A hypothesis for a pair with no direct source; used to flag, not to assert. | Cannot establish that the interaction occurs, its magnitude or its severity. |",
        "",
        "The A-E tiers are a **source hierarchy**, not a strength-of-evidence grade. A label statement (A) can be less direct than a systematic review (B) for a specific pair, and an E-tier mechanism can be biologically plausible but unverified. The tiers describe provenance; they are not weights in the engine and do not enter the grade.",
    ]
    (OUT / "table_s16_source_tiers.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("S16 written")


def exposure_risk() -> None:
    rows = [
        "| Mechanism class | Exposure-risk relationship | Implication for interpretation | Example |",
        "|---|---|---|---|",
        "| Reversible pharmacodynamic antagonism or addition (beta-blockade, NSAID prostaglandin inhibition, alpha-2 agonism) | Roughly concentration-dependent, but the slope depends on receptor reserve, potency and therapeutic index. | Lower exposure usually lowers effect, but a potent agent or a narrow-therapeutic-index victim can still be clinically important. | Timolol + verapamil; ketorolac + warfarin |",
        "| Narrow-therapeutic-index pharmacokinetic interaction (CYP induction/inhibition, P-gp) | Risk depends on the fractional change in victim-drug exposure, not on the ophthalmic agent's absolute exposure. | A small degree of inhibition can matter for warfarin, digoxin, tacrolimus or cyclosporine. | Dexamethasone + CYP3A4 substrates; beta-blocker + CYP2D6 inhibitors |",
        "| Threshold or idiosyncratic reaction (sulfonamide hypersensitivity, fluoroquinolone tendon injury) | Not a simple linear function of exposure; host factors and prior sensitisation dominate. | Low exposure does not guarantee absence of risk; the grade should be read as a flag, not a probability. | Sulfacetamide; fluoroquinolones + systemic corticosteroid |",
        "| Cumulative or time-dependent toxicity (corticosteroid IOP rise, adrenal suppression) | Depends on duration and cumulative dose, which the pair-level model does not represent. | A single-pair grade cannot capture long-term risk; duration must be assessed clinically. | Topical corticosteroid + systemic corticosteroid |",
        "| Local ocular toxicity (corneal, conjunctival, IOP) | Route-independent; not a systemic DDI. | Outside the scope of the absorption model. | Prostaglandin analogues; preservative-related toxicity |",
        "",
        "The absorption tier models **systemic exposure**, not **clinical interaction risk**. Reducing exposure reduces the probability of a concentration-dependent systemic effect, but it does not eliminate risk for narrow-therapeutic-index drugs, idiosyncratic reactions or cumulative toxicity. This is why the 77.7% divergence is reported as a difference in classification, not as evidence of reduced harm.",
    ]
    (OUT / "table_s17_exposure_risk.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("S17 written")


if __name__ == "__main__":
    grade_definitions()
    route_aware_table()
    route_aware_cases()
    matrix_table()
    patient_factors()
    source_tiers()
    exposure_risk()
