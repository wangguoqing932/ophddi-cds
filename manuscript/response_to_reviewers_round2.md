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
**171 pairs with a low-or-below absorption tier receive medium (95) or high (76), all 171
arrive through the rule path, and all 76 high grades come from
`nsaid_antihypertensive_antagonism`**, which requires no absorption flag.

The manuscript no longer claims that absorption scaling forces low-absorption pairs to
low risk across the cascade. Section 2.2 now states that the forcing applies within the
matrix layer only and that the final grade is the maximum of an ungated rule layer and
an absorption-scaled matrix layer, and Section 4.2 draws the consequence. The path
distribution the reviewer asked for is reported: class matrix 68.8%, G19 hard constraint
12.0%, rule layer 11.9%, default-low 7.3%. The previously undocumented default-low path
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
- **flurbiprofen.** Confirmed: tiered high in `entities_a.csv` while the candidate file
  records no tier flag, with identical evidence sources. Recorded as a defect in
  Section 4.4.
- **Nine non-topical agents.** Confirmed: six intravitreal anti-VEGF agents (including
  aflibercept, which the manuscript itself uses as the example of a pair with no
  plausible topical pathway), intraocular acetylcholine and two surgical viscoelastics.
  Recorded in Section 4.4.

*Open:* re-running the registry analysis after correcting the assignments. Because the
tier drives both the class-matrix forcing and the L3 constraint, correcting it will move
the 75.0% figure in Section 3.4 and other reported numbers. We have therefore not
changed the assignments in this revision; instead we deposit the tier table with sources,
report the defects, and make the correction the first item of future work (Section 4.5).
Section 3.4 already carries the tier cross-tabulation the reviewer asked for
(`audits/divergence_by_tier.csv`), so the magnitude can be judged against the tier
distribution that produces it.

### Comment 5 — the baseline comparison cannot support the claim made for it

**Accepted; the conclusion is qualified rather than defended.** Section 2.4 now states
that the comparison used a single proprietary endpoint (`deepseek-chat`) with a 10-token
output cap that forces a one-word answer and precludes any reasoning or justification,
that parsing was by substring, that the named `lightrag` baseline does not query the
LightRAG index, and that these choices bound what the comparison can support. The exact
prompts and parameters are provided in Supplementary Text S3 and in
`configs/prompts.yaml`.

We have also reported the comparison symmetrically, as requested: on the audit set the
two ungrounded baselines reach 0.848 high-risk sensitivity each, against 0.440 for the
cascade (lightrag 0.296). This appears in Section 3.5 and, in abbreviated form, in the
Abstract.

*Open:* re-running the comparison with a reasoning model, adequate token budget and
repeated sampling at fixed temperature. This is a substantive new experiment rather than
a revision of text, and we would prefer to run it as such; the current revision states
what the existing comparison can and cannot support.

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

**Accepted.** Section 3.5 now reports 37 of 62 (**0.597**) alongside 0.707 and identifies
it as the figure free of the system's own assumption; the Abstract carries the same
qualification. The stratified breakdown was already disclosed and remains.

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

**Partially confirmed.** The skipped test is confirmed to be an empty placeholder
(`test_integration.py`, marked "Fill in during Phase 4"). We have not been able to
reproduce the cp1252 failure on a clean Windows clone: the repository contains no Greek
beta in any file the tests read, and the suite reports 34 passed, 1 skipped under the
default console encoding. We would be grateful for the traceback so we can fix the
specific case rather than guessing.

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

## Open items, stated plainly

We prefer the response to be shorter than the record of what remains undone.

1. **Absorption-tier reassignment (R1-4, R1-6).** The defects are documented and the
   per-agent table is deposited, but the tiers themselves have not been changed, because
   doing so moves the 75.0% divergence figure and other reported numbers. We have made
   this the first item of future work rather than presenting corrected numbers we have
   not produced.
2. **Rule-layer absorption gating (R1-3).** The cascade's actual behaviour is now
   described accurately, with the path distribution quantified. Whether to gate
   `nsaid_antihypertensive_antagonism` is a design decision with downstream effects on
   results, and we have left it open.
3. **Baseline re-run with a reasoning model (R1-5).** Not performed. The comparison's
   limitations are now stated explicitly in both the Methods and the Discussion, and we
   have reported the direction in which the baselines outperform the system.

We are grateful to Reviewer 1 for auditing the deposit rather than accepting it, and to
Reviewer 2 for a set of questions that made the Methods substantially more complete.

Yours sincerely,

**Wang Guoqing, M.D.**
Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: 17690924120@163.com

**Yi Xianglong, M.D., Ph.D.** (corresponding author)
Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University
E-mail: yixianglong1010@163.com
