# R1-5 independent adjudication packet (completed)

**Status: reviewed on 2026-11-14.** One non-author ophthalmologist (reviewer code GZQ)
returned all 30 cases. Result: exact agreement with the author classification **14/30
(46.7%)**; **14/28 (50.0%, kappa 0.271)** on the 28 cases within the author's three
classes. The reviewer classified 14 of the 21 author route-consistent downgrades as
unsupported, kept all five author unsupported cases, and considered two of the four
author over-grades supported upgrades. The returned file is
`cases_blinded_reviewed.csv`; the scored output is `independent_review_results.json`.

## Why this exists

Reviewer 1, comment 5 asked for a “focused, **independently reviewed** analysis” of the
30 disagreements, separating route-consistent downgrading from unsupported undergrading.
The manuscript currently reports an **author-made** classification and says so. This
packet lets an independent reviewer redo that classification without seeing the authors'
answers, the engine's decision path or the matched rule IDs.

## Eligibility

The reviewer must:

- be a clinician (ophthalmologist or clinical pharmacist) **not listed as an author**;
- not have participated in building the rule set, the class matrix or the reference labels;
- have no access to `author_key.csv` or to the engine's rationale while reviewing.

Author re-checking is useful for the numbers but **cannot** substitute for this step.

## Files

| File | Who sees it | Contents |
|---|---|---|
| `review_form.html` | reviewer | **offline web form** for the same 30 cases: radio choices, reason, confidence, autosave, CSV export. Recommended for sending. |
| `cases_blinded.csv` | reviewer | 30 cases: case ID, drug pair, reference label, system grade, absorption tier, direction; empty `your_class`, `your_reason`, `confidence` |
| `author_key.csv` | **study team only** | case ID → author classification (the answer key) |
| `analyze_independent_review.py` | study team | scores the returned CSV: exact agreement, Cohen's kappa, confusion matrix |
| `README.md` | both | this protocol |

Do **not** send `author_key.csv` to the reviewer. Do not add `path`, `rules` or the
author class to `cases_blinded.csv`.

## What the reviewer sees and does not see

Sees: the drug pair, the audit reference label, the system grade, the absorption tier,
and whether the system grade is a downgrade or an upgrade. These are needed to judge
whether the system's grade is supported.

Does not see: the author classification, the decision path (rule / matrix / G19 /
default), the matched rule IDs, or any model output. This prevents anchoring on the
authors' rationale while still allowing a judgement about the grade itself.

## Classification labels

Use one of these in `your_class`:

| Label | Use when | Applies to |
|---|---|---|
| `route_consistent_downgrade` | The lower system grade is consistent with limited systemic exposure from the topical ophthalmic route; the effect is plausibly exposure-dependent | downgrades |
| `unsupported_undergrading` | The lower system grade is not supported: the mechanism is not exposure-limited, the agent is high-absorption, or the clinical consequence remains at low exposure | downgrades |
| `system_overgrading` | The higher system grade is not supported by the pair and the reference label | upgrades |
| `supported_upgrade` | The higher system grade is supported (outside the author's three-class key; reported separately) | upgrades |
| `uncertain` | The provided information is insufficient to decide (reported separately, not scored) | either |

Write a one-line reason in `your_reason` for every case. `confidence` is optional
(`high` / `medium` / `low`).

## Step by step

1. Send the reviewer `review_form.html` (recommended) or `cases_blinded.csv`, plus the
   “Classification labels” section above (or this README with the `author_key.csv` row removed).
   The HTML form is self-contained and works offline in any browser; it autosaves and exports
   the same CSV schema.
2. Ask them to fill `your_class`, `your_reason` and, optionally, `confidence`; keep the
   case IDs unchanged.
3. Save the returned file as `cases_blinded_reviewed.csv` in this directory.
4. Score it:

```bash
python outputs/audits/r1_5_independent_review/analyze_independent_review.py \
  --reviewed outputs/audits/r1_5_independent_review/cases_blinded_reviewed.csv
```

Outputs: `independent_review_results.json` and `.md` (agreement, kappa, confusion
matrix, cases outside the three-class key).

## After scoring: what must be updated

- §3.5: replace “not independently adjudicated” with the reviewer's role, the agreement
  result, and any reclassifications.
- Supplementary Table S2 note: report the independent result and list every case whose
  class changed.
- R1 response, comment 5: add the independent review and the agreement figure.
- Rebuild manuscript/supplement clean and marked versions; rerun
  `python scripts/final_consistency_check.py` (expect 92/92) and
  `python scripts/audit_manuscript.py` (expect 0 FAIL / 2 WARN).

## Current numbers the reviewer's result will be compared against

Author classification: 21 route-consistent, 5 unsupported undergrading, 4 over-grading.
The 12 default-path cases comprise 10 route-consistent and 2 unsupported. These are the
values in Supplementary Table S2 and §3.5.
