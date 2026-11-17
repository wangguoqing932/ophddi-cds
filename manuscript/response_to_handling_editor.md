# Response to the Handling Editor

**Manuscript:** 2032864 — OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening  
**Journal:** Frontiers in Pharmacology — Drugs Outcomes Research and Policies  
**Date:** 18 November 2026

Dear Dr. Huang,

Thank you for the careful editorial check and for identifying these inconsistencies. We have addressed all six points. No new experiments were required; the changes are corrections of reporting, documentation and metadata.

## 1. Inconsistent percentages for DDI severity downgrading

The 75.3% and 80.5% values in the previous Scope Statement were from the pre-revision analysis. The final analysis, after the absorption-tier and label corrections, gives:

- **1,502 of 1,933 graded-severity pairs (77.7%)** graded lower;
- **1,341 of 1,757 assessed pairs (76.3%)**;
- **1,206 of 1,502 downgrades (80.3%)** involving low-tier ophthalmic agents.

The Scope Statement has been rebuilt and now reports 77.7% and 80.3%, matching the Abstract, Section 3.4 and Conclusions. The old values no longer appear as current results; they are retained only where this letter quotes the prior values to explain the correction.

## 2. Discrepancies between the manuscript and the public repository

The repository README and release notes have been rewritten for the current Frontiers submission. They now report:

- **101/118 (0.856; kappa 0.779)** under the frozen labels and **104/118 (0.881; kappa 0.818)** after the three post-lock corrections — not 107/118 or 0.857;
- **77.7%** downgrading and **80.3%** low-tier association — not 75.3% or 80.5%;
- the current deposit as **v3.0-frontiers** (DOI 10.5281/zenodo.23439606), with the earlier BMC-era package explicitly archived under `outputs/archive/bmc_submission/` and marked historical.

The corrected `README.md` and `RELEASE_NOTES.md` are provided as separate files in `repository_docs/` with this revision. The public repository has been synchronized to this release and verified file-by-file: all 690 final files matched the repository tree, with no missing or mismatched file. The manuscript and package values therefore correspond to the public release.

## 3. Inconsistency in the description of LLM comparisons

The Scope Statement now states that the two configurations differ **simultaneously in model, token allowance and sampling strategy**. Section 2.4 already states the same, and the Results describe them as two configurations rather than as an effect of output budget. The wording has been aligned across the Scope Statement, Section 2.4 and the Figure 2 legend.

## 4. Clarification of clinician participation and ethics documentation

The independent reviewer in Section 3.5 is a **third ophthalmologist**, not one of the two clinicians who rated the 12 cases in Section 2.5. This is now stated explicitly in Section 2.5.

The Ethics Statement now describes both human-participant components: the 12-case anonymous professional-opinion exercise and the 30-case anonymous independent review. It states that the independent reviewer is not an author, did not take part in the 12-case exercise, reviewed only the 30 disagreement cases using the drug pair, reference grade, system grade, absorption tier and direction, and collected no new data; the review did not constitute new human-subjects research. The reviewer is identified by a pseudonymous code in the supplement and named in the Acknowledgments as Dr. Zhouqi Guo (郭州岐). Neither activity involved patient data or identifiable personal information. Data availability includes the 30-case review record.

## 5. Consistency in reporting unassessed drug pairs

Section 3.4 now states explicitly that the 176 default-path pairs are labelled `unassessed` in the output and in Figure 6 and are referred for manual review; they are never presented as assessed low-risk pairs. This is consistent with Section 2.6, Table 6 and the intended workflow, which already distinguished unassessed from assessed low risk.

## 6. Administrative and affiliation inconsistencies

The author-affiliation numbering has been unified as:

- **¹** Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University — Wang Guoqing, Hu Lumei, Yi Xianglong;
- **²** Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital — Wang Shaocheng;
- **³** Xinjiang Medical University — Yi Xianglong.

The author line is now Wang Guoqing, M.D.¹; Hu Lumei, M.M.¹; Wang Shaocheng, B.M.²; Yi Xianglong, M.D., Ph.D.¹³*. The manuscript title page and the local submission status table have been aligned to this numbering and these degrees; the submission record will be updated to the same numbering and degrees before upload. The repository no longer describes the project as a BMC Bioinformatics submission; the BMC-era files are archived and marked historical.

We hope these corrections resolve the remaining editorial points. We would be glad to make any further consistency correction if needed.

With respectful regards,

Xianglong Yi, on behalf of all authors
