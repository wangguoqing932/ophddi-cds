# Response to Reviewers and Editor

**Manuscript ID:** 363ea8da-e16c-45ce-bbf1-39ff3555463b

**Title:** OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug–Drug Interaction Screening

**Authors:** Wang Guoqing, M.D.; Yi Xianglong, M.D., Ph.D. (corresponding)

**Decision:** Revise

---

Dear Dr Shelke and Dr Parikesit,

We thank the editor for a careful assessment that identified three concrete,
actionable gaps. All three have been addressed, and the manuscript has also been
revised in line with the general guidance to report results accurately, remove
overstated conclusions, and explain limitations fully. Below we respond point by
point; the changes are marked in the revised manuscript.

We also record one change to the framing of the paper, made in response to the
editorial guidance about overstated conclusions. It is described under "Changes to
framing and claims" below, because it affects the abstract and conclusion and we
want the reviewers to be able to assess it deliberately.

---

## Editor comment 1 — Source code must be deposited in an open repository

> *"After I did thorough examination of the manuscript, including on the
> suplementary material, I can't find any pointers to the source code repository.
> So it is not feasible on my end to repeat the computational procedure.
> Therefore, the source code of the computational procedure should be deposited in
> the Github or similar open source repository, so repeatability is possible."*

**Accepted in full.** The editor is right, and the omission was ours: the previous
submission described a "downloadable release package" as supplementary material
without ever pointing to a public, versioned repository. The complete source code is
now deposited at:

> **https://github.com/wangguoqing932/ophddi-cds** (public; accessible without a GitHub account)

The repository contains the production screening engine, the curated knowledge base,
the rule-citation verification tooling, the evaluation scripts, and a test suite. As
requested, the deposited code is complete and runnable, not a stub:

| Component | Contents |
|---|---|
| `src/ophthalmic_ddi_cds_agent/` | Screening engine, registry layer, rule matcher, citation sources |
| `configs/` | `rules.yaml` (40 rules + 3 patient-factor policies), `class_matrix.yaml`, `drug_classes.yaml`, `flag_catalog.yaml` |
| `data/curation/` | Candidate registries and the rule-to-citation map |
| `data/raw/evidence/citations/` | Cached Crossref / OpenAlex / PubMed responses, so citation verification replays **offline** |
| `scripts/` | Demo, evaluation, and build scripts |
| `tests/` | Test suite — **34 passed, 1 skipped** |

We verified the deposit the way a reviewer would: cloning the public repository into a
clean directory and running it there, rather than testing only in our own working copy.
The clone produced 96 files and the demonstration completed with all 25 mock cases
reproducing their expected risk level.

Every number in the manuscript is reproducible from this deposit. The deterministic
cascade described in the paper — which is the contribution — requires no API key and
no network access, so the editor can reproduce the system's own results directly. The
LLM-baseline comparisons are also included but require the reviewer to supply their
own model API credentials; this is stated in the repository README rather than left
implicit.

## Editor comment 2 — Deposit mock-up data so the pipeline can be inspected

> *"Pertaining the data, you don't need to deposited your computed data in the
> repository, and you can proceed by depositing mock up data. So the reviewer can
> really check whether your pipeline is working or not. Real data could be deposited
> later, if this manuscript is accepted."*

**Accepted.** The repository ships a self-contained mock dataset and a single command
that exercises the full pipeline:

```bash
python scripts/demo_pipeline.py
```

This runs 25 drug pairs through the production cascade with no API key and no network
access, and checks each returned risk level against the value frozen at release. The
mock set deliberately covers all three decision paths the paper describes — rule
match (13 cases), class-matrix match (11 cases), and the unknown-drug fail-safe path
(1 case) — so a reviewer can confirm not only that the code runs but that the three
documented layers each behave as claimed. The command also verifies the fail-safe
property asserted in Section 2.2: a medication outside the registry returns an
explicit unknown-drug path and receives **no** risk grade, rather than a default.

```
25/25 mock cases reproduced their expected level
PASS: no risk grade is assigned to an unknown drug
All checks passed.
```

`data/mock/mock_evidence_chunks.jsonl` provides eight illustrative evidence passages
for the retrieval path. These are explicitly labelled `mock-synthetic` in the file and
in the README — they are written for the repository and are **not real citations** — so
that no reader mistakes demonstration text for evidence.

We note for transparency that the two entity registries (`data/seed/entities_a.csv`,
`entities_b.csv`) are deposited as **real** data rather than mock, because they contain
only drug names, drug classes, mechanism flags and absorption tiers — no patient data
and no personal information. Depositing the real registries means the demo runs against
the same 113 × 232 agent set used in the manuscript, which we judged more useful to a
reviewer than a synthetic registry. We will of course replace them with mock registries
if the editor prefers.

## Editor comment 3 — Ethics waiver opinion must appear in the ethics statement

> *"As this manuscript involves expert opinion from health care professionals, waiver
> opinion for the ethics approval should be provided in the ethics statement."*

**Accepted, and the statement has been rewritten.** The previous version stated merely
that "ethics approval was not required for this study design under applicable
institutional policy" and offered a waiver "on request" — which is exactly the
weakness the editor identified. The revised statement now sets out the basis for the
waiver explicitly:

> This study did not involve human participants, human tissue, patient data, or
> clinical interventions. The only human involvement was an expert-opinion exercise in
> which two ophthalmologists independently rated 12 hypothetical drug-pair vignettes
> constructed by the study team; no identifiable information was collected, and both
> experts provided informed consent for their anonymised ratings to be used in research
> and publication. Under the policy of the Ethics Committee of the First Affiliated
> Hospital of Xinjiang Medical University, a study of this type (expert opinion on
> hypothetical vignettes, with no human participants and no identifiable data) does not
> require full ethics review; a formal waiver opinion has been requested from the
> committee and is provided as supplementary material. The work was conducted in
> accordance with the Declaration of Helsinki.

We have also added the two other missing elements the journal requires in this section:
a `Consent for publication` subheading ("Not applicable — this study did not involve
data from any individual person") and an `Acknowledgements` subheading.

*Note to the editor, should it be useful:* the study described here is distinct from
the expert-opinion exercise, so no approval number for a separate protocol is cited in
the ethics statement. The waiver is documented on the basis of the study design
described above.

---

## Changes to framing and claims (editorial guidance)

The editor asked that results be reported accurately, overstated conclusions rewritten,
and limitations fully explained. Reviewing the manuscript against its own evidence, we
found that the weakest-supported claim was the one leading the paper, and we have
restructured accordingly. No data, analysis, or number has changed; the framing has.

**What changed.**

1. **The abstract no longer leads with the 0.915 accuracy figure.** That figure measures
   agreement with a gold standard that the authors themselves constructed from the same
   literature sources that informed the rules — a homogeneous construction we already
   disclosed. It is now reported as what it is, the internal consistency of an
   explicitly evidence-graded encoding, and the paper's opening claim is instead the
   measurement that does not depend on the gold at all: across all 1,933 registry-matched
   DDInter pairs, absorption-aware assessment grades 75.0% of pairs lower, with 77.0% of
   that shift attributable to a single mechanism, low systemic absorption from the
   topical route.

2. **That registry-scale audit has been promoted to its own Results subsection and moved
   ahead of the gold-dependent audit.** It is now presented as the primary quantitative
   finding, with its two boundary conditions stated in the Results rather than deferred:
   it quantifies divergence and not error, and the absorption tiers that drive it were
   assigned by the study team from pharmacokinetic sources and regulatory labels.

3. **The expert assessment is now framed as a finding rather than a failure of
   validation.** Two ophthalmologists agreed closely with each other (κ = 0.846) but
   graded most cases one tier below both the cascade and its gold. Crucially, their
   agreement with the gold was numerically identical to their agreement with the system
   (κ = 0.125 and 0.010), because the cascade reproduced its gold on all 12 cases. The
   divergence therefore lies between clinical prior and evidence-graded assessment, not
   in the system. We state plainly that with n = 12 it cannot be distinguished from
   chance-level agreement.

4. **The Discussion now states the methodological implication directly:** a severity
   rating exported from a systemic-route database is not a valid ophthalmic ground
   truth, and evaluating an ophthalmic tool against one measures the distance between
   two assumptions rather than accuracy. This is why the unadjusted-label agreement
   figures (0.210 and 0.443, Section 3.2) are reported as a quantification of the
   adjustment rather than as performance.

5. **The conclusion was rewritten** to lead with what the study establishes about the
   grading of ophthalmic DDI risk, and to state the audit-set high-risk sensitivity
   (0.440) as the number that bounds the system's current value as a safety screen.

**Limitations.** Section 3.8 and Section 4.4 have been revised to state the following
without softening: the L1 gold is literature-derived and author-annotated rather than
expert-adjudicated, and shares its sources with the rules; only the 40 procedurally
frozen cases are independent in a procedural sense, and only 20 of those were free of
development exposure; 78 of 118 L1 cases overlap the development-phase validation set by
case identity; the audit gold inherits the system's absorption assumption for 30 of 92
cases; audit-set high-risk sensitivity is 0.440, the lowest of the four methods; and at
1% prevalence the audit operating point implies a positive predictive value of
approximately 9%, so the system's value lies in systematic coverage and traceability
rather than in screening yield.

We are grateful for the editor's engagement with the supplement, which is what surfaced
the missing repository pointer.

Yours sincerely,

**Wang Guoqing, M.D.**
Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: 17690924120@163.com

**Yi Xianglong, M.D., Ph.D.** (corresponding author)
Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: yixianglong1010@163.com
