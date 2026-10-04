# Release notes — v1.1-revision3

## Which manuscript version this corresponds to

This release is the deposit for **round 3** of the manuscript:

> OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening
> Submission ID 363ea8da-e16c-45ce-bbf1-39ff3555463b, BMC Bioinformatics, revision v3.0

Every number reported in that version can be regenerated from this tree with the scripts
listed below. The previous tag `v1.0-submission` remains in the history but corresponds to
an earlier revision that lacks the reasoning-model experiment, the statistical module and
several corrections; it is no longer cited by the manuscript.

## How to reproduce the reported results

```bash
pip install -e .          # or: pip install -r requirements.txt

# test suite (passes on a fresh clone, cp1252 and UTF-8 consoles)
python -m pytest tests/ -q

# every reported figure, regenerated from the deposited data
python scripts/recompute_all_reported_numbers.py     # -> outputs/recomputed/numbers.json

# statistical procedures used in the paper, with a self-test against the reported values
python scripts/stats_tests.py

# expert-review statistics, computed against the grades the experts were shown
python scripts/expert_review_analysis.py

# BM25 gold leakage measurement reported in Section 3.5
python scripts/naive_rag_leakage_audit.py

# 1,933-pair registry audit, and the alternative-tier scenario
python scripts/audit_ddinter_disagreement.py
python scripts/audit_ddinter_disagreement.py --tier-override data/curation/entity_a_candidates.yaml

# deterministic cascade smoke test (no API key, no network)
python scripts/demo_pipeline.py
```

## What is in this release

| path | contents |
|---|---|
| `manuscript/` | the revised manuscript, the marked-changes copy, the round-2 and round-3 response letters |
| `figures/`, `tables/` | publication figures and tables as deposited |
| `supplementary/` | supplementary material, including the per-agent tier table (S5) and evaluation prompts (S3) |
| `data/gold/` | four evaluation gold sets with case-level provenance |
| `data/predictions/` | 9,600 prediction rows for the primary comparison |
| `data/predictions/glm53_baselines/` | **the reasoning-model re-run**: 3,150 raw responses with token usage, parsed labels, metrics, run log |
| `data/registry/`, `data/curation/` | the per-agent absorption tier table and the curation file it is compared against |
| `data/ddinter/` | DDInter 2.0 severity tables (**CC BY-NC-SA 4.0 — see LICENSE**) |
| `configs/` | rules, class matrix, drug classes, flag catalog, prompts |
| `scripts/` | evaluation harness, statistics module, audits, regeneration entry point |
| `tests/` | test suite |
| `audits/` | registry audit outputs, path attribution, tier scenarios, leakage audit, recomputed numbers |

## Known limitations recorded in this release

These are stated in the manuscript and repeated here so that a reader of the deposit alone
sees them:

- **Absorption tiers are a study-team assignment.** The per-agent source column records
  `DrugBank DBxxxxx|PubMed` for all 113 agents, with "PubMed" as a bare word; individual
  pharmacokinetic sources are named for timolol, atropine and dexamethasone only. The
  remaining tiers rest on the curation process, and Table S5 marks each row accordingly.
- **Thirteen agents differ between the registry and the curation file.** The registry
  (`data/seed/entities_a.csv`) is authoritative because the engine loads it; the audit
  re-run under curation-file tiers is deposited as `audits/tier_override_scenario.json`.
- **The expert review is not an independent validation.** The questionnaire displayed both
  the proposed gold and the system grade, and the system reproduced its gold on all 12
  cases, so the expert–gold and expert–system comparisons are not independent. One case
  was fully concordant among both experts, the shown grade and the gold (R07).
- **The naive_rag audit-set result is partly confounded.** 500 of the 1,307 evidence chunks
  are DDInter severity statements, and the top-3 passages contain the pair's own statement
  for 19 of the 62 third-party-graded audit cases.
- **Nine of the 113 "ophthalmic topical" agents are not topically administered** (six
  intravitreal anti-VEGF agents, intraocular acetylcholine, two surgical viscoelastics).
- **The reasoning-model re-run uses one commercial model at one endpoint**, which exposes
  no checkpoint revision.

## Licensing

Code is Apache-2.0. Original data and configuration are CC BY 4.0. **The bundled DDInter
severity tables are not relicensed and remain under DDInter's CC BY-NC-SA 4.0 terms.**
See the component-licensing section of `LICENSE`.
