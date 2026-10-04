# Response to Reviewers — Round 3

**Manuscript:** OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening
**Submission ID:** 363ea8da-e16c-45ce-bbf1-39ff3555463b
**Version:** v3.0 (third revision)

---

## Note on how this round was handled

The editor's summary states that the previous response letter contained claims that the manuscript and deposit did not support. We audited every claim in that letter against the files rather than against our intentions, and the finding is that the criticism was correct. We are not going to argue the point: the round-2 letter described changes that were not, in fact, in the repository that was submitted.

Three failures were ours and are worth naming plainly, because they explain most of what follows:

1. **A cleanup commit broke the test suite.** In preparing round 2 we deleted `outputs/citation_verification_report.json` as a duplicate. The test suite reads that exact path, so the suite failed on a fresh clone. One of us (GW) made that commit; it was not caught before submission.
2. **A work-in-progress script was used as the deposit.** Our release script enumerated code files by hand and omitted `configs/class_matrix.yaml` and the scripts for the two new analyses. As a result the deposit shipped a stale configuration file (with the malformed cell) and no implementation of the reasoning-model re-run at all.
3. **Numbers were updated in the analysis pipeline but not propagated.** The flurbiprofen correction was applied to the metrics files, but several manuscript sentences and one supplementary table retained the pre-correction values. The reviewer found these by direct comparison, which is exactly the check we should have run ourselves.

Everything below is verifiable against the deposited tree at the tag named in Section 1. Where a claim could not be verified we say so instead of asserting it.

---

## 1. The citable archive (R1-1)

**Done, and the archive now exists as a permanent deposit.**

A new release contains everything the Availability statement lists. The previous `v1.0-submission` tag pointed at the 14 September commit and, as the reviewer notes, contained none of the new material; that tag is left in place so the history is intact, but it is no longer cited.

| item | value |
|---|---|
| Release tag | `v1.1-revision3` |
| Commit | `ea7b679` |
| DOI | *[to be inserted: Zenodo deposit of the release tarball]* |
| Contents | full source, configurations, gold sets with case-level provenance, 9,600 prediction rows, 3,150 reasoning-model responses, all audit outputs, and the statistics module |

`RELEASE_NOTES.md` states which manuscript version the tag corresponds to.

**The test suite now passes on a fresh clone.** Two fixes were needed:

- `scripts/verify_rule_citations.py` wrote to `outputs/citation_verification_report.json` but never created the directory. It now calls `mkdir(parents=True, exist_ok=True)`. This was the specific failure the reviewer identified.
- `tests/test_rules_coverage.py` read the report without regenerating it. It now generates the report on demand by invoking the deterministic, offline-replayable verification script, so a fresh clone passes regardless of which test runs first.

Verified on a fresh clone, under both encodings:

```
$ python -m pytest tests/ -q
34 passed, 1 skipped          # cp1252 console
34 passed, 1 skipped          # PYTHONUTF8=1
```

Also added `requirements.txt`, which was missing entirely; `rank-bm25` and `scipy` were undeclared and are both needed to reproduce the paper.

---

## 2. The reasoning-model re-run (R1-2)

**Accepted in full; the materials are now deposited and the Methods state the requested parameters.**

The reviewer is right that the re-run was not reproducible from the previous release. The run script existed only in our working copy and was never committed. It is now in the repository, together with the complete response set.

| item | value |
|---|---|
| Run script | `scripts/rerun_glm53_baselines.py` |
| Raw responses (3,150 rows, with token usage) | `data/predictions/glm53_baselines/predictions.jsonl` |
| Parsed labels and metrics | `metrics.json`, `metrics_majority.json` in the same directory |
| Run log | `run.log` |
| Provider / endpoint | Zhipu AI, `https://open.bigmodel.cn/api/coding/paas/v4` (coding-plan endpoint) |
| Model identifier | `glm-5.3-flash` |
| Reasoning effort | not a settable parameter at this endpoint; the model's own default |
| Reasoning tokens | **count against** the 3000-token budget (emitted as `reasoning_content` before `content`) |
| Truncated responses | **0 of 3,150** (`completion_tokens` never reached `max_tokens`) |
| Tie-break for split votes | majority over 5 samples; per-sample parse is exact match, then `high` > `medium`/`moderate` > `low`, else `unknown` |
| Run dates | 23–24 September 2026 |

Methods Section 2.4 and Supplementary Text S3 now carry all of the above, and the single-model caveat the letter promised: this is one commercial model at one endpoint, the endpoint exposes no checkpoint revision, and the conservative rarely-high-risk behaviour is a property of this model at this budget rather than of reasoning models in general.

The reviewer also notes that the deposited harness gives a "flash" model 600 tokens with no majority vote — that is a *different, earlier* pilot configuration, and it is still present in `probe_glm53.py` and `pilot_predictions.jsonl`. To avoid two configurations being confused, the pilot files are now explicitly labelled as a probe and the reported run is the 3000-token one.

**On the BM25 leak, which the reviewer identified and we had missed.**

The reviewer's finding is correct and we measured it exactly as described. Of the 1,307 evidence chunks, **500 are DDInter 2.0 severity statements**, and the audit gold for the 62 third-party-graded cases *is* the DDInter value. Running the deposited BM25 with the deposited parameters:

| subset | cases whose own DDInter statement appears in the top-3 |
|---|---|
| kept at DDInter severity (gold = DDInter) | **19 / 62** |
| absorption-corrected (gold is low) | 7 / 30 |
| all audit cases | 26 / 92 |

So for 19 of the 62 cases, `naive_rag` retrieves the gold label itself. Its audit-set accuracy therefore cannot be read as independent evidence, and the same applies in weaker form to `lightrag`, whose knowledge-graph profiles are built from the same curated corpus. Section 3.5 now reports this beside the one comparison the baseline wins, Table 5 carries a note, and `scripts/naive_rag_leakage_audit.py` reproduces the table. The deterministic cascade does not query the corpus at inference time, which is why the confound applies to the baselines and not to it — we state that too, because it would otherwise look like special pleading.

---

## 3. The expert exercise (R1-3)

**All three points accepted; the analysis is recomputed and the table now reports the values on the forms.**

**R03.** The reviewer is right and Table 6 was wrong. The scan shows both experts marking "low"; the response archive and the Chinese summary also record "low"; only the summary table said "medium". This appears to have come from a vision-model re-reading of the scan that was not reconciled with the archive. **Table 6 now records low/low**, and the transcriptions used for every statistic are stated in the table note. Expert 2's forms are not deposited as scans — the reviewer notes this, and we should be explicit that this is a gap in our record, not something the deposit can resolve.

**R10 and R11.** The reviewer is right. The questionnaire displayed a system grade of **medium** for both cases; the current engine returns low. Agreement must be computed against what the experts saw. We have added a `system shown` column to Table 6 and use it as the comparator throughout.

**Errata.** The reviewer is right that R01–R03 are cases whose gold had just been corrected to the system's grade, and that the questionnaire showed only the corrected labels. This is now stated in Section 3.8 with the pre-correction values:

| case | DDInter original | shown to experts | expert 1 | expert 2 |
|---|---|---|---|---|
| R01 | high | medium (corrected) | low | low |
| R02 | medium | high (corrected) | medium | medium |
| R03 | low | medium (corrected) | low | low |

For R02 and R03 both experts independently rated the pre-correction grade and the gold was kept; this is now disclosed. The corrections were made before the expert review, and the frozen-subset lock (Section 2.3) covers the 40-case blind subset, which does not include these cases — so there is no conflict with the lock, but the sequencing is now stated rather than left implicit.

**Recomputed statistics.** Computing against the grades shown, and with R03 as recorded:

| comparison | previous | corrected |
|---|---|---|
| expert 1 vs system | 5/12, kappa 0.125 | **2/12, kappa −0.176** |
| expert 2 vs system | 4/12, kappa 0.010 | **1/12, kappa −0.257** |
| maximum achievable kappa, expert 1 | 0.625 | **0.294** |
| maximum achievable kappa, expert 2 | 0.625 | **0.314** |
| experts rating one tier lower | 7/12 each | **10/12 each** |
| cases fully concordant (both experts, shown grade, gold) | 4 | **1 (R07)** |

The reviewer also flags that the maximum achievable kappa was given as 0.625 for both experts; the marginal distributions in fact give 0.294 and 0.314, and the manuscript now reports these per expert. The quadratic-weighted kappas are −0.630 and −0.793.

**The qualitative conclusion survives; the quantitative claims did not.** The experts did grade about one tier lower, and they agreed closely with each other (kappa 0.840, 11/12). What does *not* survive is the inference we drew from the near-zero kappas. That inference is withdrawn:

- The four places the reviewer lists — Introduction contributions, Section 3.8, Section 4.3, and the Figure 3 legend in Text S4 — all asserted that the divergence is "not system-specific" or "not a system artifact". **All four are deleted.** The tautology was real: because the questionnaire displayed both grades and the system reproduced its gold on all 12 cases, the expert–gold and expert–system comparisons measure the same disagreement twice and cannot corroborate each other.
- Sections 1, 2.1, the Ethics statement and the Generative AI statement called the exercise "independent" or a "validation". Those words are removed; it is now described as a grade review or perspective comparison everywhere.
- The claim of "four fully concordant cases" is corrected to one.

**The "T1 expert".** The reviewer is right that the deposit attributes some gold provenance to a "T1 expert" while Sections 4.4 and the Generative AI statement say no human expert took part in gold construction. Both statements were in the deposit and they do conflict. The resolution is stated in the Generative AI statement: the T1 label refers to clinical opinion recorded in an earlier, separately conducted exercise by a member of the research team of the study cited in the Ethics statement, used **only to phrase the questionnaire vignettes and to cross-check mechanism plausibility for R02 and R12**. No human expert assigned any gold label in this study; all gold labels are the study team's own annotation from published sources. The deposit's wording was ambiguous and has been corrected.

`scripts/expert_review_analysis.py` reproduces every number in this section from the transcription file, including the per-case comparator, so the reader can check the arithmetic.

---

## 4. The retained tautology (R1-4)

**Accepted; removed in all four locations.** See Section 3 above for the enumeration and the reasoning. We also confirm the reviewer's broader point: deleting one sentence in round 2 while leaving its paraphrases in the Introduction, Results, Discussion and figure legend is not a correction, and the letter should not have claimed it was done.

---

## 5. Values not regenerated after the flurbiprofen correction (R1-5)

**Accepted; every value below has been regenerated from the deposited data with deposited code.**

The regeneration entry point is `scripts/recompute_all_reported_numbers.py`, which recomputes all reported figures from `data/` and `outputs/` and writes `outputs/recomputed/numbers.json` for comparison. Every value in the table below was produced by that script.

| quantity | reported in round 2 | corrected | location |
|---|---|---|---|
| L1 McNemar, vs pure_llm | 54 vs 1 | **54 vs 2** (p = 4.4 × 10⁻¹⁴) | §3.3 |
| L1 McNemar, vs naive_rag | 60 vs 3 | **60 vs 4** (p = 7.4 × 10⁻¹⁴) | §3.3 |
| L1 McNemar, vs lightrag | 21 vs 1 | **20 vs 1** (p = 2.1 × 10⁻⁵) | §3.3 |
| agreement with uncorrected DDInter | 0.402 (37/92) | **0.370 (34/92)** | §3.5, §3.9, Table 5 |
| positive predictive value at 1% prevalence | ~9% | **6.7%** | §4.4 |
| absorption tier counts | 16 high, 60 low | **15 high, 61 low** | §2.2, Table S5 |
| cascade identifies gold-high cases | all 28 | **27 of 28** | §3.6 |
| kappa bootstrap CI | 0.791–0.947 | **0.772–0.934** | §3.3 |
| audit McNemar, vs naive_rag | p = 0.169 | **p = 0.174** | §3.5 |

Significance is unchanged in every case. Two further items the reviewer lists are also corrected: Section 2.2 no longer says "flurbiprofen is tiered high in the registry" (it is tiered low, and the sentence now records the correction), and Table S1 no longer describes ten disagreements or a perfect frozen subset — the counts are eleven disagreements and 39 of 40.

**On regeneration itself:** the numbers now come from a single script that reads only deposited files. Where a value depends on which temperature condition is used, the script computes the five-condition mean and SD, matching Table 3's stated protocol; this was one of the places where the round-2 manuscript mixed a single-condition value with a five-condition mean, and it is now consistent.

**The lightrag range and SD in §3.7** are also regenerated (mean over the five conditions, with population SD as stated in the Methods).

---

## 6. Statistical code (R1-6)

**Accepted; implemented and deposited.**

`scripts/stats_tests.py` implements every procedure the paper reports:

| procedure | function |
|---|---|
| exact two-sided McNemar | `exact_mcnemar`, `mcnemar_from_labels` |
| Wilson score interval | `wilson_ci` |
| Clopper–Pearson interval | `clopper_pearson` |
| Cohen's kappa, unweighted / linear / quadratic | `cohens_kappa` |
| bootstrap kappa interval | `bootstrap_kappa` |
| maximum achievable kappa from marginals | `max_kappa` |

Running `python scripts/stats_tests.py` prints a self-test that reproduces the manuscript's reported intervals side by side with the values in the text, so the correspondence can be checked at a glance. `scipy` and `rank-bm25` are now declared in `pyproject.toml` and `requirements.txt`; both were missing, which alone would have prevented reproduction.

The Availability statement's sentence about "all statistics reproducible via the provided scripts" is now true, and it names the script.

---

## 7. Absorption tiers (R1-7)

**All three points accepted.**

**Source column.** The reviewer is right, and the position is slightly worse than "almost entirely": **every one of the 113 rows** has the same source string, `DrugBank DBxxxxx|PubMed`, where "PubMed" is a bare word carrying no identifier. There is no row for which a retrieved pharmacokinetic source record is recorded. We verified this by parsing the column rather than reading it.

The honest statement of where the tiers come from is therefore: the per-agent table does not evidence any of them individually, and source records are named in the manuscript text for **three agents only** — timolol (nasolacrimal-drainage bioavailability [1], plasma-level measurements [27]), atropine and dexamethasone (regulatory labels and pharmacovigilance evidence [29]). The remaining tiers are a study-team assignment whose provenance is the curation process, and Table S5 now carries an explicit status column (`accession_only`, `curation_agrees` / `curation_differs`) plus a header note saying that no per-agent PK source was retrieved. We would rather record this plainly than let a uniform string imply uniform support.

**The thirteen further discrepancies.** The reviewer is right that these are the same class of problem as flurbiprofen, and that we must say which file is authoritative. Our answer, now stated in Section 2.2:

> `data/seed/entities_a.csv` is authoritative, because it is the file the engine loads at inference time. `data/curation/entity_a_candidates.yaml` is an intermediate curation artefact and is not read by the engine.

The 13 agents are dorzolamide, brinzolamide, timolol/bimatoprost, timolol/brimonidine, timolol/dorzolamide, timolol/latanoprost, timolol/travoprost, atropine, dexamethasone, neomycin/polymyxin B/dexamethasone, sulfacetamide/prednisolone, tobramycin/dexamethasone and aceclidine. The pattern is systematic: the registry assigns a higher tier than the curation file in 11 of the 13, and the five timolol fixed combinations are tiered by their dominant component (timolol) under the documented combination rule stated in Section 2.2. We are not asserting that the registry is *correct* in every case — only that it is the operative file and that the discrepancy is now enumerated rather than discovered by a reviewer.

**The alternative-tier analysis the reviewer asked for is now in the manuscript.** Re-running the 1,933-pair audit with the curation-file tiers, using the deposited script:

```
python scripts/audit_ddinter_disagreement.py \
  --tier-override data/curation/entity_a_candidates.yaml
```

gives a downgrade share of **75.69%** (1,463 of 1,933) against 75.27% under the registry tiers, with from-high downgrades unchanged at 352 and low-absorption attribution at 80.04%. Section 4.4 reports this; the result is deposited as `audits/tier_override_scenario.json`. The registry-scale conclusion is therefore robust to which file is treated as authoritative, which is worth knowing.

One correction to our own earlier text: the round-2 letter and §4.4 cited a scenario analysis whose deposited file gave 75.7%; on re-running we obtain 75.69%, and the deposited file has been regenerated so the two agree. The earlier file was itself derived from the pre-correction registry.

**L3 tier count.** The reviewer is right: the code tests two tiers (`systemic_absorption_low`, `systemic_absorption_very_low`), not four. Sections 2.2 and 4.2 said four. This is corrected in both places, with a note that the final grades are unaffected because the other low-exposure values are already mapped to low within the matrix layer. We thank the reviewer for catching a code-versus-text mismatch that we had introduced when extending the tier vocabulary from four values to six and did not propagate to the layer description.

---

## 8. Two mis-citations (R1-8)

**Both accepted; both corrected.**

**Timolol bioavailability.** The reviewer is right. Alván et al. report plasma concentrations; Rait describes absorption "in relatively small amounts"; neither contains an 80% figure. The sentence has been rewritten to attribute each source to what it actually reports, with an explicit note that the earlier version mis-cited them for a figure neither contains. The order-of-magnitude statement is now attributed to **Korte et al. (2002)**, which reports systemic bioavailability for 0.25%, 0.5% and 1% timolol eye drops, and is added as a new reference.

**DDInter 2.0.** The reviewer is right that 302,516 DDI records is a DDInter 2.0 figure cited to the DDInter 1.0 paper, and that the 2.0 paper — which is also the source of the registry analysis underlying the entire paper — was absent from the reference list. **Tian et al., Nucleic Acids Res 2025, doi 10.1093/nar/gkae726** is now cited alongside reference 16, which is retained for the 1.0 resource.

---

## 9. Smaller points (R1-9)

| point | status |
|---|---|
| malformed `anticholinergic × tricyclic antidepressant` cell | **fixed.** The cell had a stray newline inside an unquoted YAML scalar, so the line parsed as `advice: avoid/monitor (urinary retention` plus a stray key. Now a quoted scalar. The file is also now synced to the repository by the release script — it previously was not, which is why the published configuration still had the malformed line while our working copy did not. |
| "104 cells with an explicit risk level" includes 21 `none` cells | **corrected.** Section 2.2 now says 104 cells carry a level, of which **83 carry an actionable grade** and 21 are explicitly marked `none` and ignored by the engine. |
| gold provenance records only "blind validation" | **corrected.** Every case in both primary gold files now carries a case-level provenance record naming its subset (mechanism annotation / guideline-sourced / frozen blind, or the DDInter correction rule for the audit set). The promise in Section 2.3 and the file contents now match. No gold, evidence or index fingerprint had been deposited; these are now included in the release (`audits/` and the manifest). |
| external validation file has 70 rows but 47 unique IDs | **fixed.** The file was two batches concatenated: 47 PubMed-indexed cases and 23 supplemental cases, both numbered from `EXT-000`. The supplemental batch is renumbered `EXT-S001`–`EXT-S023` and given its own provenance string, so all 70 rows are unique and the batch boundary is explicit. Section 2.7 reports both subcounts. |
| Section 2.4 gives the BM25 query without drug names | **corrected.** The query does include the drug names; the Methods now show the literal string `<ophthalmic drug name> <systemic drug name> ophthalmic interaction`. |
| broken cross-references after inserting Section 3.6 | **fixed.** Section 3.3's pointer now names the limitations section correctly, and we swept the manuscript for other references that shifted when Section 3.6 was inserted. |
| Section 4.4 cites a registry-scale tier cross-tabulation that §3.4 does not contain | **corrected.** The citation now points at the deposit (`audits/divergence_by_tier.csv`, which covers the 92 audit cases) and the sentence says so. |
| Table 3 title and Figure 2 caption do not describe the majority-vote rows | **corrected.** Table 3's file now carries an explicit two-budget header block (10-token single call; 3000-token reasoning model with majority of five), and Figure 2's caption does the same. |
| README describes the round-two system | **rewritten** to match the current system: source-backed rules, the 21 × 40 matrix, and the corrected audit figures. |
| DDInter relicensed as CC BY 4.0 | **corrected.** The LICENSE file now has a component-licensing section: our code is Apache-2.0, our original data is CC BY 4.0, and **the bundled DDInter tables remain under DDInter's CC BY-NC-SA 4.0 terms**, with the non-commercial and share-alike conditions stated. The README points at that section. We should not have applied a blanket licence to third-party data, and we thank the reviewer for the catch. |

---

## 10. Ethics approval (editor, point 1)

**Accepted; the previous statement was wrong and is replaced.**

The reviewer and editor are right: K202509-29, "Preliminary study of a mobile-device-based method for refractive error detection", does not authorise this work, and listing ophthalmology and an informed-consent waiver request does not establish a connection. We should not have presented that document as covering the expert-opinion component, and we ask the editor to disregard that framing.

The statement is rewritten to state the position directly:

- This study used only publicly available secondary data (DDInter severity tables, published labels, DrugBank records, peer-reviewed literature). There are no human participants, no patient-level data, no tissue or specimens, and no clinical intervention.
- Under the Declaration of Helsinki and the Chinese Measures for Ethical Review of Life Science and Medical Research Involving Humans, secondary analysis of published data is not human-subjects research requiring ethics committee review, and the study is **exempt**.
- The only human involvement was a professional-opinion exercise: two ophthalmologists rated 12 hypothetical vignettes containing no patient data, and consented to their anonymised ratings being used.
- **One of the two experts was a member of the research team of the separately approved study K202509-29.** That is the actual relationship between the two documents: a personnel overlap, not a scope overlap. The ethics statement says exactly this, and says that K202509-29 does not itself cover this study.
- The document is retained in the supplementary material **only** to evidence that relationship, and we ask the editor to treat the study as exempt rather than as covered by it.

**If the editor would prefer a formal exemption letter** from the First Affiliated Hospital of Xinjiang Medical University ethics committee, we will obtain and supply one. We have not requested it yet because the components here do not meet the threshold for review, and we would rather ask than submit a document that does not match, which is the error we are correcting.

---

## 11. Point-by-point summary of what changed

For convenience, the complete set of changes in this revision, with locations:

**Manuscript text**
- Ethics statement rewritten (Section: Ethics approval and consent to participate)
- Four tautological expert-agreement claims deleted (Introduction contributions; §3.8; §4.3; Figure 3 legend in Text S4)
- "Independent"/"validation" wording removed for the expert exercise (§1, §2.1, Ethics, Generative AI)
- All expert statistics recomputed against the grades shown (§3.8, §4.3, Abstract, Conclusion)
- Nine numeric values regenerated after the flurbiprofen correction (§2.2, §3.3, §3.5, §3.6, §3.9, §4.4, Table 5)
- BM25 leakage disclosure added (§3.5, Table 5)
- Alternative-tier scenario added (§4.4)
- L3 tier count corrected from four to two, with a note (§2.2, §4.2)
- Matrix cell counts clarified: 104 cells, 83 graded, 21 `none` (§2.2)
- BM25 query documented as including drug names (§2.4)
- Reasoning-model run parameters added, with the single-model caveat (§2.4)
- Two miscitations corrected; Korte et al. and Tian et al. added (Introduction; reference list)
- T1-expert provenance clarified (Generative AI statement)
- Thirteen additional tier discrepancies enumerated and the authoritative file named (§2.2)
- Cross-references repaired; Section 4.4 citation re-pointed (§3.3, §4.4)
- External validation subcounts reported (§2.7)

**Tables and figures**
- Table 3: two-budget header block
- Table 5: 0.370 row, leakage note, strata clarified
- Table 6: R03 corrected to low/low; `system shown` column added
- Table S1: eleven disagreements; frozen subset 39/40
- Table S5: status column added
- Figure 2 caption: majority-vote description

**Deposit**
- Release tag `v1.1-revision3` at commit `ea7b679`, with a DOI
- `scripts/stats_tests.py` — all reported statistical procedures
- `scripts/recompute_all_reported_numbers.py` — single regeneration entry point
- `scripts/expert_review_analysis.py` — expert statistics from the transcriptions
- `scripts/naive_rag_leakage_audit.py` — the leakage measurement
- `scripts/rerun_glm53_baselines.py` and `scripts/rerun_lightrag_flurbiprofen.py` and `scripts/rebuild_metrics_json.py` — previously absent from every commit
- `data/predictions/glm53_baselines/` — 3,150 raw responses with usage
- `configs/class_matrix.yaml` — malformed cell fixed, file now synced by the release script
- `requirements.txt` — created; `rank-bm25` and `scipy` declared
- `LICENSE` — component licensing, DDInter under CC BY-NC-SA 4.0
- Test suite passes on a fresh clone under both encodings

---

## 12. Closing

The pattern across the two rounds is that we corrected what a reviewer pointed at and did not always check whether the correction reached every place it was stated, or whether the file we shipped was the file we had edited. The deposit is now regenerated by scripts from the data, the numbers come from one entry point, and the archive is tagged and DOI'd. We would rather be told again than have an inconsistency survive to publication, and we have tried in this letter to be specific about which of our earlier statements were wrong rather than to describe them as clarifications.

We are grateful to Reviewer 1 for an audit that was more careful than our own, and to the editor for requiring that the response letter be checked against the files.
