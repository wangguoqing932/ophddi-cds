# Cover Letter

Dear Editors,

We submit our manuscript, **"OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening"**, for consideration as an Original Research article in *Frontiers in Pharmacology*. We suggest the section **Pharmaceutical Medicine and Outcomes Research**, and we would be glad to be placed in whichever section the editors consider most appropriate for clinical decision support in pharmacotherapy.

**The problem.** Ophthalmic topical medications are assumed to act locally, yet several reach clinically meaningful systemic exposure: timolol attains plasma concentrations comparable to low oral doses, and atropine, dexamethasone and the fluoroquinolones carry documented systemic effects. General-purpose interaction databases nonetheless grade severity from systemic administration and encode no ophthalmic absorption model. The result is that the same drug pair can carry a high-risk alert for oral dosing while being clinically negligible as an eye drop, and no study has measured how often that happens at registry scale.

**What we did and found.** We built a deterministic three-layer cascade of 40 mechanism rules, an absorption-scaled drug-class matrix and a hard constraint, covering 113 ophthalmic and 232 systemic agents, and compared three ways of assigning risk to the same pairs. Against DDInter severity for all 1,933 registry-matched pairs, absorption-aware assessment graded 75.3% lower, with 352 pairs moving down from high; 80.5% of that shift follows from one pharmacokinetic mechanism, low systemic absorption from the topical route. On a 118-case literature-derived gold the cascade reached 0.907 exact accuracy (kappa 0.857) against 0.415–0.737 for three LLM baselines. When the baselines were re-run with a reasoning model and a 3000-token budget their label agreement rose but their high-risk sensitivity collapsed to 0.214–0.536, while the cascade retained 0.964. A semi-independent 92-case audit against DDInter gave 0.674 exact accuracy but a high-risk sensitivity of only 0.320, which we report as the principal limitation of the current system rather than a footnote.

**Why this journal.** *Frontiers in Pharmacology* publishes pharmacotherapy and medication-safety work with a clinical readership, and this manuscript addresses a gap that sits squarely in that readership's practice: eye drops prescribed by ophthalmologists interacting with cardiovascular, antidiabetic, psychotropic and anticoagulant therapy managed by other clinicians. The contribution is mechanistic and auditable rather than model-driven: every decision returns the rule identifiers, the decision path and the evidence chain, which suits a pharmacology audience more than a computational one.

**Reproducibility.** The complete engine, curated knowledge base, gold sets with per-case provenance and 9,600 prediction rows are deposited at https://github.com/wangguoqing932/ophddi-cds under release tag `v3.0-frontiers`. The deterministic path makes no model call and requires no credential, so every reported number can be regenerated from the deposit. A one-command demonstration (`python scripts/demo_pipeline.py`, 25 mock pairs) and a test suite accompany the code.

**Disclosures.** The manuscript is original, is not under consideration elsewhere, and all authors approved the submitted version. The work involved no human participants, patient data or clinical intervention, so ethical review and informed consent were not applicable. The only human involvement was an anonymous 12-case professional-opinion exercise on constructed vignettes containing no patient data, described in full in the Ethics statement, including the fact that one participant is a member of the study team. Generative AI use is disclosed in the Declarations.

We confirm that we have no conflicts of interest to declare.

Yours sincerely,

Yi Xianglong, M.D., Ph.D. (corresponding author)
Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China
E-mail: yixianglong1010@163.com

On behalf of all authors: Wang Guoqing, Hu Lumei, Wang Shaocheng, Yi Xianglong
