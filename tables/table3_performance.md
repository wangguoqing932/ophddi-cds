# table3_performance

| dataset_id | method | n | sensitivity_high | specificity_high | f1_high | accuracy_3level | cohens_kappa |
|---|---|---|---|---|---|---|---|
| blind_l1 | pure_llm | 118 | 0.771 | 0.542 | 0.476 | 0.475 | 0.256 |
| blind_l1 | naive_rag | 118 | 0.757 | 0.462 | 0.434 | 0.415 | 0.182 |
| blind_l1 | lightrag | 118 | 0.779 | 0.936 | 0.785 | 0.737 | 0.603 |
| blind_l1 | full_system | 118 | 0.964 | 0.989 | 0.964 | 0.907 | 0.857 |
| blind_v3_ddinter | pure_llm | 92 | 0.848 | 0.704 | 0.642 | 0.630 | 0.396 |
| blind_v3_ddinter | naive_rag | 92 | 0.848 | 0.579 | 0.570 | 0.535 | 0.290 |
| blind_v3_ddinter | lightrag | 92 | 0.264 | 0.949 | 0.377 | 0.591 | 0.220 |
| blind_v3_ddinter | full_system | 92 | 0.320 | 0.955 | 0.444 | 0.674 | 0.428 |

Note: exact accuracy is on the three-level scale (high/medium/low); LLM outputs that failed parsing were scored as errors (none occurred). Mean over five temperature conditions; full_system SD = 0 (deterministic).
