# Response to Reviewers — Round 2

**Manuscript ID:** 363ea8da-e16c-45ce-bbf1-39ff3555463b

**Title:** OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug–Drug Interaction Screening

**Authors:** Wang Guoqing, M.D.; Yi Xianglong, M.D., Ph.D. (corresponding)

---

Dear Dr Shelke, Dr Parikesit and reviewers,

We thank both reviewers for an unusually careful read. Reviewer 1 in particular
audited the deposit rather than trusting it, and several of the findings are correct in
ways we could not have discovered from our own working copy: the deposit did not
contain the evaluation material, two of the three stubs really were stubs, and the
absorption forcing does not operate where the manuscript said it does. We verified
each point independently before acting on it, and where a claim was wrong we have said
so in the manuscript rather than quietly correcting it.

This round we have completed the changes that are purely textual or documentary. Three
items remain open, and we state clearly which they are and why, rather than letting the
response imply more progress than the manuscript reflects.

A marked-changes copy is uploaded as a related file, with every changed paragraph in
red. The main manuscript file is clean, as the journal requires.

---

## Reviewer 1

### Comment 1 — the deposit did not support the reproducibility claims made for it

**Accepted; the material is now deposited.** The reviewer is right that a fresh clone
contained no gold file, no expert ratings, no prediction rows, no evidence base and no
DDInter severity table, and that `configs/prompts.yaml` and
`src/ophthalmic_ddi_cds_agent/naive_rag.py` were placeholders. The material existed in
the predecessor working copy; it had never been deposited, and the Availability
sentence described a package the reader could not reach. That was a genuine failure of
the deposit, not a misunderstanding.

All of it is now public at **https://github.com/wangguoqing932/ophddi-cds** (release tag
`v1.0-submission`, accessible without an account), and the Availability statement has
been rewritten to describe what is actually there.

| Requested | Now deposited |
|---|---|
| Four gold files with case-level provenance | `data/gold/` — 6 sets (118 / 92 / 200 / 70 + two development-gate sets), each with `cases.jsonl`, `dataset.meta.json` and source references |
| 9,600 prediction rows | `data/predictions/` — 4 methods × 5 temperature conditions × 4 datasets, per-seed files, aggregate metrics, run log |
| 12-case expert ratings | `data/expert_review/` — ratings, response archive, review instrument, scanned questionnaires |
| Evidence base | `data/evidence/evidence_chunks.jsonl` — 1,307 chunks, plus the offline citation cache |
| DDInter severity table | `data/ddinter/ddinter_code_{A,B,C,N,S}.csv` |
| Exact prompts | `configs/prompts.yaml` — was 1 line, now 98: system prompt, BM25 parameters, per-method user prompts, parse rule, 10-token cap, temperature schedule |
| Retrieval code | `src/ophthalmic_ddi_cds_agent/naive_rag.py` — was a 2-line skeleton, now a working BM25 retrieval class |
| Evaluation and statistics scripts | `scripts/run_multiseed_per_dataset.py`, `scripts/evaluate.py` |

`scripts/run_baselines.py` retains its `--synthetic` behaviour, but its module docstring
now states in its first lines that it is an offline pipeline scaffold, **not** the
reported evaluation, and that its synthetic mode hardcodes `full_system` at zero error
and must never be used as a result.

### Comment 2 — "40 citation-verified mechanism rules" is not what the report shows

**Accepted in full.** The verification report covers 8 manifest items over 7 distinct
DOIs, of which three rules resolve to a verified literature citation. Of the 40 rules,
53 source records break down as 41 DrugBank entries, 7 regulatory label records, 2
DOIs, 2 DDInter pair annotations and 1 PubMed citation; the DrugBank and label records
were never independently re-verified.

The phrase "citation-verified" has been removed throughout, and Methods Section 2.2 now
states the coverage precisely, including the reviewer's suggested formulation. We have
also recorded the two specific problems the reviewer identified: that several rules
whose output class would call for a citation declare a list that does not resolve to a
verified item, and that `beta_blocker_digoxin_additive` cites a study of additive
topical-plus-systemic beta-blockade rather than a digoxin-specific source while grading
as high a pair its own DDInter annotation records as moderate. The conservative high
grade is retained; the provenance gap is now stated rather than left implicit.

### Comment 3 — the absorption-first mechanism is not enforced where the paper says it is

**Accepted; the reviewer's numbers reproduce exactly.** We wrote an independent audit
(`scripts/path_attribution_audit.py`, output deposited as `audits/path_attribution.json`)
and swept all 26,216 evaluable registry pairs. The result matches the reviewer's figures:
**202 pairs with a low-or-below absorption tier receive medium (107) or high (95), all 202
arrive through the rule path, and all 95 high grades come from
`nsaid_antihypertensive_antagonism`**, which requires no absorption flag. These figures are from
the corrected registry; the same audit before the flurbiprofen correction gave 171 pairs with
76 high grades.

The manuscript no longer claims that absorption scaling forces low-absorption pairs to
low risk across the cascade. Section 2.2 now states that the forcing applies within the
matrix layer only and that the final grade is the maximum of an ungated rule layer and
an absorption-scaled matrix layer, and Section 4.2 draws the consequence. The path
distribution the reviewer asked for is reported in Section 2.2 and in the deposited audit:
class matrix 68.7%, G19 hard constraint 12.2%, rule layer 12.0%, default-low 7.1%. The previously undocumented default-low path
is now described in the cascade description.

*Open:* whether to gate `nsaid_antihypertensive_antagonism` on absorption, as the four
matrix upgrades are gated. That changes the system's behaviour and therefore the
reported results, so we have not done it silently; we describe the behaviour accurately
in this revision and identify the gating decision as future work.

### Comment 4 — the absorption tier is the most load-bearing and least documented variable

**Accepted; the documentation gaps are closed, the reassignment is flagged.**

- **Per-agent table.** Now deposited as Supplementary Table S5 (113 rows) with a source
  record for every agent, and in the deposit at
  `data/registry/per_agent_absorption_tier.csv`. The reviewer is right that the previous
  Supplementary Table S5 was the audit stratification and that the word flurbiprofen did
  not appear anywhere in the supplement.
- **Operational definition.** Section 2.2 now gives the thresholds and units: the tier is
  a categorical assignment intended to represent fractional systemic bioavailability
  (high ≳50%, medium ≳10–50%, low <10%, with very-low, minimal and none indicating
  progressively smaller exposure), and it is stated explicitly that the sources report
  heterogeneous quantities (bioavailability fractions, plasma concentrations, qualitative
  statements), so the tiers are an ordinal model rather than measured exposure.
- **Six values, not four.** Section 2.2 now reports all six and their counts (16 high,
  17 medium, 60 low, 9 very-low, 7 minimal, 4 none) and notes that the L3 constraint
  tests four of them.
- **flurbiprofen.** Confirmed and **corrected in this revision**. The registry tiered it
  high while the curation file recorded low, for the same two evidence sources (DrugBank
  DB00712, PubMed). At 0.03% it is the lowest-concentration ophthalmic NSAID in the
  registry and the other four ophthalmic NSAIDs are all tiered low, so the high tier was a
  data-entry error with no pharmacokinetic basis. It is now tiered low, and every
  downstream analysis has been re-run (see the item on the affected numbers below).
- **Nine non-topical agents.** Confirmed: six intravitreal anti-VEGF agents (including
  aflibercept, which the manuscript itself uses as the example of a pair with no
  plausible topical pathway), intraocular acetylcholine and two surgical viscoelastics.
  Recorded in Section 4.4.

**The correction moved several reported numbers, and all of them have been re-run rather
than patched.** Correcting the flurbiprofen tier changes the cascade's output on every
pair involving it, which propagates into both validation sets and the registry-scale
audit; additionally, the registry-scale audit itself could not be reproduced from the
deposited code (74.2% rather than the reported 75.0%), because the audit had been run
nine minutes before the registry was last modified and the first commit captured the
modified registry beside the stale audit result. We therefore treat the flurbiprofen
correction and the reproducibility defect as one repair. Table 3, Figure 2, Sections 3.3
to 3.6, the Abstract and the Conclusion have all been regenerated; the corrected values
are listed in the "Change to the reported numbers" section below.

*Open:* reassigning the nine non-topical agents. The tier drives both the class-matrix
forcing and the L3 constraint, and the scenario analysis deposited with the manuscript
(`audits/tier_alternative_scenarios.json`) quantifies how each candidate reassignment
moves the registry-scale figures; adopting one is a scientific choice rather than an
error correction, so we have not made it unilaterally and have made it the first item of
future work (Section 4.5). Section 3.4 carries the tier cross-tabulation the reviewer
asked for (`audits/divergence_by_tier.csv`), so the magnitude can be judged against the
tier distribution that produces it.

### Comment 5 — the baseline comparison cannot support the claim made for it

**Accepted and acted on.** The reviewer identified three specific deficiencies and proposed
four remedies, all of which we adopted: a current reasoning model, an adequate output budget,
repeated sampling at fixed temperature rather than one temperature per condition, and a
pre-specified parsing rule. The three LLM baselines were re-run over both validation sets
(3,150 API calls, no errors and no unparseable responses) with `glm-5.3-flash`, a 3000-token
budget, temperature 0.0, five repeated samples per case and a majority vote. Prompts, retrieval
settings and parse rule were otherwise unchanged, so the two settings differ only in model,
budget and sampling. Both settings are now reported side by side (new Section 3.6; Table 3;
Figure 2).

**The reviewer was right that the 10-token cap suppressed the baselines**, and the re-run shows
it in the accuracy column: on the L1 set pure_llm rises from 0.475 to 0.576 and naive_rag from
0.415 to 0.585. **But the constraint was masking a worse problem, not a better capability.**
With an adequate budget the baselines shift toward a conservative rarely-high-risk policy:
pure_llm assigns high risk to 6% of L1 cases where the gold contains 24%, and to 2% of audit-set
cases where the gold contains 27%. High-risk sensitivity therefore falls from 0.771 to 0.250
(pure_llm), 0.757 to 0.214 (naive_rag) and 0.779 to 0.536 (lightrag), while specificity rises to
approximately 1.000. Because both gold sets are dominated by low and medium grades, this
conservatism inflates exact accuracy — which is why accuracy improved while discrimination
collapsed. We report this as a finding about what general-purpose models do when given room to
reason in this domain, and we base no claim about LLM capability on the accuracy column.

**Two further consequences we report rather than manage.** First, the ordering between retrieval
methods reverses: naive_rag scored below pure_llm under the 10-token cap (0.415 versus 0.475),
and we had attributed that to retrieval noise, but with an adequate budget naive_rag scores at or
above pure_llm on both sets (0.585 versus 0.576; 0.728 versus 0.609). **We withdraw the claim that
keyword retrieval injects noise in this domain** and have removed it from the Introduction,
Results and Discussion. Second, on the audit set the adequate-budget naive_rag baseline reaches
0.728 exact accuracy and 0.400 sensitivity, both above the cascade (0.674 and 0.320). This is the
one comparison in which a baseline outperforms the system and we state it in the Abstract,
Results and Discussion rather than leaving it to be discovered; its sensitivity is unstable
across samples (0.280 to 0.480), whereas the cascade returns the same grade every time.

**A note on sampling that vindicates the reviewer's third point.** Even at temperature 0.0 the
baselines varied by 0.013 to 0.034 in exact accuracy across five repeats, so a single call would
not have been a fair comparison; the reported figures use a majority vote. The cascade's SD
remains 0.000.

**Net effect on the paper's claims.** On the L1 set the cascade's advantage in high-risk
sensitivity is now larger than before (0.964 versus 0.214–0.536, where the earlier comparison
gave 0.964 versus 0.757–0.779), because the baselines are no longer constrained into giving an
answer. On the audit set the cascade is not the best method and we say so. We have therefore
narrowed the claim: the contribution is a deterministic, auditable decision procedure with a
high-sensitivity profile and reproducible output, not across-the-board superiority in label
agreement.

### Comment 6 — the registry-scale divergence measures the absorption model, not the database

**Partially accepted.** The framing point is taken: Section 3.4 already disclosed that
the tiers were assigned by the study team, and it now leads with the consequence — the
measurement is a property of an explicitly stated absorption model, not an independent
pharmacokinetic result. The tier × severity cross-tabulation the reviewer asked for is
deposited as `audits/divergence_by_tier.csv`. We have also softened the Background claim
about route-specific severity being absent from mainstream resources, and added the
reviewer's examples (Drugs.com maintains a separate ophthalmic entity for timolol with
its own severity distribution; Lexicomp asks the user to specify route).

*Open:* the same analysis under one or two alternative tier assignments. This depends on
the tier reassignment in comment 4 and is folded into the same future-work item.

### Comment 7 — the expert argument is a tautology as stated

**Accepted; the sentence has been removed.** The reviewer's logic is right: because the
system reproduced its gold on all 12 cases, expert-versus-gold and expert-versus-system
agreement are necessarily the same comparison, and that identity cannot be evidence that
the divergence is not system-specific.

In the course of acting on this we found a second, related problem that neither reviewer
could have seen from the manuscript. **The expert instrument was not blinded.** The
questionnaire shown to both ophthalmologists displays, for every case, the proposed gold
grade and the system grade with a one-line mechanistic rationale; the scanned
questionnaires, the blank template and the archived responses all carry these two
columns. The manuscript previously described the experts as "blinded to system outputs
and gold labels", which is not correct. We have rewritten the passage as a **grade
review** in Methods 2.5 (renamed), Results 3.7, the contributions paragraph, Discussion
4.1, Limitations 3.8 and 4.4, and the Abstract and Conclusion.

What the exercise does support is stated plainly and nothing more: two ophthalmologists,
given no mechanism evidence, did not endorse the assigned grades, and their divergence
was stable between them; with n = 12 and near-chance kappa it cannot be distinguished
from chance. We have also noted, as the reviewer requested, that the maximum achievable
unweighted kappa of 0.625 applies to one expert's marginals rather than both.

### Comment 8 — the audit set mixes a third-party component with one graded under our assumption

**Accepted.** Section 3.5 now reports 34 of 62 (**0.548**) alongside 0.674 and identifies
it as the figure free of the system's own absorption assumption; the Abstract now carries
the same qualification, as the reviewer asked. The stratified breakdown (30 corrected
cases 28/30; 62 kept cases 34/62) is reported in the same subsection, and the
tier x severity cross-tabulation is deposited as `audits/divergence_by_tier.csv`.

### Comment 9 — supplementary cross-references are systematically wrong

**Accepted; the numbering has been rebuilt.** The root cause was that prose sections and
tables shared one S1–S6 sequence while the tables also carried their own Table S1–S6
labels, so the two collided. There are now two independent series, **Supplementary Text
S1–S7** and **Supplementary Table S1–S8**, and every cross-reference in the manuscript
has been checked against the item it names.

The four missing items the reviewer identified have been supplied:

- the **per-agent absorption tier table** (now Table S5, 113 rows with sources);
- the **evaluation prompts** (now Text S3, full system prompt and all three user
  prompts with parameters);
- the **TRIPOD-AI checklist** (now Text S6 — the previous Text S6 was the abbreviation
  list, which is now Text S7);
- the **L1 disagreement rationales** (now Table S1 — the previous Table S1 was the
  registry summary, now Table S4).

### Comment 11 — matrix counts

**Accepted.** The configuration declares 21 ophthalmic row keys and 40 systemic column
keys, 34 columns in use, and 104 cells carrying an explicit level. Section 2.2 now
reports these figures and states that the earlier 20 × 37 / 82 description did not match
the configuration. The malformed cell
(`anticholinergic × antidepressant_tca`, whose advice string had been split by a
newline-and-colon into a spurious `delirium): null` key) has been repaired, and the
matrix is described as sparse by design with a default cell for undefined pairs.

### Comment 12 — "zero variance" as a comparative virtue

**Accepted.** Removed from the Abstract and the Conclusion. It is retained in Results 3.6,
where it is stated as a determinism check on a method that makes no model call, and in
Section 4.2 it is explicitly recast as a design property rather than a robustness result.

### Comment 13 — test suite requires forced UTF-8

**Confirmed and fixed; the reviewer's diagnosis was exactly right.** The failure is in
`scripts/verify_rule_citations.py`, which printed its JSON report to stdout with
`ensure_ascii=False`. The report contains the full citation records, and those include
Greek characters from drug names and pharmacological terms (`β`, `α`, `μ`). On a cp1252
console the print raises `UnicodeEncodeError: 'charmap' codec can't encode character
'β'`, which fails `tests/test_phase3_policy.py::test_policy_gate_replays_cached_sources`
— the test that replays cached citations offline.

We reproduced it under `PYTHONIOENCODING=cp1252` and fixed it by writing the report to
file as UTF-8 (unchanged) while degrading only the terminal echo to ASCII escapes. The
suite now passes under both encodings:

```
PYTHONIOENCODING=cp1252 pytest tests/   ->  34 passed, 1 skipped
pytest tests/                            ->  34 passed, 1 skipped
```

This was a real portability defect and it sat oddly with the "platform independent"
claim, as the reviewer notes; that claim is now accurate. The skipped test is confirmed
to be an empty placeholder (`test_integration.py`, marked "Fill in during Phase 4"), and
we have left it as such rather than presenting it as a passing test.

### Comment 14 — fingerprints depend on line endings

**Accepted; the definition is now stated.** Section 2.7 notes that SHA-256 digests are
defined over **LF-normalised content**, gives both digests for the deposited
`configs/rules.yaml` (`2afabaad81161c40` under CRLF as deposited, `b5c77f6fde8a9f7d` after
LF normalisation) so a reader can reproduce either, and states that the evidence and index
fingerprints are recorded alongside the deposited artefacts rather than only in the
project log.

### Comment 15 — reference errors

**Accepted; all four corrected**, verified against Crossref and the arXiv API:

| Ref | Was | Now |
|---|---|---|
| 1 | fifth author "Peterson G" | **Widmark G** |
| 14 | Cochrane issue 3 | **issue 2** |
| 21 | authors "Wang Y, Wu Z, Wu C, et al." | **Guo Z, Xia L, Yu Y, Ao T, Huang C** (5 authors; the previous list named people not on the paper) |
| 27 | 2019, no volume | **2020;48(1):24-30** |

The statement "three over-alerts" has been corrected to **four**: tacrolimus × ibuprofen
was omitted from the list.

---

## Reviewer 2

All fourteen points have been addressed in Methods Sections 2.1–2.4.

| # | Point | Where addressed |
|---|---|---|
| 1 | Whether route of administration is covered | New paragraph in 2.1: route is modelled through the absorption tier and through route-dependent rule predicates, not as a free-text field |
| 2 | Bold L1/L2/L3 and other sub-labels | L1/L2/L3 now bold in 2.2; the corresponding labels in 3.5 bolded |
| 3 | Second-order interactions | 2.2: none are modelled; rules are evaluated independently; the only cross-layer composition is the final maximum |
| 4 | Most matrix cells undefined | 2.2: the matrix is sparse by design, 104 defined cells, undefined pairs fall through to the L3 default rather than receiving an interpolated grade; the matrix is deposited |
| 5 | Is absorption scaling empirically validated | 2.2: stated that it is not, with the rationale and where its behavioural consequence is quantified |
| 6 | Which layer the class mapping applies to | 2.2: the drug-to-class mapping is consumed by the L2 matrix layer only |
| 7 | Gold selection criteria | 2.3: inclusion rule for the 20 mechanism annotations and the sampling logic for the 58 guideline cases |
| 8 | "No human expert participated" vs a study team of experts | 2.3: clarified that the team comprises the two named clinician authors, so the statement means no *independent* expert was involved |
| 9 | How the gold shares sources with the rules | 2.3: the sharing differs by subset, described per subset |
| 10 | Contradictory evidence | 2.3: more conservative grade retained, disagreement recorded in the case file |
| 11 | Development data in its own subsection; correction method | 2.3: development sets separated from validation sets, features and labels described; explicit three-condition correction rule for the 30 audit cases |
| 12 | DeepSeek architecture version and input language | 2.4: model identifier as used, the endpoint does not expose architecture, English input throughout |
| 13 | RAG protocol | 2.4: BM25 parameters, query string, top-k, truncation and prompt assembly given in full |
| 14 | Prompts not findable | Supplementary Text S3 (full prompts) and `configs/prompts.yaml` in the deposit |

---

## Change to the author list

This revision adds two authors, both of whom contributed to the revision work and have
approved the submitted version:

- **Lumei Hu, M.D.** — Department of Ophthalmology, The First Affiliated Hospital of Xinjiang
  Medical University (second author)
- **Shaocheng Wang, M.D.** — Department of Gastroenterology, Xinjiang Production and
  Construction Corps Third Division General Hospital (third author)

The author list is now Wang G, Hu L, Wang S, Yi X, and the Author Contributions statement has
been updated accordingly (both new authors are credited with clinical input, data
interpretation and critical revision of the manuscript). We draw the editor's attention to this
change explicitly because author-list changes after submission require editorial awareness; all
four authors have approved the submission, and no other element of authorship has changed.

---

## Change to the reported numbers

Correcting the flurbiprofen tier, and repairing the stale registry audit that the same
investigation exposed, moved several reported values. All occurrences in the manuscript,
tables, figures and supplement have been regenerated from the corrected data rather than
edited by hand. The reviewer's request for an analysis under alternative tier assignments
is what surfaced the problem, so we set the changes out explicitly.

| Quantity | Previously reported | Corrected |
|---|---|---|
| L1 118 cases: exact accuracy | 0.915 (108/118) | **0.907 (107/118)** |
| L1: Cohen's kappa | 0.870 | **0.857** |
| L1: high-risk sensitivity | 1.000 (28/28) | **0.964 (27/28)** |
| Frozen blind subset (n = 40) | 1.000 (40/40) | **0.975 (39/40)** |
| Audit set: exact accuracy | 0.707 (65/92) | **0.674 (62/92)** |
| Audit set: high-risk sensitivity | 0.440 (11/25) | **0.320 (8/25)** |
| Audit set, third-party-only subset | 0.597 (37/62) | **0.548 (34/62)** |
| Registry audit: pairs downgraded | 1,450 (75.0%) | **1,455 (75.3%)** |
| Registry audit: downgraded from high | 346 (17.9%) | **352 (18.2%)** |
| Registry audit: low-absorption attributable | 1,117 (77.0%) | **1,171 (80.5%)** |
| Rule path, low-tier pairs receiving medium/high | 171 (76 high) | **202 (95 high)** |

Two of these changes work against the paper and one works for it, and we state which is
which. **Against:** the audit-set sensitivity falls from 0.440 to 0.320, and the L1
sensitivity is no longer exactly 1.000; the "perfect" framing has been removed wherever
it appeared. **For:** the registry-scale result strengthens, with low-absorption
attribution rising from 77.0% to 80.5%, and the flurbiprofen pair — now correctly tiered
low — becomes a clearer illustration of the paper's central point, since a 0.03%
formulation cannot plausibly reach systemic exposure yet carries a systemic-route
severity rating of high in the database.

The recomputation is replayable: `scripts/rerun_lightrag_flurbiprofen.py` re-runs the
affected LLM predictions, `scripts/rebuild_metrics_json.py` rebuilds the aggregate
metrics, and `scripts/tier_reassignment_scenarios.py` reproduces the scenario table.

---

## Open items, stated plainly

We prefer the response to be shorter than the record of what remains undone.

1. **Tiering of the nine non-topical agents (R1-4).** The flurbiprofen error is corrected and
   the registry-scale analysis re-run, but the nine agents in the ophthalmic registry that are
   not topically administered (intravitreal anti-VEGF agents, intraocular acetylcholine, two
   surgical viscoelastics) are still tiered on a topical-absorption rationale that does not
   apply to them. The scenario analysis deposited with the manuscript quantifies how each
   candidate reassignment moves the registry-scale figures; we have not adopted one unilaterally.

2. **Rule-layer absorption gating (R1-3).** The cascade's behaviour is now described accurately
   and the path distribution quantified, with the measured cost of gating reported (L1 accuracy
   falls from 0.907 to 0.890 or 0.847 depending on how many rules are gated). We argue the
   decision belongs with outcome-linked calibration rather than with fitting the present gold,
   and have left the engine unchanged.

3. **Other reasoning models (R1-5).** We re-ran the baselines with one reasoning model
   (glm-5.3-flash). Whether the conservative shift we observe is specific to this model or
   general across current reasoning models is not established by a single model, and we say so
   in Section 3.6.

**Wang Guoqing, M.D.**
Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: 17690924120@163.com

**Yi Xianglong, M.D., Ph.D.** (corresponding author)
Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: yixianglong1010@163.com
