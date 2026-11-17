# OphDDI-CDS

**Ophthalmic drug–drug interaction knowledge base and clinical decision support system.**

A deterministic, pharmacodynamic/pharmacokinetic rule-based framework for screening
interactions between **ophthalmic topical medications** and **systemic drugs**, with
explicit modelling of systemic absorption from the topical route.

Coverage: **113 ophthalmic agents × 232 systemic agents**, three interaction
mechanisms (pharmacodynamic, pharmacokinetic, systemic-absorption), a six-level
absorption tier on every ophthalmic agent, and an evidence level (A–E) on every
knowledge-base chunk.

## Current manuscript and results

This repository accompanies the **Frontiers in Pharmacology** Original Research submission
(manuscript ID 2032864). The values below are the ones reported in the current manuscript:

- **1,933** registry-matched pairs with a graded DDInter severity; **77.7%** were graded lower
  by absorption-aware assessment, **76.3%** among the **1,757** assessed pairs, and **80.3%**
  of downgrades involved low-tier ophthalmic agents.
- **118-case author-derived reference set:** 101/118 exact agreement under the frozen labels
  (0.856; kappa 0.779); 104/118 after the three post-lock corrections (0.881; kappa 0.818),
  reported as a sensitivity analysis.
- **40-case frozen blind set:** 36/40 (0.900).
- **92-case semi-independent audit:** 62/92 (0.674); high-risk sensitivity 8/25 (0.320).

The BMC-era package is archived under `outputs/archive/bmc_submission/` and is **not** the
current submission. The current deposit is `v3.0-frontiers` (DOI 10.5281/zenodo.23439606).

## What is in this repository

| Path | Contents |
|---|---|
| `src/ophthalmic_ddi_cds_agent/` | Engine: `kg_layer.py` (three-layer cascade), `risk_rules.py`, `evidence_store.py`, retrieval adapters |
| `configs/` | `rules.yaml` (40 mechanism rules + 3 patient-factor policies), `class_matrix.yaml`, `drug_classes.yaml`, `flag_catalog.yaml`, prompts |
| `data/seed/` | `entities_a.csv` (113 agents with absorption tier), `entities_b.csv` (232 drugs), `evidence_chunks.jsonl` (1,307 chunks) |
| `data/datasets/` | Validation sets with per-case provenance |
| `data/mock/` | 25 mock pairs for the demonstration script |
| `app/streamlit_app.py` | Interactive interface (3 tabs) |
| `scripts/` | Build, evaluation, audit and figure-generation scripts |
| `tests/` | Test suite |
| `outputs/` | Manuscript sources, figures, tables, recomputed numbers |

### Where the final files are

| Location | Role |
|---|---|
| `outputs/deliverables/frontiers/` | **Submission package** — clean and marked manuscript, supplement, both response letters, cover letter, Figures 1–6 (PDF/PNG/SVG/TIFF), scope statement |
| `outputs/paper/manuscript.en.md` | Manuscript source of record (the file the build reads) |
| `outputs/deliverables/supplementary_files/Supplementary_Material.md` | Supplement source of record |
| `outputs/submission/response_to_reviewers_r1.md`, `..._r2.md` | Response-letter sources of record |
| `outputs/deliverables/manuscript_round2_submitted.md` | Baseline text of the previously submitted version; `build_marked_docx.py` diffs against it to produce the redline. Kept in place because the build reads it — not a current manuscript |
| `outputs/deliverables/{manuscript,cover_letter,figure_legends}.*` | Build outputs kept in their canonical script locations; identical to the copies in `frontiers/` |
| `outputs/archive/` | **Superseded versions only** (pre-compression drafts, old figures, pre-fix predictions, BMC package, QA page renders). See `outputs/archive/README.md`; nothing here is submitted |

Build scripts write to the canonical locations above and then sync `frontiers/`; old
versions are never edited in place.

## The cascade

```
input: ophthalmic agent A + systemic drug B (+ patient factors)
  → entity normalisation against the registries
  → L1  rule engine: 40 mechanism rules, MAX-MATCH, absorption-gated where the exposure model applies
  → L2  class matrix: 21 × 34 keys, 104 defined cells, absorption scaling in-layer
  → L3  G19 hard constraint: low/very-low absorption with no other signal → low
  → final grade = max(L1, L2, L3); unknown drugs are refused, never scored
  → output: high / medium / low / unassessed + matched rule IDs + decision path + source records
     (unassessed = no rule and no defined matrix cell; a coverage gap, not assessed low risk)
```

Layer shares over all 26,216 registry pairs: class matrix 25.7%, G19 42.9%,
rule layer 11.7%, explicit default-low/unassessed path 19.7%. The production path makes no LLM
call and returns identical grades across temperature conditions.

## Quick start

```bash
python -m venv .venv && source .venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt

# zero-configuration smoke test: 25 mock pairs, no API key, no network
python scripts/demo_pipeline.py

# test suite
python -m pytest tests/ -q
```

Python 3.11 or later is required (the package uses `enum.StrEnum` and `datetime.UTC`).

## Reproducing the reported results

```bash
# every number in the manuscript -> outputs/recomputed/numbers.json
python scripts/recompute_all_reported_numbers.py

# statistics used in the paper, with a self-test against the reported values
python scripts/stats_tests.py

# expert-review statistics from the raw ratings
python scripts/expert_review_analysis.py

# BM25 leakage audit and the 1,933-pair DDInter audit
python scripts/naive_rag_leakage_audit.py
python scripts/audit_ddinter_disagreement.py

# manuscript consistency gate (must report 0 FAIL)
python scripts/audit_manuscript.py
```

Re-running the LLM baselines requires model-API credentials in `.env`
(see `.env.example`); the deterministic cascade requires none.

## Evaluation summary

| Set | n | Result |
|---|---|---|
| L1 literature-derived reference | 118 | 0.856 under the frozen labels (101/118; κ 0.779); 0.881 after three post-lock corrections (104/118; κ 0.818) |
| Frozen blind subset | 40 | 36/40 under the frozen labels (0.900); 39/40 after corrections |
| DDInter audit set | 92 | 0.674 exact agreement; 0.548 on the 62 cases free of the system's absorption assumption |
| Registry-scale audit | 1,933 pairs | 77.7% graded lower than DDInter severity; 80.3% of downgrades involved low-tier ophthalmic agents |

The system's principal limitation is high-risk sensitivity on the audit set
(0.320, 8 of 25). The reference sets, the audit-set correction rule and every
limitation are documented in the manuscript and its supplementary material.

## Interactive demo

```bash
pip install -e ".[streamlit]"
streamlit run app/streamlit_app.py
```

The interface uses the same palette as the manuscript figures and is labelled in English.
A three-page illustrated walkthrough, built from screenshots of the running app, is in
[`outputs/deliverables/Interactive_Demo_Guide.pdf`](outputs/deliverables/Interactive_Demo_Guide.pdf).

[![Step 1 — select a pair](outputs/figures/demo_ui_step1_select.png)](outputs/deliverables/Interactive_Demo_Guide.pdf)

> ⚠️ Research decision support only. It does not replace clinician or pharmacist judgement.

## Data sources and licensing

Evidence is derived from DDInter 2.0, FDA ophthalmic product labels, DrugBank,
Stockley's Drug Interactions, the British National Formulary and PubMed.

- Code: Apache-2.0
- Original data and configuration: CC BY 4.0
- **Bundled DDInter severity tables remain under DDInter's CC BY-NC-SA 4.0 terms**
  and are included for research reproducibility only.

See `LICENSE` for the component split.

## Citation

If you use this work, cite the manuscript:

> Wang G, Hu L, Wang S, Yi X. OphDDI-CDS: an absorption-first deterministic
> cascade for ophthalmic drug–drug interaction screening. Frontiers in Pharmacology
> (Original Research, manuscript under review; ID 2032864).

The release matching the submitted manuscript is tagged `v3.0-frontiers` and archived at
DOI [10.5281/zenodo.23439606](https://doi.org/10.5281/zenodo.23439606); the concept DOI
[10.5281/zenodo.23143344](https://doi.org/10.5281/zenodo.23143344) resolves to the newest version.
