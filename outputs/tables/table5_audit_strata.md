| Reference labels | Subset | n | Agreement | Sensitivity (high) | Specificity (high) | Kappa |
|---|---|---|---|---|---|---|
| applied | all | 92 | 0.674 (62/92) | 0.320 (8/25) | 0.970 | 0.428 |
| applied | kept at DDInter (label-independent) | 62 | 0.548 (34/62) | 0.320 (8/25) | 0.946 | 0.343 |
| applied | 26 retrievable cases excluded | 66 | 0.712 (47/66) | 0.200 (3/15) | 0.961 | 0.391 |
| rederived | all | 92 | 0.663 (61/92) | 0.276 (8/29) | 0.968 | 0.434 |
| rederived | kept at DDInter (label-independent) | 62 | 0.597 (37/62) | 0.348 (8/23) | 0.949 | 0.398 |
| rederived | 26 retrievable cases excluded | 66 | 0.697 (46/66) | 0.167 (3/18) | 0.958 | 0.400 |

**Disagreement classification (applied labels).**

| Class | n | Cases |
|---|---|---|
| Route-consistent downgrade | 21 | D3-000, D3-002, D3-005, D3-010, D3-011, D3-013, D3-019, D3-022, D3-025, D3-026, D3-027, D3-028, D3-029, D3-030, D3-033, D3-034, D3-037, D3-040, D3-042, D3-080, D3-085 |
| Unsupported undergrading | 5 | D3-001, D3-004, D3-006, D3-014, D3-018 |
| System over-grading | 4 | D3-035, D3-038, D3-057, D3-063 |

**Independent review of the 30 disagreements (one non-author ophthalmologist, 14 November 2026).**

| Class | Author | Independent |
|---|---:|---:|
| Route-consistent downgrade | 21 | 7 |
| Unsupported undergrading | 5 | 19 |
| System over-grading | 4 | 2 |
| Supported upgrade | — | 2 |

Note: Exact agreement: 14/30 (46.7%); on the 28 cases within the author's three classes, 14/28 (50.0%, kappa 0.271). The reviewer classified 14 of the 21 author route-consistent cases as unsupported, kept all five author unsupported cases as unsupported, and considered two author over-grades to be supported upgrades. The `class` column above is the author classification; the independent classification is in Supplementary Table S2.

**Retrieval overlap (naive_rag, top-3).**

| Subset | n | Cases with the pair's own DDInter statement | Rate |
|---|---|---|---|
| kept at DDInter severity (reference source) | 62 | 19 | 0.306 |
| absorption-corrected (reference label is low) | 30 | 7 | 0.233 |
| all audit cases | 92 | 26 | 0.283 |
