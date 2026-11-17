| Dataset | Label set n | Method | n | Sensitivity (high) | Specificity (high) | F1 (high) | Agree. | Cohen's kappa |
|---|---|---|---|---|---|---|---|---|
| L1, frozen (primary) | 118 | pure_llm | 118 | 0.779 | 0.544 | 0.481 | 0.478 | 0.259 |
| L1, frozen (primary) | 118 | naive_rag | 118 | 0.764 | 0.464 | 0.439 | 0.419 | 0.185 |
| L1, frozen (primary) | 118 | rule_context | 118 | 0.593 | 0.989 | 0.728 | 0.714 | 0.561 |
| L1, frozen (primary) | 118 | full_system | 118 | 0.857 | 0.978 | 0.889 | 0.856 | 0.779 |
| L1, corrected (sensitivity) | 118 | pure_llm | 118 | 0.771 | 0.542 | 0.476 | 0.475 | 0.256 |
| L1, corrected (sensitivity) | 118 | naive_rag | 118 | 0.757 | 0.462 | 0.434 | 0.415 | 0.182 |
| L1, corrected (sensitivity) | 118 | rule_context | 118 | 0.621 | 0.998 | 0.762 | 0.719 | 0.570 |
| L1, corrected (sensitivity) | 118 | full_system | 118 | 0.893 | 0.989 | 0.926 | 0.881 | 0.818 |
| L1, frozen blind (40) | 40 | pure_llm | 40 | 0.855 | 0.552 | 0.562 | 0.560 | 0.360 |
| L1, frozen blind (40) | 40 | naive_rag | 40 | 0.764 | 0.476 | 0.485 | 0.465 | 0.226 |
| L1, frozen blind (40) | 40 | rule_context | 40 | 0.364 | 0.972 | 0.507 | 0.610 | 0.402 |
| L1, frozen blind (40) | 40 | full_system | 40 | 0.818 | 0.966 | 0.857 | 0.900 | 0.848 |
| DDInter audit, applied | 92 | pure_llm | 92 | 0.848 | 0.704 | 0.642 | 0.630 | 0.396 |
| DDInter audit, applied | 92 | naive_rag | 92 | 0.848 | 0.579 | 0.570 | 0.535 | 0.290 |
| DDInter audit, applied | 92 | rule_context | 92 | 0.264 | 0.979 | 0.400 | 0.602 | 0.237 |
| DDInter audit, applied | 92 | full_system | 92 | 0.320 | 0.970 | 0.457 | 0.674 | 0.428 |
| DDInter audit, re-derived | 92 | pure_llm | 92 | 0.786 | 0.711 | 0.651 | 0.630 | 0.398 |
| DDInter audit, re-derived | 92 | naive_rag | 92 | 0.834 | 0.600 | 0.617 | 0.572 | 0.338 |
| DDInter audit, re-derived | 92 | rule_context | 92 | 0.228 | 0.978 | 0.357 | 0.559 | 0.204 |
| DDInter audit, re-derived | 92 | full_system | 92 | 0.276 | 0.968 | 0.410 | 0.663 | 0.434 |
| Configuration 2, L1 (corrected) | 118 | pure_llm | 118 | 0.250 | 1.000 | 0.400 | 0.576 | 0.333 |
| Configuration 2, L1 (corrected) | 118 | naive_rag | 118 | 0.214 | 0.989 | 0.343 | 0.585 | 0.341 |
| Configuration 2, L1 (corrected) | 118 | rule_context | 118 | 0.536 | 1.000 | 0.698 | 0.737 | 0.587 |
| Configuration 2, audit (applied) | 92 | pure_llm | 92 | 0.080 | 1.000 | 0.148 | 0.609 | 0.317 |
| Configuration 2, audit (applied) | 92 | naive_rag | 92 | 0.400 | 1.000 | 0.571 | 0.728 | 0.553 |
| Configuration 2, audit (applied) | 92 | rule_context | 92 | 0.240 | 1.000 | 0.387 | 0.674 | 0.428 |

Note: 10-token rows (L1 and audit) are means over the five temperature conditions; full_system is deterministic (SD = 0). Configuration 2 rows use the majority vote over five repeats at temperature 0.0 with the reasoning model (glm-5.3-flash, max_tokens 3000). The frozen-label rows are the primary analysis; corrected-label rows are the sensitivity analysis (frozen labels: `gold_pre_errata` in `outputs/recomputed/l1_gold_provenance.csv`, falling back to `gold_current` when empty; the `gold_risk` field in the prediction files stores the corrected labels). The frozen blind row is the 40-case subset; both B01-B20 and C01-C20 were reviewed during development (C entered the class-matrix loop in v2.1-v2.3; B informed rule-gap diagnosis and matrix design), so neither half is development-free. `rule_context` is the method stored as `lightrag` in the deposited code. Configuration 1 rule_context was re-run with corrected exposure bands and absorption gate; pure_llm and naive_rag were not re-run and share the original system prompt, which lists dexamethasone as >50%. Configuration 2 rule_context uses the pre-correction prompt and is not directly comparable to the corrected configuration-1 rule_context.
