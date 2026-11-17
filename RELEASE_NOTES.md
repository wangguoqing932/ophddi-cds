# Release notes — v3.0-frontiers (current)

## Which manuscript this release corresponds to

This is the deposit for the Frontiers in Pharmacology Original Research submission:

> OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening
> Manuscript ID 2032864, Frontiers in Pharmacology — Drugs Outcomes Research and Policies

Archived at DOI **10.5281/zenodo.23439606** (concept DOI 10.5281/zenodo.23143344).

Every number reported in the current manuscript can be regenerated from this tree with the
scripts listed below. The repository **does not** describe a BMC Bioinformatics submission;
the earlier BMC-era files are archived under `outputs/archive/bmc_submission/` and are
historical only.

## Current results (matching the manuscript)

- **1,933** registry-matched pairs with a graded DDInter severity (Major/Moderate/Minor).
  **1,502 (77.7%)** were graded lower by absorption-aware assessment; **1,341/1,757 (76.3%)**
  among assessed pairs; **1,206/1,502 (80.3%)** of downgrades involved low-tier ophthalmic agents.
- **118-case author-derived reference set:** 101/118 exact agreement under the frozen labels
  (0.856; kappa 0.779); 104/118 after three post-lock corrections (0.881; kappa 0.818; sensitivity analysis).
- **40-case frozen blind set:** 36/40 (0.900); the 20 B-only cases were 18/20 frozen and
  20/20 corrected, descriptive and not development-free.
- **92-case semi-independent audit:** 62/92 (0.674); high-risk sensitivity 8/25 (0.320),
  the principal limitation. The re-derived labels give 61/92 (0.663) and 8/29 (0.276).
- **30 disagreements:** author classification 21 route-consistent / 5 unsupported / 4 over-grades;
  an independent non-author ophthalmologist agreed with 14/30 (14/28 within the three author
  classes; kappa 0.271) and classified 14 author route-consistent cases as unsupported.

## How to reproduce the reported results

```bash
pip install -e .          # or: pip install -r requirements.txt

python -m pytest tests/ -q
python scripts/recompute_all_reported_numbers.py   # -> outputs/recomputed/numbers.json
python scripts/revision_r1_stats.py                # -> outputs/recomputed/revision_r1_stats.json
python scripts/audit_ddinter_denominator.py        # 4,546 / 2,613 / 1,933
python scripts/path_attribution_audit.py           # 504 / 507 / 746 / 176 on the 1,933 pairs
python scripts/demo_pipeline.py                    # deterministic smoke test, no API key
```

## What is in this release

| path | contents |
|---|---|
| `outputs/deliverables/frontiers/` | the submission package: clean and marked manuscript, supplement, response letters, cover letter, scope statement, Figures 1–6 |
| `outputs/paper/` | manuscript source of record |
| `outputs/deliverables/supplementary_files/` | supplement source and build outputs |
| `data/seed/`, `data/curation/`, `data/ddinter/` | registries, tier evidence, DDInter severity tables |
| `configs/` | rules, class matrix, drug classes, flag catalog, prompts |
| `scripts/`, `tests/` | evaluation, audit, regeneration and test code |
| `outputs/archive/` | superseded versions, including the earlier BMC-era package; not current |

## Licensing

Code is Apache-2.0. Original data and configuration are CC BY 4.0. The bundled DDInter
severity tables remain under DDInter's **CC BY-NC-SA 4.0** terms and are included for
research reproducibility only. See the component-licensing section of `LICENSE`.

## Historical note

Versions `v1.x` were prepared for an earlier BMC Bioinformatics submission and are retained
only in the archive/history. They are superseded by `v3.0-frontiers` and must not be cited
as the current manuscript.
