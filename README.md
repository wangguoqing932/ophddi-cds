# OphDDI-CDS

**Ophthalmic drug–drug interaction knowledge base and clinical decision support system.**

A deterministic, pharmacodynamic/pharmacokinetic rule-based framework for screening
interactions between **ophthalmic topical medications** and **systemic drugs**, with
explicit modelling of systemic absorption from the topical route.

Coverage: **113 ophthalmic agents × 232 systemic agents**, three interaction
mechanisms (pharmacodynamic, pharmacokinetic, systemic-absorption), a six-level
absorption tier on every ophthalmic agent, and an evidence level (A–E) on every
knowledge-base chunk.

## What is in this repository

| Path | Contents |
|---|---|
| `src/ophthalmic_ddi_cds_agent/` | Engine: `kg_layer.py` (three-layer cascade), `risk_rules.py`, `evidence_store.py`, retrieval adapters |
| `configs/` | `rules.yaml` (40 mechanism rules + 3 patient-factor policies), `class_matrix.yaml`, `drug_classes.yaml`, `flag_catalog.yaml`, prompts |
| `data/seed/` | `entities_a.csv` (113 agents with absorption tier), `entities_b.csv` (232 drugs), `evidence_chunks.jsonl` (1,307 chunks) |
| `data/gold/` | Validation sets with per-case provenance |
| `data/mock/` | 25 mock pairs for the demonstration script |
| `app/streamlit_app.py` | Interactive interface (3 tabs) |
| `scripts/` | Build, evaluation, audit and figure-generation scripts |
| `tests/` | Test suite |
| `outputs/` | Manuscript sources, figures, tables, recomputed numbers |

## The cascade

```
input: ophthalmic agent A + systemic drug B (+ patient factors)
  → entity normalisation against the registries
  → L1  rule engine: 40 mechanism rules, MAX-MATCH, not uniformly absorption-gated
  → L2  class matrix: 21 × 34 keys, 104 defined cells, absorption scaling in-layer
  → L3  G19 hard constraint: low/very-low absorption with no other signal → low
  → final grade = max(L1, L2); unknown drugs are refused, never scored
  → output: high / medium / low + matched rule IDs + decision path + source records
```

Layer shares over all 26,216 registry pairs: class matrix 68.7%, G19 12.2%,
rule layer 12.0%, explicit default-low 7.1%. The production path makes no LLM
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
| L1 literature-derived gold | 118 | 0.907 exact accuracy (107/118), κ 0.857 |
| Frozen blind subset | 40 | 39/40 (36/40 under pre-correction labels) |
| DDInter audit set | 92 | 0.674 exact accuracy; 0.548 on the 62 cases free of the system's absorption assumption |
| Registry-scale audit | 1,933 pairs | 75.3% graded lower than DDInter severity; 80.5% of downgrades attributable to low absorption |

The system's principal limitation is high-risk sensitivity on the audit set
(0.320, 8 of 25). The gold sets, the audit-set correction rule and every
limitation are documented in the manuscript and its supplementary material.

## Interactive demo

```bash
pip install -e ".[streamlit]"
streamlit run app/streamlit_app.py
```

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
> cascade for ophthalmic drug–drug interaction screening. (manuscript under review)

The release matching the submitted manuscript is tagged `v3.0-frontiers` and archived at
DOI [10.5281/zenodo.23439606](https://doi.org/10.5281/zenodo.23439606); the concept DOI
[10.5281/zenodo.23143344](https://doi.org/10.5281/zenodo.23143344) resolves to the newest version.
