# -*- coding: utf-8 -*-
"""build_supplementary_r1.py — rebuild the supplementary material for the R1 revision."""
from __future__ import annotations

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material.md"
OUT = SRC
TABLES = ROOT / "outputs/tables"

text = SRC.read_text(encoding="utf-8")


def replace_block(start: str, end: str | None, new: str) -> None:
    global text
    i = text.find(start)
    if i < 0:
        sys.exit(f"missing start: {start[:70]}")
    j = text.find(end, i + len(start)) if end else len(text)
    text = text[:i] + new + text[j:]


def read_table(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8").strip()


# ── Text S2: rule provenance ──
s2 = """## Supplementary Text S2. Rule provenance and verification

The verification report covers **8 manifest items spanning 7 distinct DOIs**. It establishes that
these records exist, are not retracted and match their titles; it does not establish that a record
supports a specific pair, route and severity. This revision therefore adds a structured audit of all
40 rules (Table S9), scoring each on three questions: does the source concern the named ophthalmic
agent, does it support the pair, and does it support the assigned severity and route.

The audit classifies 2 rules as direct ophthalmic pair evidence, 5 as contextual ophthalmic evidence,
23 as systemic-route class evidence extrapolated to the ophthalmic agent, and 10 as mechanism-only with
no pair-level clinical source. Severity is directly supported for 2 rules, inferred for 28 and
provisional for 10. "Citation-verified" in the manuscript therefore means what Table S9 records.

**Corrections made in this revision.** Four citations that named an unrelated drug were corrected.
`beta_blocker_digoxin_additive` cited Schuman 2000, a study of topical-plus-systemic beta-blockade
that does not address digoxin; the citation was removed, the rule now carries only its DDInter pair
record and is labelled class-extrapolated. `antibiotic_warfarin_enhancement` cited the timolol
DrugBank entry and now cites the warfarin monograph. `low_abs_antiplatelet` and
`low_abs_anticoagulant` cited latanoprost, a prostaglandin analogue; they are relabelled as
absorption priors rather than pair-level DDI evidence.

The report is bound to a SHA-256 of `configs/rules.yaml`, so any later edit invalidates it. The
verification report is deposited as `outputs/citation_verification_report.json`; the
rule-level audit is deposited as `data/curation/rule_provenance_audit.csv`.

"""

# ── Text S5: reproducibility and retrieval scope ──
s5 = """## Supplementary Text S5. Evaluation reproducibility

- Five temperature conditions: 0.0, 0.3, 0.6, 0.9, 1.2
- Prediction rows: 9,600; API failures: 0
- SHA-256 fingerprints are defined over **LF-normalised content**; convert CRLF to LF before hashing or Windows and Linux checkouts will differ. Evaluated rules version: the current `configs/rules.yaml` (hash in `MANIFEST.sha256`).
- Statistical tests: exact McNemar, Wilson 95% CI, bootstrap CI for kappa, Clopper-Pearson for proportions
- Revision statistics: `scripts/revision_r1_stats.py` writes `outputs/recomputed/revision_r1_stats.json`, from which every number in Sections 3.3-3.6 and Tables 3 and 5 can be regenerated.

**Retrieval-scope audit (prospective, all methods).** Of the 1,307 evidence chunks, 500 are DDInter
2.0 severity statements, and the audit reference labels for the 62 third-party cases *are* the DDInter
values. Before comparing methods we measured, for each method, how often its context contains the
pair's own DDInter statement (Table S13). `naive_rag` (BM25 top-3) contains it for 26 of 92 cases
(28.3%); `pure_llm` has no retrieval channel and `rule_context` builds its context from the
registries and rule configuration rather than the 1,307-chunk corpus, so neither has a
DDInter-statement channel. Results with and without the 26 affected cases are reported for the
cascade in Table 5 and for all methods under configuration 1 in Table S13; the configuration-2
exclusion figures quoted in Section 3.6 appear in that section.

"""

replace_block("## Supplementary Text S2. Rule provenance and verification", "## Supplementary Text S3.", s2)
replace_block("## Supplementary Text S5. Evaluation reproducibility", "## Supplementary Text S6.", s5)

# S4 figure legends: always take the current manuscript legends (includes Figure 6)
figleg = (ROOT / "outputs" / "paper" / "figure_legends.md").read_text(encoding="utf-8")
figleg = figleg.replace("# Figure Legends", "").strip()
s4 = "## Supplementary Text S4. Figure legends" + chr(10) * 2 + figleg + chr(10) * 2
replace_block("## Supplementary Text S4. Figure legends", "## Supplementary Text S5.", s4)

# ── Table S1: 15 frozen-label disagreements ──
prov = {r["case_id"]: r for r in csv.DictReader(
    (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
rows = [json.loads(l) for l in (ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl").open(encoding="utf-8")
        if json.loads(l)["method"] == "full_system"]
RATIONALE = {
    "B02": "Frozen label high; the engine returns medium, which equals the post-lock corrected label. Kept as a disagreement in the primary analysis.",
    "B12": "Frozen label medium; the engine returns high, which equals the post-lock corrected label. Kept as a disagreement in the primary analysis.",
    "C17": "Frozen label low; the engine returns medium, which equals the post-lock corrected label. Kept as a disagreement in the primary analysis.",
    "C04": "NSAID-anticoagulant bleeding risk graded medium after the flurbiprofen tier was corrected to low (0.03% formulation); the frozen label retains the systemic-route high (additive_nsaid_bleeding, low_abs_anticoagulant).",
    "G106": "Anticholinergic burden with a tricyclic antidepressant (expert-consensus matrix cell high; guideline label conservative at medium).",
    "G108": "Weak-corticosteroid potency granularity (rimexolone intermediate IOP effect; class-matrix cell coarse).",
    "G113": "Ophthalmic fluoroquinolone QT risk: low-absorption design decision vs guideline label medium.",
    "G114": "Ophthalmic fluoroquinolone QT risk: low-absorption design decision vs guideline label medium.",
    "G121": "Dexamethasone re-tiered to medium on measured plasma <1 ng/mL; the low-severity CYP3A4 rule no longer raises this pair to medium.",
    "G122": "Dexamethasone re-tiered to medium on measured plasma <1 ng/mL; the low-severity CYP3A4 rule no longer raises this pair to medium.",
    "G131": "Macrolide CYP3A4 inhibition with low-absorption ophthalmic erythromycin vs guideline label medium.",
    "G132": "Macrolide CYP3A4 inhibition with low-absorption azithromycin vs guideline label medium.",
    "G133": "Azole CYP3A4 inhibition with low-absorption voriconazole vs guideline label medium.",
    "G134": "Azole CYP3A4 inhibition with low-absorption fluconazole vs guideline label medium.",
    "G139": "Combination corticosteroid x warfarin (INR fluctuation risk) vs the frozen low label.",
    "G137": "Gated in this revision: nsaid_antihypertensive_antagonism cannot fire at this low tier, but nsaid_acei_arb_antagonism still returns medium; the frozen guideline label is high, and the ungated analysis returns high (Supplementary Table S19).",
    "G138": "Gated in this revision: nsaid_antihypertensive_antagonism cannot fire at this low tier and no other rule applies, so the pair returns low; the frozen guideline label is high, and the ungated analysis returns high (Supplementary Table S19).",
}
s1 = ["**Supplementary Table S1. L1 author-derived reference set: the seventeen exact-scale disagreements under the frozen labels, with the pharmacological rationale for each.**", "",
      "**A. Case-level grades.**", "",
      "| case | ophthalmic | systemic | reference label | system | direction |", "|---|---|---|---|---|---|"]
details = []
n_blind = n_guide = n_t1 = 0
n_dis = 0
for r in rows:
    g = prov[r["case_id"]]["gold_pre_errata"] or prov[r["case_id"]]["gold_current"]
    if r["predicted"] == g:
        continue
    n_dis += 1
    direction = "upgrade" if {"low": 1, "medium": 2, "high": 3}[r["predicted"]] > {"low": 1, "medium": 2, "high": 3}[g] else "downgrade"
    s1.append(f"| {r['case_id']} | {r['a_name']} | {r['b_name']} | {g} | {r['predicted']} | {direction} |")
    subset = r["subset"].replace("guideline_sourced", "guideline").replace("blind_frozen", "frozen")
    details.append(f"| {r['case_id']} | {subset} | {RATIONALE.get(r['case_id'], '')} |")
    if r["subset"] == "blind_frozen":
        n_blind += 1
    elif r["subset"] == "guideline_sourced":
        n_guide += 1
    else:
        n_t1 += 1
s1 += ["", "**B. Subset and rationale.**", "", "| case | subset | documented rationale |", "|---|---|---|"] + details
s1 += ["", f"Seventeen disagreements under the frozen labels: {118 - n_dis} of 118 exact agreement. The three post-lock errata cases (B02, B12, C17) are disagreements only because the primary analysis retains the frozen labels; under the corrected labels they agree. The frozen blind subset contributes {n_blind} disagreements, the T1 subset {n_t1} and the guideline subset {n_guide}. G137 and G138 are new disagreements introduced by gating `nsaid_antihypertensive_antagonism` on absorption in this revision; the ungated sensitivity analysis (Supplementary Table S19) retains the previous 103 of 118. The eleven guideline labels overridden by hand after review (Section 2.3) are G113, G114, G125, G126, G128, G131-G134, G149 and G154.", ""]
replace_block("**Supplementary Table S1.", "**Supplementary Table S2.", chr(10).join(s1))

# ── Table S2: audit disagreements with classification ──
d = json.load((ROOT / "outputs/recomputed/revision_r1_stats.json").open(encoding="utf-8"))["R1_5_disagreements"]
rev_path = ROOT / "outputs/audits/r1_5_independent_review/cases_blinded_reviewed.csv"
rev = {r["case_id"]: r["your_class"] for r in csv.DictReader(rev_path.open(encoding="utf-8-sig"))} if rev_path.exists() else {}
s2t = ["**Supplementary Table S2. DDInter audit disagreements (30) with the author and independent classifications.**", "",
       "| case | ophthalmic | systemic | DDInter | reference label | system | tier | path | rules | direction | class | independent |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in d["cases"]:
    s2t.append(f"| {c['case_id']} | {c['a']} | {c['b']} | {c['ddinter']} | {c['gold']} | {c['system']} | "
               f"{c['tier']} | {c['path']} | {', '.join(c['rules']) or '-'} | {c['direction']} | {c['class']} | "
               f"{rev.get(c['case_id'], '—')} |")
s2t += ["", f"Author classes: route-consistent downgrade = {d['by_class'].get('route_consistent_downgrade', 0)}, "
             f"unsupported undergrading = {d['by_class'].get('unsupported_undergrading', 0)}, "
             f"system over-grading = {d['by_class'].get('system_overgrading', 0)}. Of the 30 cases, 12 are on "
             "the unassessed default path (10 route-consistent downgrades and 2 unsupported undergradings); "
             "their low grade is not evidence of safety. "
             "**Independent review:** one non-author ophthalmologist (reviewer code GZQ, 14 November 2026), "
             "blinded to the author class, decision path and matched rules, reclassified all 30 from the pair, "
             "reference label, system grade, tier and direction. Exact agreement with the author classification "
             "was 14/30 (46.7%); on the 28 cases within the author's three classes, 14/28 (50.0%, kappa 0.271). "
             "The reviewer classified 14 of the 21 author route-consistent downgrades as unsupported, kept all "
             "five author unsupported undergradings as unsupported, and considered two of the four author "
             "over-grades to be supported upgrades. The author classification is descriptive and is not "
             "reproduced by the independent reviewer; both columns are shown so readers can see the disagreement.", ""]
replace_block("**Supplementary Table S2.", "**Supplementary Table S3.", "\n".join(s2t))

# ── Table S5: tier evidence ──
ev = list(csv.DictReader((ROOT / "data/curation/absorption_tier_evidence.csv").open(encoding="utf-8")))
s5t = ["**Supplementary Table S5. Per-agent systemic-absorption tier (n = 113): certainty and source.**", "",
       "Every row carries an explicit certainty label. `measured` = a reported plasma concentration, bioavailability or AUC after topical dosing; `label_statement` = the label states systemic absorption or a low-exposure claim without a value; `class_inference` = assigned from class pharmacology and label warnings and **explicitly uncertain**. Detailed formulation and exposure evidence for the 24 measured/label rows is given in Table S5b.", "",
       "| id | agent | route | tier | certainty | source |", "|---|---|---|---|---|---|"]
for r in ev:
    source = (r['source'] or '').replace('|', ';')
    s5t.append(f"| {r['ophthalmic_id'].replace('topical_ophthalmic_', '')} | {r['primary_name']} | {r['route']} | "
               f"{r['absorption_tier'].replace('systemic_absorption_', '').replace('minimal_systemic_absorption', 'minimal').replace('very_low', 'very low')} | {r['certainty']} | {source} |")
s5t += ["", "**Supplementary Table S5b. Formulation, dosing and exposure evidence for the 24 measured/label agents plus conbercept (class-inferred); the six intravitreal anti-VEGF agents are shown individually.**", "",
        "| agent | formulation / concentration | dosing | exposure evidence | source | certainty |", "|---|---|---|---|---|---|"]
for r in ev:
    if r["certainty"] in ("measured", "label_statement") or r["route"] == "intravitreal":
        source = (r['source'] or '').replace('|', ';')
        s5t.append(f"| {r['primary_name']} | {r['formulation_concentration']} | {r['dosing']} | "
                   f"{r['exposure_evidence']} | {source} | {r['certainty']} |")
s5t += ["", "Counts: measured 13 (six single agents and seven fixed combinations: five timolol combinations and two dexamethasone combinations, each following the measured component), label_statement 11, class_inference 89. Conbercept is class-inferred rather than label-stated. The 89 class-inferred rows are marked uncertain and are not evidence that the assigned band is correct.", ""]
replace_block("**Supplementary Table S5.", "**Supplementary Table S6.", "\n".join(s5t))

# S6: current rule inventory from configs/rules.yaml (regenerated table2)
t2 = (ROOT / "outputs" / "tables" / "table2_rules.md").read_text(encoding="utf-8")
t2 = t2.replace("**Table 2a.", "**A.").replace("**Table 2b.", "**B.").replace("**Table 2c.", "**C.")
s6t = "**Supplementary Table S6. Rule inventory (40 mechanism rules plus 3 patient-factor policies, current configuration).**" + chr(10) * 2 + t2 + chr(10)
replace_block("**Supplementary Table S6.", "**Supplementary Table S7.", s6t)

# ── Table S7: performance (reuse the new Table 3) ──
t3 = read_table(TABLES / "table3_performance.md")
s7 = ("**Supplementary Table S7. Method performance: frozen-label primary analysis, corrected-label sensitivity analysis, the 40-case frozen blind subset, the DDInter audit under both label sets, and configuration 2.**\n\n"
      + t3 + "\n")
replace_block("**Supplementary Table S7.", "**Supplementary Table S8.", s7)

# ── Table S8: distribution terminology ──
s8 = """**Supplementary Table S8. Reference-label distribution of the two validation sets.**

| dataset_id | labels | reference level | count | percentage |
|---|---|---|---|---|
| blind_l1 | frozen (primary) | high | 28 | 23.7% |
| blind_l1 | frozen (primary) | medium | 50 | 42.4% |
| blind_l1 | frozen (primary) | low | 40 | 33.9% |
| blind_l1 | corrected (sensitivity) | high | 28 | 23.7% |
| blind_l1 | corrected (sensitivity) | medium | 51 | 43.2% |
| blind_l1 | corrected (sensitivity) | low | 39 | 33.1% |
| blind_v3_ddinter | applied | high | 25 | 27.2% |
| blind_v3_ddinter | applied | medium | 19 | 20.7% |
| blind_v3_ddinter | applied | low | 48 | 52.2% |
| blind_l1 | total | - | 118 | 100.0% |
| blind_v3_ddinter | total | - | 92 | 100.0% |
| all | total | - | 210 | - |

Note: the primary L1 analysis uses the frozen labels (28 high / 50 medium / 40 low); the corrected labels are the sensitivity analysis (28 / 51 / 39). The DDInter audit rows give the applied absorption-corrected labels (25 / 19 / 48). The table covers 210 cases; the two development-phase sets are described in Section 3.2.
"""
replace_block("**Supplementary Table S8.", None, s8)

# Drop any existing S9-S19 appendix so the script is idempotent.
i = text.find("## Supplementary Text S9.")
if i >= 0:
    text = text[:i].rstrip()
    if text.endswith("---"):
        text = text[:-3].rstrip()

# ── Append S9-S13 and Text S10 ──
appendix = ["", "---", "", "## Supplementary Text S9. Revision provenance audit", "",
            "This revision resolves the 13 registry-versus-curation-file absorption-tier discrepancies, replaces the prior per-agent source column with a certainty-graded evidence table, audits all 40 rules on pair, route and severity support, and adds a distinction between an assessed low grade and the unassessed default path. Table S9 reports the rule audit; Table S10 reports the tier resolution and the component-wise assignment of fixed combinations; Table S11 reports the decision-path distribution and lists the unassessed pairs; Table S12 reports the route-restricted analysis; Table S13 reports the retrieval-overlap audit. The scripts that generate these tables are `scripts/build_absorption_evidence_table.py`, `scripts/build_revision_tables.py` and `scripts/revision_r1_stats.py`.", ""]
appendix += ["## Supplementary Text S10. Rule and matrix construction protocol", "",
             "**Candidate generation.** Rules were generated from three sources: DDInter 2.0 pairs linking an ophthalmic agent to a systemic drug class; ophthalmic product labels (warnings and drug-interaction sections); and published case reports or reviews. Candidates were retained when the mechanism was explainable by an entity flag already present in the registry or could be added with a documented definition.", "",
             "**Rule encoding and severity.** Each candidate was encoded as an entity-flag predicate with match-all or match-any semantics. Severity was assigned in a fixed order: the DDInter level where the pair was recorded; otherwise the label's warning category; otherwise the clinical consequence expected from the mechanism and the therapeutic index of the systemic drug. The support level of each severity is recorded in Table S9 as direct, inferred or provisional.", "",
             "**Adjudication.** The rule inventory was reviewed by the study team and the two clinician authors; disagreements were resolved by consensus. There was no formal Delphi panel, blinded review or independent clinical committee. The only post-lock severity change was the dexamethasone CYP3A4 rule, downgraded from medium to low after the measured plasma concentration was found to be below 1 ng/mL.", "",
             "**Class matrix.** The 21 ophthalmic row keys and 34 systemic column keys (33 with defined cells, drawn from the 40 systemic classes) were defined from the registry classes. 83 actionable cells were defined from the rule set, class extrapolation, expert consensus or pharmacological inference; 21 additional cells are explicitly marked none. Each cell records a level, mechanism, advice and evidence type (Table S14). Four upgrade rules require a class match plus a high-absorption or selectivity flag. Cell levels were reviewed with the rule set by the study team and were not independently adjudicated.", "",
             "**Reproducibility.** The rule file, matrix file and their SHA-256 fingerprints are deposited. The rule-level audit is `data/curation/rule_provenance_audit.csv`; the matrix is `configs/class_matrix.yaml`.", "",
             "## Supplementary Tables S9-S19", ""]
for num, title, path in [
    ("S9", "Rule provenance audit (40 rules): evidence grade, route support and severity support.", "table_s9_rule_provenance.md"),
    ("S10", "Resolution of the 13 tier discrepancies, component-wise fixed-combination assignment, and certainty of the 113 tiers.", "table_s10_tier_resolution.md"),
    ("S11", "Decision-path attribution, the unassessed pairs, and low-tier rule overrides.", "table_s11_path_attribution.md"),
    ("S12", "Route-restricted analysis: 104 topical versus 9 non-topical agents.", "table_s12_route_scope.md"),
    ("S13", "Retrieval-overlap audit by method.", "table_s13_retrieval_overlap.md"),
    ("S14", "Class-matrix cells (n = 104): level, mechanism and evidence type.", "table_s14_matrix_cells.md"),
    ("S15", "Patient-specific factors: representation, effect on the output and remaining gap.", "table_s15_patient_factors.md"),
    ("S16", "Source tiers A-E: what each can and cannot support.", "table_s16_source_tiers.md"),
    ("S17", "Exposure-risk relationship by mechanism class.", "table_s17_exposure_risk.md"),
    ("S18", "Case-level route-aware comparison on the 42 L1 cases with a DDInter record.", "table_s18_route_aware_cases.md"),
    ("S18b", "Lexicomp route-aware comparison on the same 42 cases.", "table_s18b_lexicomp.md"),
    ("S19", "Gated primary analysis versus ungated sensitivity analysis.", "table_s19_gating_sensitivity.md"),
]:
    body = read_table(TABLES / path)
    lines = body.splitlines()
    while lines and (not lines[0].strip() or lines[0].strip().startswith("**Supplementary Table")):
        lines.pop(0)
    appendix += [f"**Supplementary Table {num}. {title}**", "", chr(10).join(lines), ""]
text = text.rstrip() + "\n" + "\n".join(appendix) + "\n"

# R1 terminology: risk labels are "reference labels", not "gold"; keep file paths untouched.
for old, new in [
    ("gold shown", "reference shown"),
    ("gold source", "reference source"),
    ("proposed gold grade", "proposed reference grade"),
    ("gold construction", "reference construction"),
    ("gold homogeneity", "reference-label homogeneity"),
    ("absorption-corrected gold", "absorption-corrected reference labels"),
    ("under that gold", "under those reference labels"),
    ("the gold", "the reference labels"),
    ("Gold level", "Reference level"),
    ("corrected gold", "corrected reference labels"),
    ("gold-level", "reference-level"),
    ("earlier-round gold", "earlier-round label"),
    ("scores 60 of 92 (0.652)", "scores 61 of 92 (0.663)"),
    ("An illustrative positive predictive value at 1% prevalence is given in Section 4.4; prospective, outcome-linked evaluation is required future work (Sections 4.4, 4.5)",
     "No outcome data are available, so predictive value for adverse events cannot be estimated; prospective, outcome-linked evaluation is required future work (Sections 4.4, 4.5)"),
    ("under an adequate output budget with a reasoning model", "in configuration 2 with a reasoning model (3000-token allowance)"),
]:
    text = text.replace(old, new)
OUT.write_text(text, encoding="utf-8")
print("supplementary rebuilt", len(text), "chars")
