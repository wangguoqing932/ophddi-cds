# Response to the Editor and Reviewer — Final Round

**Manuscript:** OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening
**Submission ID:** 363ea8da-e16c-45ce-bbf1-39ff3555463b
**Decision:** Rejected, 17 October 2026
**Purpose of this document:** a complete, verifiable record of how each point in the final decision was addressed in the manuscript and the deposited code. This is not a resubmission letter; it is the audit trail for the revised article.

---

## How to read this document

Every row below names the artefact that changed and the place a reader can check it. Where a point cannot be closed without a document that does not exist (for example a committee determination that was never issued, or a co-reviewer's original form that was never scanned), the manuscript says so explicitly rather than asserting that the point is resolved. The guiding rule for this revision was: **no claim in the text that the deposit cannot support.**

The final round raised 5 editor points and 7 reviewer points. All 12 are addressed; 9 are fully closed in the text and deposit, and 3 are closed as far as the available record allows, with the residual gap stated in the manuscript.

---

## Part A — Editor

### A1. Ethics: no named committee, consent unstated, independence overstated, editor-addressed sentence

| Sub-point | Status | Change |
|---|---|---|
| Exemption claim names no committee | Closed | The Ethics declaration now names the competent body — the Ethics Committee of the First Affiliated Hospital of Xinjiang Medical University — and states that **no determination was requested from it**, rather than claiming an exemption granted by an unnamed committee. |
| Questionnaire never mentions research use or publication | Closed (disclosed) | §2.5 and the Ethics declaration state that the form asked for the expert's independent professional judgment but did not describe research use or publication. This is presented as a limitation of the consent process, not defended. |
| How consent was obtained is not stated | Closed (disclosed) | The Ethics declaration states that no separate written consent form was signed; the forms were distributed by the study team on 3 August 2026, the return of a completed questionnaire is the only record of agreement, and no dated written consent document or record identifying who distributed the forms exists. |
| One expert sits on the research team, so "two independent ophthalmologists" overstates independence | Closed | §2.1, §2.5, §3.8, §3.9, §4.1, §4.3 and the Abstract now describe the exercise as a **grade review / perspective comparison**, never as an independent assessment, and state that one expert is a member of the study team. The word "independent" is retained only where it is accurate (the ratings were made independently of each other). |
| Remove the sentence addressed to the editor | Closed | The sentence "we ask the editor to treat this study as exempt" has been deleted from the Declarations. No editor-addressed text remains in the manuscript. |
| Consent-for-publication conflict | Closed | The statement now reads that the manuscript contains no identifiable personal data and that expert ratings are reported under pseudonymous case identifiers, which is consistent with the paragraph above it. |

### A2. The errata cases are inside the frozen blind subset; timing never stated

| Sub-point | Status | Change |
|---|---|---|
| Three errata cases are L1 cases B02, B12, C17 and are labelled `blind_frozen` | Closed | §3.8 now states that R01 = B02, R02 = B12, R03 = C17, R10 = B18, R11 = C20, and that **all five belong to the 40-case frozen blind subset**. The earlier claim that the lock excluded them has been deleted. |
| The letter and script say gold was changed to the system's grades shortly before review, contradicting §2.3 | Closed | §2.3 now states that the 58 guideline-sourced labels and the initial 40 blind proposals were drafted without reference to system outputs, with three documented exceptions: B02 high→medium, B12 medium→high and C17 low→medium, corrected after the lock and before the questionnaire was drafted. The blanket "without reference to system outputs" claim is gone. |
| Under pre-correction labels the frozen subset would be 36 of 40 | Closed | §3.8 and §3.9 report **both readings**: 39 of 40 and 107 of 118 with the corrected labels; **36 of 40 and 104 of 118** under the pre-correction labels. |
| Timing relative to the lock never stated | Closed | The full sequence is now in §3.8: lock 31 July 2026 (`blind_set_v3.sha256`, `df2890f6…`; audit-design lock `8956cfe6…`); corrected set files timestamped 18:08/18:30 on 31 July; questionnaire PDF timestamped 20:22 on 31 July; corrected files committed 3 August 2026 (`acd9f44a…`, `61dc8af7…`); questionnaires completed 3 August; transcribed 8 August. |

### A3. Expert evaluation: stale figure, wrong weighted kappas, unsupported premise, unverifiable expert 2

| Sub-point | Status | Change |
|---|---|---|
| Figure 3 byte-identical to v3.0, legend keeps old kappas and the removed inference | Closed | Figure 3 was **regenerated** from the recomputed statistics with Matplotlib (`scripts/draw_figure3.py`). Panel (a) now shows unweighted κ, quadratic-weighted κ and raw agreement for five comparisons; panel (b) shows gold, the grade displayed on the form and both experts' ratings, with R10/R11 visibly separated. Source data are deposited as `outputs/figures/source_data/figure3_source.csv` and `figure3_expert_agreement.csv`. The legend no longer contains "rather than a system-specific artifact". |
| The quadratic-weighted kappas are wrong: −0.630 and −0.793 come from alphabetical sorting; on the ordinal scale they are +0.355 and +0.31 | Closed | Confirmed and fixed. `_kappa_core` in `scripts/stats_tests.py` built its confusion matrix from `sorted(set(labels))`, i.e. alphabetical order high < low < medium. It now takes the category order from the declared levels low < medium < high. Recomputed values: **+0.355 (expert 1 vs displayed), +0.313 (expert 2 vs displayed), +0.875 (inter-expert)**; against the gold +0.473 and +0.438. A regression test (`tests/test_stats_kappa.py`) locks these values. |
| The "system reproduced its gold" premise appears in six sections; Table 6 contradicts it for R10/R11 | Closed | Every passage was rewritten. The Abstract, §1, §3.8, §4.1, §4.3 and §4.4 now report the correct comparisons: expert 1 4/12 against gold versus 2/12 against the displayed grade; expert 2 3/12 versus 1/12. The phrase "reproduced its gold" no longer appears. |
| Expert 1 agrees with gold on 4/12 but with the system shown on 2/12; expert 2 3/12 and 1/12; each rated 8 of 12 lower, not 10 | Closed | §3.8 reports exactly these counts and states that the two comparisons are **not** "to the same degree". The one-directional shift is reported as 8 of 12 for each expert against the gold (8 of 8 and 8 of 9 discordant), and 10 of 12 against the displayed grades. |
| Which did the engine return for R10/R11? | Closed | §3.8 states plainly: the engine returned **low** both at review time and in the deposited re-run; the questionnaire displayed **medium**, a class-level conservative hint written by the study team, not the engine's output. Table 6 now has separate `engine grade` and `system shown` columns. Evidence: the design file's own system column records low for both; the cascade core is bit-identical to the 3 August 2026 commit; the only later configuration edit (23 September 2026) repaired a malformed advice string and altered no level. |
| "T1 expert" files conflict with "no human assigned gold"; who was it, which labels, when, under what approval | Closed (disclosed) | §2.3 now states that **20 of the 118 L1 labels (G01–G20) originate from an earlier, separately conducted expert-informed exercise** by a clinical ophthalmologist on the research team of the study named in the Ethics declaration; five of them (G04, G05, G08, G16, G19) differ from DDInter and follow that opinion. The exercise predates the 31 July 2026 lock, has no separate approval or consent record, and the deposited record does not name the clinician. The manuscript states that whether the T1 exercise and the 12-case review involved the same individual cannot be established from the deposit, and does not assert it. The Generative AI statement was corrected accordingly. |
| Second, unreported 12-item instrument (phase4) — was it administered? | Closed | §2.5 states that the earlier 12-item instrument prepared on 30 July 2026 (`phase4_*`) was **never administered**; its answer fields are empty and it is retained only as part of the process record. |
| Expert 2's ratings are expert 1's with R08 changed; deposit the original or describe agreement as unverifiable | Closed (disclosed) | The original form cannot be deposited because it does not exist in the record. §2.5, §3.8 and §3.9 state that expert 2's ratings were transcribed by the corresponding author from written responses, that the original is not deposited, and that **the inter-rater statistics involving expert 2 cannot be independently verified from the deposit**. The 0.840 figure is reported with that caveat. |
| "Cannot be statistically distinguished from chance" confuses agreement with direction | Closed | The phrase is removed. §3.8 now says the near-zero unweighted agreement is descriptive, while the one-directional pattern (8 of 12 lower for each expert) is the finding, explicitly limited to 12 purposively selected cases. |

### A4. Archive: DOI tag pointed to the wrong commit; archived copies were pre-correction drafts; files only on main

| Sub-point | Status | Change |
|---|---|---|
| DOI tag points to 40bf1f8, not ea7b679; archived manuscript/supplement are earlier drafts | Closed | A new release was archived from the current tree and a new version DOI issued (v2.0). The manuscript now cites the **concept DOI 10.5281/zenodo.23143344**, which resolves to the latest archived version, plus the release tag. The archive toggle had been off, which is why the earlier release never reached Zenodo; it is now enabled. |
| `audit_set_design.json`, `rule_gating_experiment.py`, `audit_manuscript.py` only on main; `assemble_submission_pkg.py` in neither | Closed | All four are now inside the released tag (verified by HTTP HEAD against the tagged tree). `assemble_submission_pkg.py` was added to the repository and to the deposit. |
| Regeneration scripts read `outputs/` paths absent from the release | Closed | `scripts/deposit_paths.py` resolves every read path against both layouts; every reproduction script was re-run from a fresh clone of the release. |
| `stats_tests.py` self-test compares corrected McNemar results with round-two p-values | Closed | The self-test now compares against the values in the current manuscript (4.4e-14, 7.4e-14, 2.1e-5). |
| README gives 20 × 37 matrix and audit sensitivity 0.440 | Closed | README updated to 21 × 40 (34 columns in use, 104 cells), 0.674 audit accuracy, 0.320 audit sensitivity, and the corrected 113/232 registry counts. |
| `pyproject.toml` omits scipy and rank-bm25 and pins nothing | Closed | Both declared; core dependencies pinned to the versions used (`pydantic 2.13.4`, `pandas 2.3.3`, `scikit-learn 1.9.0`, `scipy 1.17.1`, `rank-bm25 0.2.2`). `requirements.txt` matches. |
| Gold files carry one pooled provenance string; no manifest or fingerprints; REPORT.md fingerprints do not match | Closed | Per-case provenance files added for the L1 set (`data/gold/l1_gold_provenance.csv`), the audit set (`audit_gold_provenance.csv`) and the development set (`dev_ddinter_gold_provenance.csv`), plus case-level `provenance` objects in the remaining gold files. A repository-root `MANIFEST.sha256` lists LF-normalised SHA-256 values for engine, rules, matrix, registries, evidence, gold and the index build record (`data/evidence/index_manifest.json`). `REPORT.md` fingerprints were recomputed and a note explains CRLF vs LF hashes. |
| Zenodo record licensed CC BY-NC-SA 4.0 while the manuscript says Apache-2.0 and CC BY 4.0 | Closed (explained) | The archive remains CC BY-NC-SA 4.0 because it bundles the DDInter severity tables, which are third-party data under those terms. The Availability statement now states this explicitly, alongside Apache-2.0 for code and CC BY 4.0 for original data. |

### A5. Other open items

| Sub-point | Status | Change |
|---|---|---|
| Table S1 still lists ten disagreements | Closed | Table S1 now lists **eleven** (ten guideline-sourced plus C04 flurbiprofen × warfarin), and its note no longer says the frozen subset was perfect. |
| Section 4.1 still claims cascade leadership and restates the withdrawn inference | Closed | §4.1 now says the cascade led on exact accuracy and specificity **within the primary 10-token protocol**, with the range 0.535–0.630 (including pure_llm), and notes the adequate-budget baseline that exceeded it and the leak-excluded comparison. |
| BM25 query lacks drug names | Closed | §2.4 now prints the query as `f"{a} {b} ophthalmic interaction"` and states that it includes the drug names; `audit_manuscript.py` checks code and text agree. |
| Reasoning-effort setting unstated | Closed | §2.4 and Supplementary Text S3 state that reasoning effort was **not set**; only `max_tokens` and `temperature` are sent, so the endpoint default applied. |
| No tie ever arose | Closed | §2.4 and Text S3 state that in every case at least three of five samples agreed, so the majority rule never encountered a tie. |
| README outdated | Closed | See A4. |

---

## Part B — Reviewer 1

### B1. Ethics and consent

All sub-points are addressed by the changes in A1: committee named and no determination claimed; consent process stated as undocumented; the overlap disclosed; "independent" qualified wherever it describes the experts; the editor-addressed sentence removed; the consent-for-publication statement made consistent. The reviewer's specific observation that K202509-29 names Yi Xianglong as principal investigator is now reflected in the Ethics declaration, which states that one expert is a member of the research team of that separately approved study, and that K202509-29 does not cover the present work.

### B2. The errata cases are in the frozen blind subset

Addressed by A2. The requested dates are given, R10/R11 are explicitly identified as frozen-subset cases (B18/C20), the both-way numbers are reported, and the errata table's first column has been **renamed** from "DDInter original" to "pre-correction gold (earlier round)", with a separate "DDInter severity" column — which now shows the R03 discrepancy correctly (pre-correction gold low; DDInter medium). The engine-change date is stated (23 September 2026) together with the finding that no level changed.

### B3. The expert section

Addressed by A3. In addition, the reviewer's own correction is answered directly in the text: **the engine returned low for R10 and R11**, so the round-three premise was indeed wrong; §3.8 says so and Table 6's note no longer repeats it. The expert-versus-gold counts are corrected to 4/12 and 3/12, the expert-versus-displayed counts to 2/12 and 1/12, and the lower rating counts to 8 of 12 for each expert against the gold.

### B4. The archive

Addressed by A4.

### B5. Values and text not updated

| Sub-point | Status |
|---|---|
| Table S1 ten disagreements / frozen subset perfect / flurbiprofen missing | Closed — eleven rows, note rewritten |
| §3.7 lightrag 0.720–0.771 (SD 0.018) | Closed — 0.712–0.771 (SD 0.020); audit-set SD range 0.005–0.039 |
| §4.1 cascade leadership / withdrawn inference | Closed — qualified to the 10-token protocol, range includes pure_llm |
| §2.4 BM25 query text | Closed |
| §2.4 / Text S3 reasoning effort | Closed |
| No tie arose | Closed |
| §4.4 points to a tier cross-tabulation in §3.4 | Closed — now points to Supplementary Table S5 |
| Text S6 points Limitations to §3.8 | Closed — now §3.9 and §4.4 |
| §2.1 "independent two-expert clinical assessment" | Closed — "two-expert clinical grade review — a perspective comparison rather than an independent assessment" |
| Generative AI "sole human validation channel" | Closed — removed; the 20-label expert-informed provenance is now disclosed |

### B6. The audit-set gold rule and the leakage

| Sub-point | Status |
|---|---|
| D3-057 and D3-063 corrected although the cascade reaches them through a rule | Closed (disclosed) — §2.3 lists all seven rule-hit exceptions; both readings reported |
| Two aflibercept pairs (tier minimal) kept at DDInter | Closed (disclosed) — listed as a deviation from the stated rule |
| Four flurbiprofen pairs kept under the superseded high tier | Closed (disclosed) — the design-file lock predates the tier correction; stated explicitly |
| State the rule as applied, or re-derive the gold, and report both | Closed — §2.3 states the rule as applied and as implemented; `scripts/rederive_audit_gold.py` re-derives it under the stated rule with current tiers; 10 of 92 labels change; cascade 62/92 (0.674) under the applied gold and 60/92 (0.652) under the re-derived gold |
| Leakage: report the comparison with leaked cases excluded beside §3.6 and in the Abstract | Closed — §3.5 and §3.6 report naive_rag 24/26 on leaked cases, **43/66 (0.652) on the remaining cases**, identical to pure_llm, against 47/66 (0.712) for the cascade; high-risk sensitivity 9/10 on leaked cases versus 1/15 on the rest. The Abstract reports the same comparison. |

### B7. Smaller points

| Sub-point | Status |
|---|---|
| Figure 1 produced with an image-generation tool | Closed — Figure 1 and all other figures are now drawn with Matplotlib (`scripts/draw_figure1.py`); no AI image tool was used. The Generative AI statement says so. |
| [N1] and [N2] are unresolved markers; details wrong | Closed — renumbered [41] and [42]; Korte et al. corrected to "0.5% timolol eyedrops"; DDInter 2.0 corrected to Tian Y, Yi J, Wang N, Wu C, Peng J, Liu S, et al., *Nucleic Acids Research* 2024, per Crossref. |
| Cite Korte for the claim itself, not in a note about an earlier version | Closed — the parenthetical about an earlier version was deleted; Korte is now cited directly for the systemic-bioavailability measurement. |
| Move every note on earlier versions to the letter | Closed — the remaining "earlier version" notes were removed from the manuscript, Table 6, Supplementary Table S3 and the figure legends. |
| Figure 1 prompt said to be archived as figure_prompts.md, not found | Closed — the prompt claim was removed with the AI-generated figure. |
| Initials convention inconsistent ("GW" vs "YX", "HL", "WS") | Closed — all are now family name + given-name initial: WG, YX, HL, WS. |
| Add gold annotation to Yi X's contributions | Closed — "Data curation (gold-label annotation, Section 2.3)" added to the Authors' contributions. |

---

## Part C — What remains open, and why

Three points cannot be fully closed with the existing record. They are stated in the manuscript rather than smoothed over:

1. **The ethics committee determination.** No determination covering the professional-opinion exercise was ever requested. The manuscript names the committee and states that no determination was issued. Obtaining a retrospective written determination and an English translation would close this point; it is an institutional action, not a text edit.
2. **Expert 2's original questionnaire.** It is not in the record. The manuscript describes the inter-rater statistics involving expert 2 as unverifiable from the deposit. If the form can be located and scanned, this becomes a closed point.
3. **The identity and approval basis of the "T1" exercise.** The deposit does not name the clinician and no separate approval or consent record exists. The manuscript discloses the exercise, the five labels that follow it, and the limit of what can be established.

Everything else in the final decision is closed by a change in the manuscript, a change in the deposited code, or both.

---

## Part D — Where each change can be verified

| Artefact | Location |
|---|---|
| Revised manuscript | `manuscript/manuscript.md`, `.docx`, `.pdf` |
| Marked-changes copy | `manuscript/manuscript_marked_changes.docx` (changes from the round-2 submitted text marked in red) |
| Supplementary material | `supplementary/Supplementary_Material.docx` (Texts S1–S7, Tables S1–S8) |
| Expert statistics (recomputed) | `scripts/expert_review_analysis.py` → `audits/recomputed/expert_review_recomputed.json` |
| Corrected kappa implementation and regression test | `scripts/stats_tests.py`, `tests/test_stats_kappa.py` |
| Re-derived audit gold | `scripts/rederive_audit_gold.py` → `audits/recomputed/audit_gold_rederived.json` |
| Per-case gold provenance | `data/gold/l1_gold_provenance.csv`, `audit_gold_provenance.csv`, `dev_ddinter_gold_provenance.csv` |
| Fingerprints and manifest | `MANIFEST.sha256`, `data/evidence/index_manifest.json`, `data/predictions/REPORT.md` |
| Manuscript consistency audit | `scripts/audit_manuscript.py` (0 FAIL) |
| Figures and source data | `figures/figure1_architecture.*`, `figure3_expert_agreement.*`, `figures/source_data/` |
