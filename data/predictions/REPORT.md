# Multiseed Per-Dataset Evaluation — Current Summary

**Generated:** 2026-11-12. This file replaces the 2026-08-03 working report, which is superseded.

**Authoritative sources:** `outputs/tables/table3_performance.md`, `outputs/recomputed/numbers.json`, and `outputs/recomputed/revision_r1_stats.json`. The prediction rows remain in `outputs/multiseed_per_dataset/*.jsonl`.

## L1 reference set (118 cases)

| Labels | Method | Agreement | Sensitivity | Specificity | Kappa |
|---|---|---:|---:|---:|---:|
| Frozen (primary) | `pure_llm` | 0.478 | 0.779 | 0.544 | 0.259 |
| Frozen (primary) | `naive_rag` | 0.419 | 0.764 | 0.464 | 0.185 |
| Frozen (primary) | `rule_context` | 0.714 | 0.593 | 0.989 | 0.561 |
| Frozen (primary) | `full_system` | 0.856 | 0.857 | 0.978 | 0.779 |
| Corrected (sensitivity) | `pure_llm` | 0.475 | 0.771 | 0.542 | 0.256 |
| Corrected (sensitivity) | `naive_rag` | 0.415 | 0.757 | 0.462 | 0.182 |
| Corrected (sensitivity) | `rule_context` | 0.719 | 0.621 | 0.998 | 0.570 |
| Corrected (sensitivity) | `full_system` | 0.881 | 0.893 | 0.989 | 0.818 |

Frozen blind subset (40 cases): `full_system` 0.900 (36/40), sensitivity 0.818, specificity 0.966; corrected labels 0.975 (39/40). Within it, B01-B20 (never used in development) scored 18/20 frozen and 20/20 corrected; C01-C20 (class-matrix development loop v2.1-v2.3) scored 18/20 and 19/20.

## DDInter audit (92 cases)

| Labels | Method | Agreement | Sensitivity | Specificity | Kappa |
|---|---|---:|---:|---:|---:|
| Applied | `pure_llm` | 0.630 | 0.848 | 0.704 | 0.396 |
| Applied | `naive_rag` | 0.535 | 0.848 | 0.579 | 0.290 |
| Applied | `rule_context` | 0.602 | 0.264 | 0.979 | 0.237 |
| Applied | `full_system` | 0.674 | 0.320 | 0.970 | 0.428 |
| Re-derived | `pure_llm` | 0.630 | 0.786 | 0.711 | 0.398 |
| Re-derived | `naive_rag` | 0.572 | 0.834 | 0.600 | 0.338 |
| Re-derived | `rule_context` | 0.559 | 0.228 | 0.978 | 0.204 |
| Re-derived | `full_system` | 0.663 | 0.276 | 0.968 | 0.434 |

## Configuration 2 (majority vote over five repeats)

| Dataset | Method | Agreement | Sensitivity | Specificity | Kappa |
|---|---|---:|---:|---:|---:|
| L1 (corrected) | `pure_llm` | 0.576 | 0.250 | 1.000 | 0.333 |
| L1 (corrected) | `naive_rag` | 0.585 | 0.214 | 0.989 | 0.341 |
| L1 (corrected) | `rule_context` | 0.737 | 0.536 | 1.000 | 0.587 |
| Audit (applied) | `pure_llm` | 0.609 | 0.080 | 1.000 | 0.317 |
| Audit (applied) | `naive_rag` | 0.728 | 0.400 | 1.000 | 0.553 |
| Audit (applied) | `rule_context` | 0.674 | 0.240 | 1.000 | 0.428 |

## Key registry counts

- 1,933 DDInter-matched pairs: 504 rule, 507 defined matrix cell, 746 G19, 176 default (unassessed); assessed 1,757, of which 1,341 (76.3%) downgraded; total downgrades 1,502 (77.7%).
- Full 26,216-pair grid: rule 3,079 (11.7%), matrix 6,743 (25.7%), G19 11,238 (42.9%), default 5,156 (19.7%).

## Baseline prompt caveat

Configuration 1 `rule_context` was re-run with corrected exposure bands (high >=10%, medium 1-10%, low <1%) and the absorption gate. `pure_llm` and `naive_rag` were not re-run and share the original system prompt, which lists dexamethasone as >50%. Configuration 2 `rule_context` uses the pre-correction prompt and is not directly comparable to the corrected configuration-1 rule_context. The deterministic cascade is unaffected. See manuscript Section 2.4 and Supplementary Text S3.
