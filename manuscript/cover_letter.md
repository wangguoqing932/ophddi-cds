# Cover Letter

Dear Editor,

I am pleased to submit our manuscript entitled "**OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening**" for consideration in the *BMC Bioinformatics*.

**Context and importance.** Ophthalmic topical medications are among the most widely prescribed drugs worldwide, yet a substantial subset can reach clinically meaningful systemic exposure (e.g., timolol, atropine, dexamethasone). Drug-drug interactions (DDIs) between ophthalmic drops and systemic medications are systematically under-screened in clinical practice and underestimated by general-purpose DDI databases, which rate severity from systemic administration without encoding ophthalmic absorption pharmacology. Through a full audit of all 1,933 registry-matched DDInter pairs, we quantify that divergence for the first time: 75.0% of the pairs are graded lower once ophthalmic absorption is considered (346 of them downgraded from high), and 77.0% of those downgrades follow from a single mechanism, low systemic absorption from the topical route.

**What the work provides.** We present OphDDI-CDS, a deterministic three-layer cascade (40 citation-verified rules; an absorption-scaled 20 x 37 class matrix; a hard-constraint layer) that produces traceable risk grades with zero LLM dependency, zero variance, and millisecond inference. On 118 literature-derived validation cases, the system achieved 0.915 exact accuracy and kappa = 0.870, outperforming three LLM baselines (0.415-0.741 accuracy) with significant exact McNemar tests, and showed zero variance across five temperature conditions (SD = 0.000) versus 0.014–0.024 for the LLM baselines on the same 118 cases. A blinded two-expert assessment then shows that clinical judgment diverges from evidence-graded assessment independently of our system: the two ophthalmologists agreed with each other (kappa 0.846) but graded most cases one tier lower, and because the system reproduced its gold on all 12 cases, their agreement with the gold was numerically identical to their agreement with the system. The manuscript's thesis follows from these three observations taken together: ophthalmic DDI risk currently lacks a shared grading standard, database severity is therefore not a valid ophthalmic ground truth, and evaluation in this domain should measure that disagreement rather than assume any one perspective is correct.

**Why it fits the Journal.** *BMC Bioinformatics* publishes computational methods, software, and knowledge-representation approaches across the life sciences, with a strong emphasis on reproducibility and openly available implementations. Our manuscript contributes a fully specified, zero-LLM knowledge representation for a pharmacology domain: 40 citation-verified mechanism rules, an absorption-scaled 20 x 37 class matrix, and a hard-constraint layer, together with a deterministic inference engine in which every decision returns its matched rule IDs and evidence chain. We further contribute: (i) a reproducible evaluation protocol that compares deterministic knowledge engineering against three LLM baselines under five temperature conditions; (ii) an external audit against 1,933 registry-matched DDInter pairs that quantifies where systemic-route severity diverges from absorption-adjusted ophthalmic risk; and (iii) a complete release package with a zero-configuration web interface, allowing the method to be re-run and extended to other specialty-systemic interaction domains.

The manuscript has not been published or submitted elsewhere; all authors have approved the submission. We declare no conflicts of interest.

We would be grateful for your consideration.

Sincerely,

**Guoqing Wang, M.M.**¹², **Xianglong Yi, M.D., Ph.D.**¹²*

¹ Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, China

² Xinjiang Medical University, Urumqi, China

**Corresponding author.** Email: yixianglong1010@163.com
