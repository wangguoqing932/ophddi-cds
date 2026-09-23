# Supplementary Material

## S1. Evidence base summary

- Total verified evidence chunks: 1,307 (all approved release)
- Evidence levels: A (regulatory) 53, B (meta-analysis) 191, C (original study) 215, D (in vitro or animal) 584, E (mechanism inference) 264
- Ophthalmic agents: 113; systemic medications: 232

## S2. Rule citation verification

- Rules: 40; all passed three-source cross-check (Crossref, OpenAlex, PubMed)
- Citation policy entries: 43; policy errors: 0
- Retraction screening: no retracted references identified

## S3. Supplementary tables

**Table S1. Registry summary.**

**Table S1.**


| entity_type | count | with_flags | with_drugbank_ids |
|---|---|---|---|
| ophthalmic_drugs | 113 | 113 | 103 |
| systemic_drugs | 232 | 232 | 218 |


**Table S2.**


| rule_id | severity | risk_type | entity_a_flags | entity_b_flags | match |
|---|---|---|---|---|---|
| additive_beta_blockade | high | pharmacodynamic_cardiovascular | beta_blocker|systemic_absorption_high | beta_blocker_systemic | all |
| beta_blocker_ccb_additive | high | pharmacodynamic_cardiovascular | beta_blocker|systemic_absorption_high | l_type_calcium_channel_blocker | all |
| beta_blocker_digoxin_additive | high | pharmacodynamic_cardiovascular | beta_blocker|systemic_absorption_high | na_k_atpase_inhibitor | all |
| additive_alpha2_cns_depression | high | pharmacodynamic_cns | alpha2_agonist | cns_depressant | any |
| additive_anticholinergic_effects | medium | pharmacodynamic_anticholinergic | anticholinergic | anticholinergic_systemic | any |
| additive_corticosteroid_iop | medium | pharmacodynamic_ocular_hypertension | corticosteroid | corticosteroid_systemic | any |
| additive_nsaid_bleeding | medium | pharmacodynamic_hemorrhagic | nsaid | anticoagulant | any |
| sympathomimetic_alpha_interaction | medium | pharmacodynamic_cardiovascular | sympathomimetic | antihypertensive | any |
| qt_prolongation_risk | low | pharmacodynamic_cardiotoxic | fluoroquinolone | qt_prolonging | any |
| pga_antiplatelet_bleeding | low | pharmacodynamic_hemorrhagic | prostaglandin_analog | antiplatelet | any |
| cai_diuretic_metabolic_acidosis | medium | pharmacokinetic_metabolic | cai_topical | diuretic | any |
| cai_topiramate_acidosis | medium | pharmacokinetic_metabolic | cai_topical | cai_systemic | any |
| dexamethasone_cyp3a4_induction | medium | pharmacokinetic_cyp3a4 | corticosteroid|systemic_absorption_high | cyp3a4_substrate | all |
| topical_corticosteroid_cyp3a4_induction | low | pharmacokinetic_cyp3a4 | corticosteroid | cyp3a4_substrate | any |
| systemic_absorption_high_risk | low | systemic_absorption | systemic_absorption_high | beta_blocker_systemic | any |
| systemic_absorption_moderate_risk | low | systemic_absorption | systemic_absorption_medium | narrow_therapeutic_index | any |
| p_gp_mediated_absorption | low | pharmacokinetic_transporter | p_gp_substrate | p_gp_inhibitor | any |
| calcineurin_inhibitor_cyp3a4 | low | pharmacokinetic_cyp3a4 | calcineurin_inhibitor | cyp3a4_inhibitor | any |
| macrolide_cyp3a4_inhibition | low | pharmacokinetic_cyp3a4 | macrolide | cyp3a4_substrate | any |
| azole_cyp3a4_inhibition | low | pharmacokinetic_cyp3a4 | azole | cyp3a4_substrate | any |
| sympathomimetic_maoi_hypertension | high | pharmacodynamic_cardiovascular | sympathomimetic | maoi | any |
| beta_blocker_beta2_agonist_antagonism | high | pharmacodynamic_respiratory | beta_blocker | beta2_adrenergic_agonist | any |
| immunosuppressant_nsaid_nephrotoxicity | medium | pharmacodynamic_renal | calcineurin_inhibitor | cox1_cox2_inhibitor | any |
| fluoroquinolone_corticosteroid_tendon | low | pharmacodynamic_musculoskeletal | fluoroquinolone | corticosteroid_systemic | any |
| nsaid_antihypertensive_antagonism | high | pharmacodynamic_cardiovascular | nsaid | antihypertensive | any |
| nsaid_diuretic_antagonism | medium | pharmacodynamic_cardiovascular | nsaid | ncc_inhibitor|nkcc2_inhibitor | any |
| antibiotic_warfarin_enhancement | low | pharmacokinetic_anticoagulation | antibiotic | narrow_therapeutic_index|vitamin_k_epoxide_reductase_inhibitor | all |
| beta_blocker_cyp2d6_metabolism | medium | pharmacokinetic_cyp2d6 | beta_blocker | cyp2d6_inhibitor | any |
| nsaid_acei_arb_antagonism | medium | pharmacodynamic_cardiovascular | nsaid | ace_inhibitor|angiotensin_ii_receptor_antagonist | any |
| corticosteroid_nti_interaction | medium | pharmacodynamic_endocrine | corticosteroid | narrow_therapeutic_index | any |
| sympathomimetic_tca_hypertension | high | pharmacodynamic_cardiovascular | sympathomimetic | net_inhibitor | any |
| anticholinergic_qt_prolongation | medium | pharmacodynamic_cardiotoxic | anticholinergic | qt_prolonging | any |
| moderate_abs_antiplatelet | low | pharmacodynamic_hemorrhagic | systemic_absorption_medium | antiplatelet | any |
| moderate_abs_beta_blocker | medium | pharmacodynamic_cardiovascular | systemic_absorption_medium | beta_blocker_systemic | any |
| moderate_abs_anticoagulant | low | pharmacodynamic_hemorrhagic | systemic_absorption_medium | anticoagulant | any |
| moderate_abs_cyp2d6 | low | pharmacokinetic_cyp2d6 | systemic_absorption_medium | cyp2d6_substrate | any |
| moderate_abs_diuretic | low | pharmacokinetic_metabolic | systemic_absorption_medium | diuretic | any |
| alpha2_agonist_antiplatelet | low | pharmacodynamic_hemorrhagic | alpha2_agonist | antiplatelet | any |
| low_abs_antiplatelet | low | pharmacodynamic_hemorrhagic | systemic_absorption_low | antiplatelet | any |
| low_abs_anticoagulant | low | pharmacodynamic_hemorrhagic | systemic_absorption_low | anticoagulant | any |


**Table S3.**


| dataset_id | method | n | sensitivity_high | specificity_high | f1_high | accuracy_3level | cohens_kappa |
|---|---|---|---|---|---|---|---|
| blind_l1 | pure_llm | 118 | 0.771 | 0.542 | 0.476 | 0.475 | 0.256 |
| blind_l1 | naive_rag | 118 | 0.757 | 0.462 | 0.434 | 0.415 | 0.182 |
| blind_l1 | lightrag | 118 | 0.793 | 0.936 | 0.794 | 0.741 | 0.609 |
| blind_l1 | full_system | 118 | 1.0 | 0.989 | 0.983 | 0.915 | 0.87 |
| blind_v3_ddinter | pure_llm | 92 | 0.848 | 0.705 | 0.642 | 0.63 | 0.396 |
| blind_v3_ddinter | naive_rag | 92 | 0.848 | 0.579 | 0.57 | 0.535 | 0.29 |
| blind_v3_ddinter | lightrag | 92 | 0.296 | 0.949 | 0.413 | 0.6 | 0.239 |
| blind_v3_ddinter | full_system | 92 | 0.44 | 0.955 | 0.564 | 0.707 | 0.489 |

Note: exact accuracy is on the three-level scale (high/medium/low); LLM outputs that failed parsing were scored as errors (none occurred). Mean over five temperature conditions; full_system SD = 0 (deterministic).


**Table S4.**


| dataset_id | gold_level | count | percentage |
|---|---|---|---|
| blind_l1 | high | 28 | 23.7% |
| blind_l1 | medium | 51 | 43.2% |
| blind_l1 | low | 39 | 33.1% |
| blind_v3_ddinter | high | 25 | 27.2% |
| blind_v3_ddinter | medium | 19 | 20.7% |
| blind_v3_ddinter | low | 48 | 52.2% |
| blind_l1 | total | 118 | 100.0% |
| blind_v3_ddinter | total | 92 | 100.0% |
| all | total | 210 | - |


**Table S5.**


| stratum | n | system agreement |
|---|---|---|
| All 92 (vs corrected gold) | 92 | 65 (0.707) |
| All 92 (vs uncorrected DDInter severity) | 92 | 37 (0.402) |
| Absorption-corrected cases | 30 | 28 (0.933) |
| Kept cases | 62 | 37 (0.597) |

| disagreement direction | n |
|---|---|
| high->low | 6 |
| high->medium | 8 |
| medium->low | 9 |
| medium->high | 2 |
| low->medium | 1 |
| low->high | 1 |
| **total disagreements** | **27** |


**Table S6.**


| case | ophthalmic | systemic | gold | system | expert1 | expert2 |
|---|---|---|---|---|---|---|
| R01 | Ketorolac | Enoxaparin | medium | medium | low | low |
| R02 | Brimonidine | Tramadol | high | high | medium | medium |
| R03 | Dexamethasone | Rifampicin | medium | medium | medium | medium |
| R04 | Atropine | Tramadol | high | high | medium | medium |
| R05 | Scopolamine | Amitriptyline | high | high | medium | medium |
| R06 | Atropine | Oxycodone | high | high | medium | medium |
| R07 | Levofloxacin | Sotalol | low | low | low | low |
| R08 | Betaxolol | Verapamil | medium | medium | medium | high |
| R09 | Ketorolac | Rivaroxaban | medium | medium | low | low |
| R10 | Fluorometholone | Prednisone | low | low | low | low |
| R11 | Fluorometholone | Glimepiride | low | low | low | low |
| R12 | Ketorolac | Warfarin | medium | medium | low | low |

## S4. Figure legends

# Figure Legends (v3.1 — revised after Round-1 review; verified against source data)

---

**Figure 1. System architecture of the ophthalmic drug–drug interaction clinical decision support system.**

The system evaluates drug–drug interaction (DDI) risk between ophthalmic topical drugs (113 agents) and systemic medications (232 agents) through a three-layer deterministic cascade: **(a)** the L1 rule engine (40 citation-verified mechanism rules plus 3 patient-factor policies, `configs/rules.yaml`), **(b)** the L2 class-matrix layer (20 ophthalmic × 37 systemic drug classes, 82 cells with absorption-scaled upgrades, `configs/class_matrix.yaml`), and **(c)** the L3 G19 hard constraint (low/very-low systemic absorption with no rule hit → low), with a traceable default of low risk for known drugs without rule or matrix signals; unknown or ambiguous medications are rejected with an explicit error rather than scored. The evidence store (1,307 verified evidence chunks; LightRAG index) supports retrieval-augmented baselines and the interactive screening interface; the production path (`full_system`) is fully deterministic with zero LLM calls, and every decision returns matched rule IDs and a decision path for clinical auditability.

Abbreviations: L1/L2/L3, cascade layers 1–3; G19, gate 19 hard constraint; DDI, drug–drug interaction; KG, knowledge graph.

---

**Figure 2. Performance comparison across four methods and two validation sets.**

Forest plots show high-risk sensitivity (mean ± SD over five temperature conditions) of the deterministic system (`full_system`) versus three LLM baselines — `pure_llm` (single LLM call with domain-general system prompt, no retrieved evidence), `naive_rag` (BM25 evidence retrieval), and `lightrag` (knowledge-graph context) — on the L1 literature-derived gold (118 cases; panel a) and the DDInter-derived audit set (92 cases; panel b). `full_system` achieves sensitivity 1.000 (28/28) on the L1 set versus 0.793 for lightrag and 0.771 for pure_llm, and 0.440 (11/25) on the audit set; exact three-level accuracy was 0.915 (108/118; Wilson 95% CI 0.851–0.953; Cohen's κ = 0.870, bootstrap CI 0.791–0.947) on L1 and 0.707 (65/92; CI 0.607–0.790; κ = 0.489) on the audit set. Error bars represent SD across temperature conditions; `full_system` shows zero variance (deterministic by construction).

Abbreviations: LLM, large language model; BM25, Best Matching 25 retrieval; SD, standard deviation; κ, Cohen's kappa; CI, confidence interval.

---

**Figure 3. Expert–system agreement and inter-rater reliability (two clinical experts, 12 cases).**

Panel a shows Cohen's κ and raw agreement between the two ophthalmology experts (inter-rater: agreement 91.7%, κ = 0.846) and between each expert and the system (expert 1: agreement 41.7%, κ = 0.125; expert 2: agreement 33.3%, κ = 0.010). Panel b plots agreement against κ for the four pairwise comparisons. The observed expert–system κ values are positive but near zero, and the maximum achievable unweighted κ given the marginal distributions is 0.625; quadratic-weighted κ was 0.500 (expert 1) and 0.461 (expert 2). The disagreement was systematic: expert 1 rated 7 of 12 cases one tier lower and none higher; expert 2 rated 7 lower and 1 higher; neither expert rated any of the four system-high cases as high. Experts judged from clinical practice without mechanism-level assessment (expert feedback). The expert–gold kappas are identical to the expert–system values (0.125 and 0.010) because the system matched its gold on all 12 cases, indicating that the divergence reflects clinical prior versus evidence-graded gold rather than a system-specific artifact. This is reported as a perspective gap, not as evidence of system calibration.

Abbreviations: E1/E2, expert 1/2; κ, Cohen's kappa; sys, system.

---

**Figure 4. Worked demo case: ophthalmic × systemic risk evaluation (Timolol × Atenolol).**

Panel a shows the rule signals triggered for the demo case (glaucoma patient on topical timolol with oral atenolol): `additive_beta_blockade` (high) and `systemic_absorption_high_risk`, with severity weights. Panel b shows the final risk distribution across the curated demo cases (3 high / 3 medium / 2 low). The cascade output (high) is fully traceable: matched rule IDs, decision path (`rule`), and the clinical recommendation (monitor HR/BP; consider beta1-selective agent with punctal occlusion) are returned to the clinician.

Abbreviations: HR, heart rate; BP, blood pressure.

---

**Figure 5. Step-by-step reasoning trace across the cascade layers (Timolol × Atenolol).**

The scatter plot shows per-step latency (milliseconds) of the five cascade steps: L1 rule matching (matched `additive_beta_blockade`, severity high), L2 class-matrix upgrade check (non-selective beta-blocker with high systemic absorption → upgrade applied), L3 G19 hard-constraint check (not triggered; absorption = high), MAX-MATCH decision (final = high), and LLM arbitration (not used in the deterministic path, 0 LLM calls). Total inference time is approximately 2 ms per case on a single CPU, enabling real-time screening.

Abbreviations: L1/L2/L3, cascade layers; G19, hard constraint; ms, milliseconds.


## S5. Evaluation reproducibility

- Five temperature conditions: 0.0, 0.3, 0.6, 0.9, 1.2
- Prediction rows: 9,600; API failures: 0
- Engine/rules/evidence/index SHA-256 fingerprints recorded in the project log
- Statistical tests: exact McNemar, Wilson 95% CI, bootstrap CI for kappa, Clopper-Pearson for proportions

## S6. Abbreviations

DDI, drug-drug interaction; LLM, large language model; BM25, Best Matching 25; CI, confidence interval; SD, standard deviation; KG, knowledge graph; L1/L2/L3, cascade layers; G19, gate 19 hard constraint; κ, Cohen's kappa.
