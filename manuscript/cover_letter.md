# Cover Letter

Dear Editor,

I am pleased to submit our manuscript entitled "**OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening**" for consideration in the *BMC Bioinformatics*.

**Context and importance.** Ophthalmic topical medications are among the most widely prescribed drugs worldwide, yet a substantial subset can reach clinically meaningful systemic exposure (e.g., timolol, atropine, dexamethasone). Drug-drug interactions (DDIs) between ophthalmic drops and systemic medications are systematically under-screened in clinical practice and underestimated by general-purpose DDI databases, which rate severity from systemic administration without encoding ophthalmic absorption pharmacology. Through a full audit of all 1,933 registry-matched DDInter pairs, we quantify that divergence for the first time: 75.3% of the pairs are graded lower once ophthalmic absorption is considered (352 of them downgraded from high), and 80.5% of those downgrades follow from a single mechanism, low systemic absorption from the topical route.

**What the work provides.** We present OphDDI-CDS, a deterministic three-layer cascade (40 mechanism rules, each carrying at least one source record; an absorption-scaled class matrix; a hard-constraint layer) that produces traceable risk grades with zero LLM dependency, zero variance, and millisecond inference. On 118 literature-derived validation cases, the system achieved 0.907 exact accuracy and kappa = 0.857, outperforming three LLM baselines on high-risk sensitivity (0.964, versus 0.757–0.779 for the baselines at the same budget). When the baselines were re-run with a reasoning model and a substantially larger output budget, their label agreement rose but their high-risk sensitivity collapsed to 0.214–0.536 while specificity approached 1.000: given room to reason, general-purpose models adopt a conservative rarely-high-risk policy that scores well on a gold set dominated by low and medium grades. We report both settings side by side. A two-expert grade review then shows that clinical judgment diverges from evidence-graded assessment independently of our system: the two ophthalmologists agreed with each other (kappa 0.846) but did not endorse most grades, and because the system reproduced its gold on all 12 cases, their agreement with the gold was numerically identical to their agreement with the system. The manuscript's thesis follows from these observations taken together: ophthalmic DDI risk currently lacks a shared grading standard, database severity is therefore not a valid ophthalmic ground truth, and evaluation in this domain should measure that disagreement rather than assume any one perspective is correct.

**Why it fits the Journal.** *BMC Bioinformatics* publishes computational methods, software, and knowledge-representation approaches across the life sciences, with a strong emphasis on reproducibility and openly available implementations. Our manuscript contributes a fully specified, zero-LLM knowledge representation for a pharmacology domain: 40 mechanism rules with a documented source record for each, an absorption-scaled drug-class matrix, and a hard-constraint layer, together with a deterministic inference engine in which every decision returns its matched rule IDs and evidence chain. We further contribute: (i) a reproducible evaluation protocol that compares deterministic knowledge engineering against three LLM baselines under two output-budget settings; (ii) an external audit against 1,933 registry-matched DDInter pairs that quantifies where systemic-route severity diverges from absorption-adjusted ophthalmic risk; and (iii) a complete public release containing the engine, the curated knowledge base, all gold sets with case-level provenance, the 9,600 prediction rows (plus the reasoning-model re-run), and a runnable demonstration, allowing the method to be re-run and extended to other specialty-systemic interaction domains. The deposit is at https://github.com/wangguoqing932/ophddi-cds.

We have also taken care to report the study's limitations plainly, including that the validation gold is literature-derived and author-annotated rather than expert-adjudicated, that the audit-set high-risk sensitivity is 0.320, and that one adequate-budget LLM baseline outperforms the system on the audit set; these are stated in the Abstract, Results and Discussion rather than left to be discovered.

The manuscript has not been published or submitted elsewhere; all authors have approved the submission. We declare no conflicts of interest.

We would be grateful for your consideration.

Sincerely,

**Guoqing Wang, M.D.**¹, **Lumei Hu, M.D.**¹, **Shaocheng Wang, M.D.**³, **Xianglong Yi, M.D., Ph.D.**¹²\*

¹ Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China

² Xinjiang Medical University, Urumqi, Xinjiang, China

³ Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital, Xinjiang, China

**Corresponding author.** Xianglong Yi, M.D., Ph.D., Professor of Ophthalmology. Email: yixianglong1010@163.com
