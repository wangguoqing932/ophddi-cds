# table5_audit_strata

| stratum | n | system agreement |
|---|---|---|
| All 92 (vs absorption-corrected gold) | 92 | 62 (0.674) |
| All 92 (vs uncorrected DDInter severity) | 92 | 34 (0.370) |
| Absorption-corrected cases (gold set to low) | 30 | 28 (0.933) |
| Kept cases (third-party severity, gold = DDInter) | 62 | 34 (0.548) |

| disagreement direction (vs corrected gold) | n |
|---|---|
| high->low | 8 |
| high->medium | 9 |
| medium->low | 9 |
| medium->high | 2 |
| low->medium | 1 |
| low->high | 1 |
| **total disagreements** | **30** |

Note: values reflect the corrected flurbiprofen absorption tier. The four over-alerts
(system grade above gold) are apraclonidine x midazolam, apraclonidine x loperamide,
tacrolimus x ibuprofen and bromfenac x enalapril. The 62-case "kept" stratum is the
subset whose gold is the third-party DDInter severity, so it is the only stratum free
of the system's own absorption assumption; the 0.548 figure there should be read as the
audit-set headline rather than 0.674. Of those 62 cases, the deposited BM25 retrieval
returns the pair's own DDInter statement within the top-3 passages for 19, so the
baseline figures on this stratum are partly confounded (see
`scripts/naive_rag_leakage_audit.py`).
