# Figure Legends (v3.1 — revised after Round-1 review; verified against source data)

---

**Figure 1. System architecture of the ophthalmic drug–drug interaction clinical decision support system.**

The system evaluates drug–drug interaction (DDI) risk between ophthalmic topical drugs (113 agents) and systemic medications (232 agents) through a three-layer deterministic cascade: **(a)** the L1 rule engine (40 citation-verified mechanism rules plus 3 patient-factor policies, `configs/rules.yaml`), **(b)** the L2 class-matrix layer (20 ophthalmic × 37 systemic drug classes, 82 cells with absorption-scaled upgrades, `configs/class_matrix.yaml`), and **(c)** the L3 G19 hard constraint (low/very-low systemic absorption with no rule hit → low), with a traceable default of low risk for known drugs without rule or matrix signals; unknown or ambiguous medications are rejected with an explicit error rather than scored. The evidence store (1,307 verified evidence chunks; LightRAG index) supports retrieval-augmented baselines and the interactive screening interface; the production path (`full_system`) is fully deterministic with zero LLM calls, and every decision returns matched rule IDs and a decision path for clinical auditability.

Abbreviations: L1/L2/L3, cascade layers 1–3; G19, gate 19 hard constraint; DDI, drug–drug interaction; KG, knowledge graph.

---

**Figure 2. Performance comparison across four methods on the L1 literature-derived gold (118 cases).**

Grouped bars show four metrics — high-risk sensitivity, high-risk specificity, high-risk F1 and Cohen's kappa — for the deterministic system (`full_system`) versus three LLM baselines: `pure_llm` (single LLM call with a domain-general system prompt and no retrieved evidence), `naive_rag` (BM25 evidence retrieval) and `lightrag` (knowledge-graph context). Values are means over five temperature conditions. `full_system` reaches sensitivity 0.964, specificity 0.989, F1 0.964 and kappa 0.857, against 0.779 / 0.936 / 0.785 / 0.603 for `lightrag`, 0.771 / 0.542 / 0.476 / 0.256 for `pure_llm` and 0.757 / 0.462 / 0.434 / 0.182 for `naive_rag`. Exact three-level accuracy was 0.907 (107/118; Wilson 95% CI 0.841–0.947) for `full_system`. `full_system` shows zero variance across temperature conditions because it makes no model call (Section 3.6).

Abbreviations: LLM, large language model; BM25, Best Matching 25 retrieval; F1, harmonic mean of precision and recall at the high-risk threshold; kappa, Cohen's kappa.

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
