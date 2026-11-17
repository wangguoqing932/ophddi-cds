**A. Retrieval overlap (naive_rag, top-3).**

| Subset | n | Cases with the pair's own DDInter statement | Rate |
|---|---|---|---|
| kept at DDInter severity (reference source) | 62 | 19 | 0.306 |
| absorption-corrected (reference label is low) | 30 | 7 | 0.233 |
| all audit cases | 92 | 26 | 0.283 |

**B. All methods with and without the 26 retrievable cases (mean over five temperature conditions).**

| Labels | Subset | Method | n | Agreement | Sensitivity (high) | Specificity (high) |
|---|---|---|---|---|---|---|
| applied | all 92 | full_system | 92 | 0.674 | 0.320 | 0.970 |
| applied | all 92 | pure_llm | 92 | 0.630 | 0.848 | 0.704 |
| applied | all 92 | naive_rag | 92 | 0.535 | 0.848 | 0.579 |
| applied | all 92 | rule_context | 92 | 0.602 | 0.264 | 0.979 |
| applied | 26 excluded | full_system | 66 | 0.712 | 0.200 | 0.961 |
| applied | 26 excluded | pure_llm | 66 | 0.661 | 0.813 | 0.733 |
| applied | 26 excluded | naive_rag | 66 | 0.524 | 0.760 | 0.647 |
| applied | 26 excluded | rule_context | 66 | 0.664 | 0.133 | 0.973 |
| rederived | all 92 | full_system | 92 | 0.663 | 0.276 | 0.968 |
| rederived | all 92 | pure_llm | 92 | 0.630 | 0.786 | 0.711 |
| rederived | all 92 | naive_rag | 92 | 0.572 | 0.834 | 0.600 |
| rederived | all 92 | rule_context | 92 | 0.559 | 0.228 | 0.978 |
| rederived | 26 excluded | full_system | 66 | 0.697 | 0.167 | 0.958 |
| rederived | 26 excluded | pure_llm | 66 | 0.652 | 0.733 | 0.738 |
| rederived | 26 excluded | naive_rag | 66 | 0.561 | 0.744 | 0.667 |
| rederived | 26 excluded | rule_context | 66 | 0.618 | 0.111 | 0.971 |

`pure_llm` and `rule_context` have no DDInter-statement retrieval channel; their rows are reported for consistency. The 26 cases are those whose own DDInter statement appears in the naive_rag top-3.

