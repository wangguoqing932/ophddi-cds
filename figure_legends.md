# Figure Legends (v4.0 — regenerated with the manuscript; verified against source data)

---

**Figure 1. Absorption-first cascade for ophthalmic–systemic drug–drug interaction screening.**

The system evaluates drug–drug interaction (DDI) risk between ophthalmic topical drugs (113 agents, each carrying one of six systemic-absorption tiers) and systemic medications (232 agents, with mechanism flags and drug classes) through a three-layer deterministic cascade shown as three numbered rows in the centre column: **01**, the L1 rule engine — 40 mechanism rules, each carrying at least one source record, plus 3 patient-factor policies, matched by entity-flag predicates with MAX-MATCH semantics and not gated on absorption (12.0% of registry pairs); **02**, the L2 class matrix — 21 ophthalmic row keys × 40 systemic column keys (34 columns in use), 104 cells of which 83 carry an actionable grade and 21 are marked "none", with an absorption-scaling step that forces low/very-low tiers to low inside this layer only (68.7%); and **03**, the L3 G19 hard constraint — low/very-low absorption with no rule or matrix signal → low (12.2%, plus a 7.1% explicit default-low path for pairs with no signal), while unknown medications are rejected with an explicit error rather than scored. The final grade is the maximum of the rule and matrix layers. The knowledge base (1,307 curated evidence chunks; A 53, B 191, C 215, D 584, E 264) supplies rule source records and matrix-cell provenance and supports the retrieval baselines and the interactive interface; the production path (`full_system`) makes zero LLM calls, and every decision returns matched rule IDs and a decision path for clinical auditability. Layer shares are measured over all 26,216 registry pairs (deposited path-attribution audit) and are drawn once, as a single stacked bar, rather than repeated per row. The lower band reproduces the released class matrix cell by cell (rows ordered by the number of cells they define; filled squares mark graded cells and outlined squares the 21 cells recorded as "none", with the 610 undefined cells left blank). The figure is drawn with Matplotlib from the deposited configuration; the source-data file is `outputs/figures/source_data/figure1_source.csv`.

Abbreviations: L1/L2/L3, cascade layers 1–3; G19, gate 19 hard constraint; DDI, drug–drug interaction.

---

**Figure 2. Performance comparison under two output budgets (L1 gold, 118 cases).**

Grouped bars show four metrics — high-risk sensitivity, high-risk specificity, high-risk F1 and Cohen's κ — for the deterministic cascade (`full_system`) and three LLM baselines: `pure_llm` (single LLM call with a domain-general system prompt, no retrieved evidence), `naive_rag` (BM25 evidence retrieval) and `lightrag` (knowledge-graph context). **Panel (a)** is the primary comparison: a non-reasoning model with a 10-token output cap, mean over five temperature conditions. **Panel (b)** repeats the three LLM baselines with a reasoning model (glm-5.3-flash), a 3000-token budget, a fixed temperature of 0.0 and the majority vote over five repeated samples; the cascade is unchanged because it makes no model call. In panel (a) the baselines reach sensitivities of 0.757–0.779; in panel (b) sensitivity falls to 0.214–0.536 while specificity rises to approximately 1.000, because the baselines adopt a conservative rarely-high-risk policy that inflates exact accuracy on a gold set dominated by low and medium grades. The cascade returns 0.964 sensitivity, 0.989 specificity and 0.857 κ in both panels, with exact three-level accuracy 0.907 (107/118; Wilson 95% CI 0.841–0.947); baseline accuracy was 0.415–0.737 in panel (a) and 0.576–0.737 in panel (b).

Abbreviations: LLM, large language model; BM25, Best Matching 25 retrieval; κ, Cohen's kappa; CI, confidence interval.

---

**Figure 3. Expert agreement and per-case grades (two ophthalmologists, 12 cases).**

**Panel (a)** shows, for five comparisons, Cohen's κ (unweighted), quadratic-weighted κ on the ordinal scale low < medium < high, and raw agreement: inter-rater (expert 1 vs expert 2: agreement 11/12, κ = 0.840, weighted 0.875); each expert against the grade displayed on the questionnaire (expert 1: 2/12, κ = −0.176, weighted 0.355; expert 2: 1/12, κ = −0.257, weighted 0.313); and each expert against the proposed gold (expert 1: 4/12, κ = 0.020, weighted 0.473; expert 2: 3/12, κ = −0.091, weighted 0.438). **Panel (b)** shows the per-case grades: the proposed gold (which coincides with the deposited deterministic engine grade on all 12 cases), the grade displayed on the questionnaire (which differs from the engine for R10 and R11, where a class-level conservative hint, medium, was displayed instead of the engine's low), and both experts' ratings. The disagreement is one-directional: against the gold, all 8 of expert 1's discordant ratings and 8 of expert 2's 9 discordant ratings are lower than the gold. The weighted kappas are computed on the ordinal scale low < medium < high by `scripts/stats_tests.py`, whose self-test reproduces the reported values; the figure data are deposited as `outputs/figures/source_data/figure3_source.csv` and `figure3_expert_agreement.csv`. The exercise is a grade review between non-independent participants (one expert is a study-team member) and is reported as a perspective comparison, not a validation (Sections 2.5 and 3.8).

Abbreviations: E1/E2, expert 1/2; κ, Cohen's kappa.

---

**Figure 4. Worked demo case: ophthalmic × systemic risk evaluation (Timolol × Atenolol).**

Panel a shows the rule signals triggered for the demo case (glaucoma patient on topical timolol with oral atenolol): `additive_beta_blockade` (high) and `systemic_absorption_high_risk`, with severity weights. Panel b shows the final risk distribution across the curated demo cases (3 high / 3 medium / 2 low). The cascade output (high) is fully traceable: matched rule IDs, decision path (`rule`), and the clinical recommendation (monitor HR/BP; consider beta1-selective agent with punctal occlusion) are returned to the clinician.

Abbreviations: HR, heart rate; BP, blood pressure.

---

**Figure 5. Step-by-step reasoning trace across the cascade layers (Timolol × Atenolol).**

The scatter plot shows per-step latency (milliseconds) of the five cascade steps: L1 rule matching (matched `additive_beta_blockade`, severity high), L2 class-matrix upgrade check (non-selective beta-blocker with high systemic absorption → upgrade applied), L3 G19 hard-constraint check (not triggered; absorption = high), MAX-MATCH decision (final = high), and LLM arbitration (not used in the deterministic path, 0 LLM calls). Total inference time is approximately 2 ms per case on a single CPU, enabling real-time screening.

Abbreviations: L1/L2/L3, cascade layers; G19, hard constraint; ms, milliseconds.
