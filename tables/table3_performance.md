# table3_performance

| dataset_id | setting | method | n | sensitivity_high | specificity_high | f1_high | accuracy_3level | cohens_kappa |
|---|---|---|---|---|---|---|---|---|
| blind_l1 | 10-token | pure_llm | 118 | 0.771 | 0.542 | 0.476 | 0.475 | 0.256 |
| blind_l1 | 10-token | naive_rag | 118 | 0.757 | 0.462 | 0.434 | 0.415 | 0.182 |
| blind_l1 | 10-token | lightrag | 118 | 0.779 | 0.936 | 0.785 | 0.737 | 0.603 |
| blind_l1 | 10-token | full_system | 118 | 0.964 | 0.989 | 0.964 | 0.907 | 0.857 |
| blind_l1 | 3000-token | pure_llm | 118 | 0.250 | 1.000 | 0.400 | 0.576 | 0.333 |
| blind_l1 | 3000-token | naive_rag | 118 | 0.214 | 0.989 | 0.343 | 0.585 | 0.341 |
| blind_l1 | 3000-token | lightrag | 118 | 0.536 | 1.000 | 0.698 | 0.737 | 0.587 |
| blind_v3_ddinter | 10-token | pure_llm | 92 | 0.848 | 0.704 | 0.642 | 0.630 | 0.396 |
| blind_v3_ddinter | 10-token | naive_rag | 92 | 0.848 | 0.579 | 0.570 | 0.535 | 0.290 |
| blind_v3_ddinter | 10-token | lightrag | 92 | 0.264 | 0.949 | 0.377 | 0.591 | 0.220 |
| blind_v3_ddinter | 10-token | full_system | 92 | 0.320 | 0.955 | 0.444 | 0.674 | 0.428 |
| blind_v3_ddinter | 3000-token | pure_llm | 92 | 0.080 | 1.000 | 0.148 | 0.609 | 0.317 |
| blind_v3_ddinter | 3000-token | naive_rag | 92 | 0.400 | 1.000 | 0.571 | 0.728 | 0.553 |
| blind_v3_ddinter | 3000-token | lightrag | 92 | 0.240 | 1.000 | 0.387 | 0.674 | 0.428 |
Note: exact accuracy is on the three-level scale; **10-token** denotes the primary comparison (non-reasoning model, 10-token cap, one call per case); **3000-token** denotes the re-run (reasoning model glm-5.3-flash, 3000-token budget, temperature 0.0, majority vote over five repeated samples). `full_system` is deterministic and therefore identical under both settings (SD = 0). Sensitivities are computed against each dataset's gold; the 3000-token baselines assign high risk far more rarely, which raises specificity to ~1.000 while depressing sensitivity.
