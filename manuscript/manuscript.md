# OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening

## Authors

Wang Guoqing, M.D.¹; Hu Lumei, M.D.¹; Wang Shaocheng, M.D.³; Yi Xianglong, M.D., Ph.D.¹²*

¹ Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China
² Xinjiang Medical University, Urumqi, Xinjiang, China
³ Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital, Xinjiang, China

*Correspondence: Yi Xianglong, M.D., Ph.D., Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China; yixianglong1010@163.com

## Abstract

**Background.** Ophthalmic eye drops reach the systemic circulation, yet general-purpose drug-drug interaction (DDI) databases grade severity as though every drug were swallowed. Whether that assumption holds at registry scale, and how far it departs from the judgment of prescribing clinicians, is unknown. **Methods.** We built OphDDI-CDS, a deterministic cascade of 40 mechanism rules, an absorption-scaled class matrix and a hard constraint, covering 113 ophthalmic and 232 systemic agents. We compared its grades with systemic-route database severity across all 1,933 registry-matched pairs, with three language-model baselines on 118 literature-derived cases, and with two clinicians on 12 cases. **Results.** Absorption-aware assessment graded 75.3% of the 1,933 pairs lower than the database, including 352 that fell from high risk, and low systemic absorption accounted for 80.5% of those downgrades. On the 118-case gold the cascade reached 0.907 exact accuracy (kappa 0.857), against 0.415 to 0.737 for the three baselines. Given a 3000-token budget the baselines converged on a rarely-high-risk policy: agreement rose to 0.576 to 0.737 while high-risk sensitivity fell to 0.214 to 0.536, whereas the cascade held at 0.964. On a semi-independent 92-case DDInter audit the cascade reached 0.674 accuracy but a high-risk sensitivity of only 0.320 (8 of 25), its principal limitation; on the 62 cases whose labels do not depend on its own absorption assumption, accuracy was 0.548 (34 of 62). One adequate-budget baseline scored higher on the full audit set (0.728), an advantage confined to the 26 cases whose DDInter statement it can retrieve: with those excluded it falls to 0.652 (43 of 66) against 0.712 (47 of 66) for the cascade. Two clinicians agreed with each other on 11 of 12 cases (kappa 0.840) yet rated most cases below the assigned grades, a descriptive comparison rather than a validation. **Conclusions.** Database severity, evidence-graded rules and clinical intuition assign ophthalmic DDI risk differently, and none of the three is a ground truth. An absorption-first deterministic cascade makes those disagreements enumerable, traceable and auditable, but its false-negative profile requires prospective, outcome-linked calibration.

## 1. Introduction

Ophthalmic topical medications are among the most widely prescribed drugs, yet their systemic absorption is frequently underestimated in drug-drug interaction (DDI) screening. Although eye drops are assumed to act locally, several agents reach clinically meaningful systemic exposure. Timolol attains plasma concentrations comparable to low oral doses through nasolacrimal drainage [1,2,3]. Topical carteolol can cause atrioventricular block [4], and severe reactions following ophthalmic timolol have been linked to CYP2D6 poor metabolizers [5]. Documented events include cardiogenic shock with topical timolol plus verapamil [6] and case series of bradycardia and syncope [7,8]. Alpha-2 agonists cause central nervous system depression in children [9,10,11,12], and paediatric patients are generally more susceptible [13]. Nasolacrimal occlusion reduces exposure [14], whereas in elderly patients on multiple systemic medications such additive effects can accumulate into harm [15,16].

General-purpose DDI databases, including DDInter, publish pair-level severity ratings derived predominantly from systemic administration [17,18]. DDI screening is clinically relevant but methodologically heterogeneous [19], and automated detection remains incomplete [20,21]. Crucially, these databases omit the decisive ophthalmic modifier (the magnitude of systemic absorption from topical administration) and the corresponding dose-route correction. Contextualized algorithms exist for patient factors but not for route-specific absorption [22]. Route awareness is not wholly absent: Drugs.com keeps a separate ophthalmic entity for timolol, and Lexicomp asks for the route. What is missing is an explicit registry-wide absorption model. Neither the size of the mismatch nor its relation to clinician judgment has been measured.

Large language models (LLMs) offer flexibility but raise reliability concerns. Unconstrained models can hallucinate and are non-reproducible, retrieval-augmented variants inherit the biases of their corpora [23], and prospective evaluations of LLM-based decision support remain limited [24]. In our own evaluation retrieval augmentation closed only part of the gap to a purpose-built cascade, and the ranking of retrieval methods depended on the output budget [25,26; Section 3.6]. Systematic reviews of computerized decision support report modest and variable effects on practice [27,28], and high alert-override rates remain a central adoption problem [29,30,31].

We therefore built OphDDI-CDS, a deterministic three-layer cascade of 40 mechanism rules (each with a source record), an absorption-scaled class matrix and a hard-constraint layer. It covers 113 ophthalmic and 232 systemic agents and is grounded in 1,307 approved, source-tagged evidence chunks. The production path makes no LLM call, shows zero variance across temperature conditions, and returns matched rule identifiers with every grade. Our contribution is threefold. We quantify rather than assert the divergence from systemic-route severity. We provide the instrument that makes the measurement possible and traceable. We report the evaluation, including two reference sets on which the system agrees poorly, in a form that can be audited and re-run.

## 2. Materials and methods

### 2.1 Design, data sources and route representation

Evaluation followed a four-phase protocol: rule consistency, development-phase validation, a semi-independent external audit against DDInter, and a two-expert grade review. That review is reported as a perspective comparison rather than an independent assessment, since one rater is a member of the corresponding author's research team (Section 2.5). Three LLM baselines were compared under five temperature conditions.

Route is modelled through two mechanisms rather than a route field. Every ophthalmic agent carries one of six systemic-absorption tiers, the proxy for how much of a topical dose reaches the circulation. The rule layer also encodes route-dependent predicates directly, for example a rule requiring the `systemic_absorption_high` flag before it fires.

The registries and knowledge base are summarised in Table 1. Data sources were DDInter 2.0 (302,516 DDI records) [18], FDA ophthalmic product labels, Stockley's Drug Interactions and the British National Formulary [34], and PubMed. All 1,307 evidence chunks were filtered to approved release and graded by evidence level: A regulatory label, B meta-analysis or systematic review, C original study, D in vitro, animal or pharmacokinetic first principles, E class-level mechanism inference. The distribution is A = 53, B = 191, C = 215, D = 584, E = 264 (Supplementary Text S1).

### 2.2 The cascade

The production system (`full_system`) is a three-layer deterministic cascade with zero LLM calls (Figure 1; registry and evidence-base counts in Table 1).

**L1 rule engine.** Forty mechanism rules cover additive beta-blockade, beta-blocker–calcium-channel-blocker effects, additive alpha-2 CNS depression, CYP3A4 induction or inhibition, and QT prolongation with low-absorption fluoroquinolones. Each rule is an entity-flag predicate with match-all or match-any semantics, and the highest-severity hit is retained (MAX-MATCH). The 43 policy entries comprise 40 rules plus 3 patient-factor policies (Table 2). Rules are evaluated independently; the only cross-layer composition is the final maximum of the two layers, and combination products are tiered by their dominant component.

Citation coverage is narrower than "citation-verified" implies. Every rule carries a source record, but the records are heterogeneous (41 DrugBank entries, 7 label records, 2 DOIs, 2 DDInter annotations, 1 PubMed citation). Independent verification covers 8 manifest items spanning 7 DOIs, of which three rules resolve to a verified literature citation (Supplementary Text S2). "Citation-verified" therefore does not cover every rule. `beta_blocker_digoxin_additive` cites a study of additive beta-blockade rather than a digoxin-specific source, and grades as high a pair its own DDInter annotation records as moderate; we retain the conservative grade and flag the gap.

**L2 class matrix.** The configuration declares 21 ophthalmic row keys and 40 systemic column keys (34 used) and assigns a level to 104 cells: 83 actionable, 21 marked "none". Four upgrade rules require both a class match and specific absorption or selectivity flags. An absorption-scaling step sets agents with low, very-low, minimal or no absorption to low directly; upgrades are evaluated only for high or medium tiers, so no upgrade can raise a low-tier pair. That step is **not empirically validated** against outcome data. It is an author-specified decision grounded in the principle that a dose which does not reach the systemic circulation cannot produce a systemic interaction, and its behavioural consequence is quantified in Section 3.4. Pairs reaching neither a rule nor a defined cell fall through to the default-low path.

**L3 hard constraint.** Low or very-low absorption with no rule hit and no matrix signal yields low risk (G19). Unknown medications are not silently classified: the engine returns an explicit unknown-drug path and the service raises an error, so out-of-coverage pairs are never assigned a grade by default.

**Absorption tiers.** Tiers were assigned from pharmacokinetic sources and regulatory labels, including nasolacrimal-drainage bioavailability and plasma levels for timolol [1,35] and instillation-technique effects on exposure [14]. The registry uses six values (113 agents: 15 high, 17 medium, 61 low, 9 very-low, 7 minimal, 4 none). The L3 hard constraint tests two of these, `systemic_absorption_low` and `systemic_absorption_very_low`; the matrix layer already maps minimal and none to low. The tier is a **categorical assignment, not a measured quantity**: the intended reading is fractional systemic bioavailability after instillation, but sources report heterogeneous quantities, so the tiers are an explicitly stated ordinal model. Two limitations follow (Section 4.3): flurbiprofen was tiered high against a low curation-file record and is now low, and nine of the 113 agents are not topically administered (six intravitreal anti-VEGF agents, intraocular acetylcholine, two surgical viscoelastics). The source column does not evidence the tiers individually. Most rows carry `DrugBank DBxxxxx|PubMed`, with individual sources named only for timolol [1,35] and for atropine and dexamethasone [36]. The remaining tiers are therefore the study team's curation assignment, marked as such in Supplementary Table S5. Ocular drug transfer after systemic administration is itself incompletely characterized [37].

The evidence base was embedded with a 2048-dimensional Doubao model and indexed with LightRAG [26] (1,307 documents, 4,956 entities, 6,885 relations); retrieval baselines used BM25 [25] over the same chunks.

### 2.3 Validation data

**L1 literature-derived gold (118 cases).** Three subsets: 20 cases annotated by the study team from named literature sources, 58 guideline-sourced cases covering classes where the routes diverge most, and a procedurally frozen 40-case blind subset. Twenty labels (G01–G20, tagged `T1_literature_consensus`) were annotated from FDA labels, Stockley's, BNF tables and Drugs.com, with the supporting statement deposited for each; five (G04, G05, G08, G16, G19) differ from the DDInter severity for the same pair. The remaining 98 were annotated by the two authors from the same categories of source. **How the 58 guideline labels were set.** Those cases were drawn from the evidence that specific rules cite. For 47 of the 58 the gold label is that rule's severity; the other 11 were overridden by hand after review (G113, G114, G125, G126, G128, G131–G134, G149, G154). Agreement on the 47 therefore measures rule fidelity by construction, and the groups are reported separately. The labels and blind proposals were drafted without reference to system outputs, with one exception. On 31 July 2026, after the lock and before the questionnaire, B02 (high→medium), B12 (medium→high) and C17 (low→medium) were corrected to the engine's grades (Section 3.8, results both ways). The eleven remaining disagreements are listed with rationale in Supplementary Table S1. Distribution: 28 high, 51 medium, 39 low (per-dataset in Supplementary Table S8).

**DDInter audit set (92 cases).** A stratified random sample by absorption tier and DDInter severity. The stated rule was to set a case to low when the agent's tier is low or lower, no rule fires and no matrix upgrade applies. As applied, 30 cases were corrected and 62 kept, with three documented deviations. Seven corrected cases are in fact reached by a rule. The two aflibercept pairs (tier `minimal_systemic_absorption`) were kept, and the four flurbiprofen pairs were kept on the superseded high tier recorded at the lock (full list in Supplementary Text S9). Re-deriving the gold under the stated rule changes 10 of 92 labels, giving 60 of 92 (0.652) with sensitivity 8 of 29, against 62 of 92 (0.674) and 8 of 25 under the applied gold. The audit is therefore semi-independent: the severity component is third-party, but the absorption correction shares the system's assumption.

**Reference sets.** A development set (200 DDInter-derived cases), an external co-mention set (70 cases) and an internal validation set (78 cases) served as development gates, not validation. The first two carry unadjusted systemic-route gold (Section 3.2), and the internal set overlaps 78 of the 118 L1 cases by identity with identical labels.

### 2.4 Comparators and metrics

`pure_llm` makes one LLM call with a domain-general prompt and no retrieved evidence. `naive_rag` adds BM25 retrieval (`BM25Okapi`, k1 = 1.5, b = 0.75); the query is `f"{a} {b} ophthalmic interaction"`, where `a` and `b` are the ophthalmic and systemic drug names, so the query includes the drug names. The top-3 passages are retained (top-k = 3), each truncated to 400 characters. `lightrag` adds a knowledge-graph context block rendered by `PreciseKG.full_kg_context()`, which reads the registries and rule configuration rather than the vector index. That block contains the drug profiles, the matched rule identifiers with their severities, and, for low-absorption pairs with no matched rule, an explicit instruction that the grade must be low. The baseline therefore receives part of the rule layer, so the gap between it and `full_system` understates what retrieval augmentation would achieve without those hints.

LLM baselines used `deepseek-chat` with a 10-token cap and no chain-of-thought prompting. The endpoint exposes neither parameter count nor checkpoint revision. Input was English, with temperatures 0.0 (condition 0) and 0.3, 0.6, 0.9 and 1.2 (conditions 1 to 4). Outputs were parsed by substring matching with an unknown fallback; one of the 9,600 predictions was unparseable. Five conditions × four methods × four datasets produced 9,600 rows with zero API failures (run configuration and file-level fingerprints in Supplementary Text S5). A second setting used `glm-5.3-flash` with `max_tokens` 3000, temperature 0.0 and a majority vote over five repeated samples. Because it changes model, budget and sampling together, it is reported as a second setting rather than as an isolated test of reasoning.

Metrics were exact three-level accuracy, high-risk sensitivity and specificity, high-risk F1, and Cohen's kappa [38] with Landis–Koch interpretation [39]. Method differences were tested with the exact two-sided McNemar test on discordant pairs at condition 0; intervals are Wilson, Clopper–Pearson or bootstrap as appropriate. No power calculation was performed. Full parameter lists, prompts and the run configuration are in Supplementary Text S3 and S9.

### 2.5 Expert grade review

Two ophthalmologists reviewed 12 cases under a grade-review protocol (Supplementary Table S3). Both are clinicians of the Department of Ophthalmology of the First Affiliated Hospital of Xinjiang Medical University, and one is a member of the corresponding author's research team, so we use "perspective comparison" rather than "independent assessment". The instrument displayed the drug pair, a short scenario, the proposed gold grade and a system grade with a one-line rationale, and the expert recorded their own judgment on the same three-level scale. Because both grades were visible, this is a grade review rather than a blinded assessment. Cases were constructed around the system's outputs, which is why the exercise cannot serve as independent validation. Ratings were collected on 3 August 2026 and transcribed on 8 August; expert 1's questionnaire is deposited as a scan and both sets as transcribed records.

### 2.6 Intended use and software

The system is a research-grade, mechanism-based second reader. It is not intended to replace clinical or pharmacy judgment, out-of-coverage medications are rejected with an explicit error, and it is not marketed as a medical device.

The implementation is Python 3.11 (`ophthalmic_ddi_cds_agent`). Source code, knowledge base, verification tooling and evaluation scripts are available at https://github.com/wangguoqing932/ophddi-cds (release tag `v3.0-frontiers`, archived at DOI 10.5281/zenodo.23439606), with a synthetic demonstration dataset and a one-command entry point (`python scripts/demo_pipeline.py`, 25 mock pairs). Versions are pinned by SHA-256 fingerprints in the repository-root `MANIFEST.sha256`. The report follows TRIPOD+AI [32] and DECIDE-AI [33] reporting guidance where applicable (Supplementary Text S6); generative AI use is documented in the Declarations and the software section of the manuscript.

## 3. Results


### 3.1 System construction

The knowledge base comprises 113 ophthalmic agents (104 topically administered; 9 intravitreal, intraocular or surgical) and 232 systemic medications (Supplementary Table S4). It holds 1,307 approved evidence chunks (A = 53, B = 191, C = 215, D = 584, E = 264; Supplementary Text S1) and a LightRAG index over 1,307 documents. The rule engine comprises 40 mechanism rules plus 3 patient-factor policies, each with at least one source record and zero policy errors (Table 2; Supplementary Table S6). Method performance on all four datasets is tabulated in Table 3. The class matrix defines 104 cells across 21 ophthalmic row keys and 34 used systemic columns; the distribution of gold levels across the four datasets is given in Table 4. Figure 2 summarises the method comparison, Figure 3 the clinician review and Figure 4 representative outputs.

### 3.2 Development-phase reference results

On the internal validation set (78 cases) sensitivity was 1.000 and specificity 0.984, reported as a development gate because 78 of 118 L1 cases overlap it with identical labels. Against the unadjusted systemic-route gold of the development set (200 cases) the system achieved 0.210 exact accuracy (sensitivity 0.069, specificity 0.895); against the external co-mention gold (70 cases, audited as noisy) 0.443 (0.077, 0.935). These low values quantify the magnitude of the absorption correction relative to systemic-route labels and are not interpretable as performance.

### 3.3 Agreement with the literature-derived gold (118 cases)

On this set the gold and the rules draw on the same literature, so agreement measures the internal consistency of an evidence-graded encoding rather than accuracy against an independent standard (Table 3, Figure 2; Supplementary Table S7).

`full_system` achieved 0.907 exact accuracy (107/118; Wilson 95% CI 0.841–0.947), 0.964 high-risk sensitivity (27 of 28; CI 0.823–0.994), 0.989 specificity and kappa 0.857 (bootstrap CI 0.772–0.934), with zero variance across conditions. `lightrag` reached 0.737 accuracy, 0.779 sensitivity and 0.936 specificity (kappa 0.603); `pure_llm` 0.475 and 0.771 (kappa 0.256); `naive_rag` 0.415 and 0.757 (kappa 0.182). Exact McNemar tests at condition 0 were significant against each baseline. Discordant pairs in favour of the system were 54 to 2 versus `pure_llm` (p = 4.4 × 10⁻¹⁴), 60 to 4 versus `naive_rag` (p = 7.4 × 10⁻¹⁴) and 20 to 1 versus `lightrag` (p = 2.1 × 10⁻⁵). The gradient `full_system` > `lightrag` > `pure_llm` > `naive_rag` held across all five temperature conditions. The 0.170 gap to the best baseline is the margin over a comparator that already receives the matched rules (Section 2.4), so it should not be read as the contribution of retrieval augmentation alone. Per subset, the frozen blind cases reached 39 of 40, the mechanism subset 20 of 20 and the guideline subset 48 of 58. Decomposing the guideline subset as described in Section 2.3, the system agrees on 43 of the 47 cases whose label equals the cited rule's severity and on 5 of the 11 hand-overridden cases. The 0.907 headline is therefore a weighted average of rule fidelity (43/47), agreement with hand-adjudicated labels (5/11) and agreement on the 60 T1 and frozen cases (59/60). It should not be read as a single independent accuracy estimate.

### 3.4 Registry-scale divergence

This result does not depend on the gold labels, since both sides are pre-specified: DDInter supplies a systemic-route severity rating and the cascade an absorption-aware grade. Of the 1,933 pairs for which DDInter 2.0 provides a severity record, 1,455 (75.3%) were graded lower by the system. That includes 352 downgraded from high (37 to medium, 315 to low; 18.2% of all pairs) and 1,103 from medium to low. A further 136 (7.0%) were upgraded, so the two perspectives differ for 82.3% of pairs. Of all downgrades, 80.5% (1,171 of 1,455) were attributable to low systemic absorption. Three of every four rated pairs would therefore reach a prescriber at a different grade, and most of that shift follows from a single pharmacokinetic mechanism rather than from many independent judgements.

Two caveats bound this measurement. It quantifies divergence, not error: the two perspectives rarely coincide for the topical route, but that does not make the database ratings wrong. And the tiers driving the downgrades were assigned by the study team from pharmacokinetic sources and labels (Section 2.2), so the measurement is a property of an explicitly stated absorption model rather than an independent pharmacokinetic measurement.

### 3.5 Semi-independent DDInter audit (92 cases)

On the audit set `full_system` reached 0.674 exact accuracy (62/92; Wilson CI 0.573–0.761) and kappa 0.428 against the absorption-corrected gold (specificity 0.955). Only part of that set is independent of the system's own assumption. Restricting to the 62 cases kept at third-party DDInter severity gives 34 of 62 (0.548), the figure free of that assumption, which should be read as the audit headline rather than 0.674. Against uncorrected DDInter labels agreement was 0.370 (34/92). Of the 30 corrected cases the system agreed on 28 (93%); of the 62 kept cases it agreed on 34 (55%) (Table 5). Baselines on the corrected gold were `pure_llm` 0.630, `lightrag` 0.591 and `naive_rag` 0.535. McNemar tests were significant versus `lightrag` (8 versus 1; p = 0.039) but not versus `naive_rag` (27 versus 17; p = 0.174) or `pure_llm` (18 versus 15; p = 0.728). Symmetrically, `pure_llm` and `naive_rag` exceed the system on sensitivity (0.848 each versus 0.320; `lightrag` is lower at 0.264). The cascade's advantage therefore lies in specificity and exact accuracy, not sensitivity.

This comparison is partly confounded. Of the 1,307 chunks, 500 are DDInter severity statements, and the audit gold for the 62 third-party cases is the DDInter value itself. The top-3 passages contain the pair's own statement for 19 of those 62, so `naive_rag` retrieves the gold label there; `lightrag` shows a weaker version of the same effect. With the 26 retrievable cases removed, adequate-budget `naive_rag` is correct on 43 of the remaining 66 (0.652), identical to `pure_llm`, against 47 of 66 (0.712) for the cascade, and its sensitivity falls from 9 of 10 to 1 of 15. Under the re-derived gold the cascade scores 60 of 92 (0.652), so the conclusions hold under either reading.

High-risk sensitivity on the audit set was 0.320 (8 of 25 gold-high cases; CI 0.172–0.516), above `lightrag` (0.264) but well below `pure_llm` and `naive_rag` (0.848 each). That this figure is low in absolute terms is the principal limitation of the current system. The 30 disagreements were directionally consistent with the absorption-first design. Seventeen gold-high pairs were downgraded (8 to low, 9 to medium), 9 gold-medium pairs to low, 2 gold-medium pairs upgraded to high, and 1 gold-low pair each to medium and high (Supplementary Table S2). Misses are concentrated in clinically sensitive pairs: betaxolol with verapamil or diltiazem, timolol with epinephrine, anticholinergic combinations with topiramate, and flurbiprofen with methotrexate. The last illustrates how the absorption model interacts with third-party labels. Flurbiprofen is formulated at 0.03%, the lowest concentration of any ophthalmic NSAID in the registry, so correcting its tier moved this pair and three related anticoagulant pairs further from the DDInter gold rather than closer. That divergence is between a systemic-route label and a low-absorption agent, and for a screening tool this false-negative profile is the clinically critical number.

### 3.6 Reasoning-model baselines under an adequate output budget

Because the primary comparison used a non-reasoning model with a 10-token cap, we repeated the three baselines under conditions that remove that constraint, reporting both settings. Label agreement improved: on the 118-case set `pure_llm` rose from 0.475 to 0.576 and `naive_rag` from 0.415 to 0.585, while `lightrag` was unchanged at 0.737. High-risk sensitivity, however, fell sharply and specificity rose to approximately 1.000 (Table 3): sensitivity moved from 0.771/0.757/0.779 to 0.250/0.214/0.536, while the cascade held at 0.964 with specificity 0.989. The mechanism is a shift in the predicted label distribution rather than better discrimination. Under the larger budget `pure_llm` and `naive_rag` assign high risk to 6% of cases and `lightrag` to 13%, where the gold contains 24%; on the audit set they assign 2% where the gold contains 27%. Because both gold sets are dominated by low and medium grades, this conservatism inflates exact accuracy. The baselines identify only 4 to 15 of the 28 gold-high cases across repeats, or 7 to 15 under majority vote, against 27 for the cascade. We therefore read the accuracy increase as an artefact of the decision rule adopted with more room, not as evidence that reasoning improves ophthalmic DDI screening.

Two further results bear on the primary comparison. First, the ordering between retrieval methods reverses. Under the 10-token cap `naive_rag` scored below `pure_llm`; with an adequate budget it scores at or above it on both sets (0.585 versus 0.576; 0.728 versus 0.609). The 10-token ordering is therefore a property of the constrained setting. Second, on the audit set adequate-budget `naive_rag` reaches 0.728 exact accuracy and 0.400 sensitivity, both above the cascade. That advantage is confined to cases whose own DDInter statement the retriever can reach. With those 26 excluded it falls to 43 of 66 (0.652), below the cascade's 47 of 66 (0.712), and its sensitivity falls from 9 of 10 to 1 of 15. Its sensitivity is also unstable across repeats (0.280 to 0.480), whereas the cascade returns the same grade every time. At temperature 0.0 the baselines still varied by 0.013 to 0.034 in exact accuracy, which is why the reported figures use a majority vote.

### 3.7 Determinism and temperature sensitivity

`full_system` is deterministic: all five temperature conditions returned identical predictions (SD = 0.000), a determinism check rather than a robustness claim. Figure 5 shows the per-layer latency trace, in which the cascade completes in under 2 ms with no model call. The LLM baselines varied across conditions on the L1 set. `lightrag` accuracy ranged from 0.712 to 0.771 (SD 0.020), `pure_llm` from 0.449 to 0.517 (SD 0.024) and `naive_rag` from 0.390 to 0.432 (SD 0.014), with a similar pattern on the audit set (SD 0.005–0.039).

### 3.8 Exploratory clinician grade review (12 cases)

Two ophthalmologists rated 12 cases with the proposed gold and a displayed system grade both visible (Figure 3; Section 2.5). Inter-rater agreement was 11 of 12 (kappa 0.840, 95% bootstrap CI 0.526–1.000; quadratic-weighted 0.875). Against the displayed grades, expert 1 agreed on 2 of 12 cases (kappa −0.176) and expert 2 on 1 of 12 (kappa −0.257). Against the proposed gold, expert 1 agreed on 4 of 12 (kappa 0.020) and expert 2 on 3 of 12 (kappa −0.091). The comparisons differ because for R10 and R11 the displayed grade was not the engine's grade. Against the gold each expert rated 8 of 12 cases lower (discordant judgments 8 of 8 and 8 of 9), and neither rated any of the four displayed-high cases as high. Quadratic-weighted kappas are 0.473 and 0.438 against the gold and 0.355 and 0.313 against the displayed grades, placing the divergence at roughly one tier rather than at random disagreement. The maximum attainable unweighted kappa given the marginals is 0.294 and 0.314, so the low unweighted values partly reflect margin incompatibility.

Across all twelve cases the proposed gold equals the deposited engine grade, so the expert-versus-gold and expert-versus-displayed comparisons cannot separate the gold from the engine; the exercise is a comparison against the assigned grade, not a test of either. For R10 and R11 the questionnaire displayed medium, a class-level hint written by the study team rather than the engine's output; the engine grades both pairs low, matching the gold. No rule or matrix level has changed since the review. All twelve cases correspond to L1 cases. Five belong to the frozen blind subset (R01 = B02, R02 = B12, R03 = C17, R10 = B18, R11 = C20), and the other seven are B06, C02, C03, B19, C10, C11 and G08. The blind sets were locked on 31 July 2026 (lock hash `df2890f6…`; audit design lock `8956cfe6…`). Three labels were corrected to the engine's grades the same day and committed on 3 August (`acd9f44a…`, `61dc8af7…`). Reporting both ways gives 39 of 40 and 107 of 118 under the corrected labels, and 36 of 40 and 104 of 118 under the pre-correction labels.

The exercise is not a validation: both grades were visible, one expert is a study-team member, the cases were constructed around the system's outputs, and the sample is purposive. Case-level ratings are in Supplementary Table S3. What it supports is a perspective gap between clinical prior and evidence-based grading, not an error rate.

## 4. Discussion

### 4.1 Principal findings

Three perspectives on ophthalmic–systemic risk (systemic-route database severity, evidence-graded rules and prescribing clinicians) assign grades differently, and this study measures that difference on overlapping pair sets. Absorption-aware assessment grades three quarters of the registry-matched pairs lower than the database and a further 7.0% higher, so the two differ for more than four pairs in five. Evidence-graded rules and clinical judgment also diverge: the two ophthalmologists agreed closely with each other (kappa 0.840) yet rated most cases one tier below the assigned grades (Section 3.8). Because the panel was not independent and the cases were built around the system's outputs, this is a perspective comparison rather than a validation. Three observations make a perspective difference more plausible than an error. Clinically serious events are rare, so expert judgment gravitates toward lower tiers. The interactions clinicians recall are dominated by non-selective beta-blockers, so systematic coverage matters most where recall is weakest. Reports of serious adverse events are sparse, although pharmacovigilance analyses do identify systemic signals [36,40]. High alert-override rates [29] further suggest that a tool sitting one tier above clinical intuition will be treated as noise unless its justifications are transparent. The results are therefore consistent with the absence of a shared grading standard rather than with error in any one tool.

The quantitative results bound that claim rather than carry it. The cascade reached 0.907 exact accuracy on the 118-case gold (107/118) and outperformed three LLM baselines (0.415–0.737) with significant McNemar tests. On the audit set and within the primary protocol it led on exact accuracy (0.674 versus 0.535–0.630) and specificity (0.955). Its high-risk sensitivity was, however, low in absolute terms (0.320, 8 of 25), below `pure_llm` and `naive_rag` (0.848 each) though above `lightrag` (0.264), and its advantage over those two was not significant. Under the adequate-budget re-run one baseline exceeded it. Because 47 of the 58 guideline labels are the cited rule's own severity, 0.907 is best read as internal consistency rather than independent accuracy; the audit sensitivity bounds what the system can claim as a safety screen today.

### 4.2 What we add relative to prior work

Against general-purpose DDI databases, our system makes the ophthalmic absorption factor an explicit modelling component: a tier on every agent, an absorption-scaling step inside the matrix layer, and a hard constraint. The final grade is the maximum of the rule and matrix layers. That maximum is the honest limitation of the design. Because the rule layer is not uniformly gated, 202 pairs with a low-or-below tier receive medium (107) or high (95) grades through rules that require no absorption flag, all 95 high grades from a single rule. Gating that rule would lower agreement with the L1 gold from 0.907 to 0.890, and gating all four NSAID rules to 0.847. We report the behaviour rather than re-engineer it to fit the gold; the gold's preference for an ungated rule is itself informative, because part of it was labelled from sources that reason about systemic exposure. Whether to gate these rules is a calibration decision for outcome-linked evidence, not gold agreement.

Against LLM and retrieval-augmented approaches, the practical difference is not label agreement alone, which favours the cascade on L1 and the full audit set but not on the label-independent subset. It is the sensitivity–specificity profile and the reproducibility of the decision. Machine-learning predictors built on molecular structure [41] or knowledge graphs [42] target systemic-route interactions and likewise omit route-specific absorption. The cascade is deterministic by construction, so reproducibility is a design property rather than a robustness result, and every decision returns matched rule IDs, a decision path and the rule's source record where available.

The largest methodological implication is that a severity rating exported from a systemic-route database is not a valid ophthalmic ground truth. Any evaluation treating it as one measures the distance between two assumptions rather than the tool's accuracy. That is why we report agreement with unadjusted systemic-route labels (0.210 and 0.443, Section 3.2) as a quantification of the adjustment rather than as performance.

### 4.3 Limitations

**Absorption-tier assignment.** The tiers are the most load-bearing variable and the least independently documented: a study-team assignment with no operational measurement behind every agent, with one defect corrected and one open. Flurbiprofen was tiered high against a low curation-file record and is now low. Thirteen further agents show the same discrepancy. We adopt the registry as authoritative because the engine loads it at inference. Re-running the 1,933-pair audit under the curation-file tiers moves the downgrade share from 75.27% to 75.69% and leaves the from-high downgrades at 352, so the conclusion is robust to that choice. Nine of the 113 agents are not topical, including aflibercept, so the registry-scale divergence is a property of this stated absorption model rather than an independent pharmacokinetic measurement.

**Bounded clinical impact.** The scarcity of direct evidence admits two explanations: clinically detectable systemic effects may be uncommon, or publication and ascertainment bias may operate; the present data cannot distinguish them. If the true risk gradient clusters at the low end the system may over-grade, while audit sensitivity of 0.320 shows it can also under-grade. At an illustrative 1% prevalence the audit operating point (sensitivity 0.320, specificity 0.955) yields a positive predictive value of about 6.7%, so the system's value lies in coverage and traceability rather than screening yield.

**Validation.** The L1 gold is heterogeneous. Twenty of its 118 labels are study-team annotations, 47 of the 58 guideline labels are the cited rule's severity, and the remainder was author-annotated, so it is a literature-derived proxy rather than an independently adjudicated standard. Only the 40 frozen cases are procedurally independent, only 20 of those were free of development exposure, and three of their labels were corrected toward the engine's grades after the lock, so the subset is reported both ways (Section 3.8). In addition, 78 of 118 L1 cases overlap the development set with identical labels. The two-expert review is the only human channel beyond annotation and cannot serve as an independent test. Headline results reflect the final engine and gold; earlier versions scored higher on the same cases (0.992).

### 4.4 Future directions

Four directions follow. **Registry correction:** re-assign every tier from a documented source and threshold, reclassify or exclude the nine non-topical agents, then re-run the registry-scale analysis; the same item covers whether `nsaid_antihypertensive_antagonism` and the other NSAID rules should be gated on absorption. Second, **clinical calibration:** a larger expert panel or outcome-linked retrospective data could determine whether a one-tier offset applies to specific tiers or classes, with the audit false-negative pairs as first targets. Third, **false-negative surveillance:** pharmacovigilance mining and prospective monitoring of high-absorption agents would test mechanism-derived rules against outcomes. Fourth, **coverage and scope:** extend the registry, expose an unassessed status for out-of-coverage pairs, and transfer the class-matrix architecture to dermatologic, inhaled and intranasal domains.

## 5. Conclusions

We developed OphDDI-CDS, an absorption-first deterministic cascade for ophthalmic–systemic DDI screening, and used it to compare three ways of assigning risk. Against DDInter severity, absorption-aware assessment graded 75.3% of all 1,933 registry-matched pairs lower, with 80.5% of that shift attributable to low topical systemic absorption. An exploratory grade review likewise found one-directional disagreement with the assigned grades, reported as a perspective gap rather than an error rate (Section 3.8). The cascade reached 0.907 exact accuracy on the 118-case gold (107/118; kappa 0.857) with complete output traceability, and outperformed three LLM baselines on exact accuracy in the primary protocol. On a semi-independent audit set it reached 0.674 exact accuracy, falling to 0.548 on the subset free of its own absorption assumption, but a high-risk sensitivity of only 0.320, below `pure_llm` and `naive_rag` (0.848 each). That sensitivity, together with a gold that is part study-team and part author annotation, bounds what the system can claim today. Ophthalmic DDI risk lacks a shared grading standard: database severity, evidence-graded rules and clinical prior disagree directionally in every sample studied, and evaluation here should measure that disagreement rather than assume any one is correct. Prospective, outcome-linked calibration is the next step.

## Keywords

ophthalmic drug-drug interaction; clinical decision support; deterministic rule engine; systemic absorption; explainable artificial intelligence; medication safety

Abbreviations are defined at first use and collected in Supplementary Text S7.

## Supplementary material

The Supplementary Material for this article is deposited with the manuscript and contains **Supplementary Texts S1–S7 and S9** (evidence-base summary, rule citation verification, evaluation prompts, figure legends, evaluation reproducibility, TRIPOD+AI checklist, abbreviations, and protocol detail) and **Supplementary Tables S1–S8** (L1 disagreements with rationale, audit-set disagreement directions, per-case expert ratings, registry summary, per-agent absorption tiers, rule inventory, per-dataset performance, gold-level distribution). It is also available from the public repository https://github.com/wangguoqing932/ophddi-cds under release tag `v3.0-frontiers`, archived at DOI 10.5281/zenodo.23439606.

## Declarations

### Ethics statement

Ethics approval and consent to participate are not applicable to this study. It used only publicly available secondary data (the DDInter severity tables, published drug labels, DrugBank records and the peer-reviewed literature). It involved no human participants, no patient-level data, no human tissue or biological specimens, and no clinical intervention. Under the Declaration of Helsinki and the Chinese Measures for Ethical Review of Life Science and Medical Research Involving Humans, secondary analysis of published data does not constitute human-subjects research, so neither ethical review nor informed consent was required. The committee competent for this institution is the Ethics Committee of the First Affiliated Hospital of Xinjiang Medical University; no submission to it was required for the present work.

The only human involvement was an anonymous professional-opinion exercise: two ophthalmologists, both clinicians of the Department of Ophthalmology of the First Affiliated Hospital of Xinjiang Medical University, rated 12 hypothetical drug-pair vignettes constructed by the study team on 3 August 2026. The vignettes described no real patient, contained no patient data and no identifiable information, and the ratings are reported under pseudonymous case identifiers (R01–R12). Because the exercise collected no personal data and posed no intervention or risk to the participants, it does not constitute human-subjects research, and the participants' consent beyond agreeing to take part was not required; the completed questionnaires were returned anonymously to the study team. One of the two is a member of the corresponding author's research team. The pair is therefore not an independent external panel, and the exercise is reported as a descriptive perspective comparison rather than as independent validation.

The system is a research decision-support tool and is not intended to replace clinical judgment (Section 2.6).

### Consent statement

Not applicable. The manuscript contains no identifiable personal data. The expert ratings were returned anonymously and are reported under pseudonymous case identifiers, with no information that could identify either participant (see the Ethics statement).

### Data availability statement

All datasets supporting the conclusions of this article are deposited in a public repository and are also included as additional files. The deposit contains the entity registries (113 ophthalmic, 232 systemic agents) and the 1,307-chunk evidence base; all gold files with per-case provenance (`data/gold/`); the audit-set design file and its re-derived gold; the 12-case expert ratings with the review instrument and the returned questionnaires (expert 1's as a scan, both sets as transcribed records); the 9,600 primary prediction rows (4 methods × 5 temperature conditions × 4 datasets), the 3,150 reasoning-model responses, and the evaluation and statistics scripts; the exact prompt templates; the DDInter severity tables used for the registry-scale audit; a per-agent absorption-tier table with a source column for each agent; the path-attribution audit reporting which layer produced each grade; a synthetic demonstration dataset with a one-command entry point (`python scripts/demo_pipeline.py`, 25 mock pairs covering all three decision paths and the unknown-drug fail-safe); and a repository-root `MANIFEST.sha256` (LF line endings, so `sha256sum -c` works directly) covering the engine, rules, class matrix, registries, evidence base, gold files and the LightRAG index build record. The deterministic cascade requires no API key or network access, so the pipeline runs end to end from the deposit; re-running the LLM baselines requires model-API credentials. A test suite (`pytest tests/`) verifies the registry, rules and citation-verification layers. DDInter severity tables are redistributed under DDInter's own CC BY-NC-SA 4.0 terms, for research reproducibility only; original data and configuration are CC BY 4.0, and code is Apache-2.0. No dataset is restricted or available only on request.

**Repository.** The source code, configuration and derived datasets are maintained at https://github.com/wangguoqing932/ophddi-cds, publicly accessible without an account. A versioned release of the code matching this manuscript, with its own persistent identifier, will be deposited on acceptance.

**Software.** Project name: OphDDI-CDS (Python package ophthalmic_ddi_cds_agent). Project home page: https://github.com/wangguoqing932/ophddi-cds. A versioned release with a persistent identifier will be deposited on acceptance. Operating system(s): platform independent. Programming language: Python 3.11; dependencies pinned in `pyproject.toml`. Licence: Apache-2.0 (code) and CC BY 4.0 (original data). The Zenodo archive carries a whole-record CC BY-NC-SA 4.0 licence because it bundles the DDInter severity tables, which are third-party data under those terms; see the component-licensing section of the repository LICENSE.

### Conflict of interest

The authors declare that the research was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest.

### Funding

This study was supported by the Natural Science Foundation of Xinjiang Uygur Autonomous Region, China (Key Project No. 2022D01D68).

### Author contributions

Wang G: Conceptualization, Methodology, Software, Formal analysis, Data curation, Visualization, Writing - original draft. Hu L: Clinical input, Data interpretation, Writing - review & editing. Wang S: Clinical input, Data interpretation, Writing - review & editing. Yi X: Conceptualization, Supervision, Project administration, Funding acquisition, Resources, Data curation (gold-label annotation, Section 2.3), Writing - review & editing. All authors contributed to the article and approved the submitted version.

### Acknowledgments

Not applicable. No non-author individual or institution contributed to the work beyond the funding acknowledged above; the expert participants are acknowledged in the Ethics statement under pseudonymous identifiers.

### Generative AI statement

Generative AI tools were used during this research and manuscript preparation, with full author review and responsibility. DeepSeek-chat (deepseek.com) was used for LLM-baseline evaluations and as an assistive tool in knowledge-engineering tasks, including registry curation, evidence grading, and gold-label annotation; Zhipu GLM-4.6V was used for visual verification of scanned expert questionnaires. Figure 1 (system architecture) and Figures 2–5 were drawn directly from the system's configuration and outputs with standard plotting software (Matplotlib); no AI image-generation tool was used for any figure. All AI-assisted content was reviewed and validated by the authors, who take full responsibility for the content of this manuscript. The label `T1_literature_consensus` in the deposited files marks the 20 literature-annotated gold cases described in Section 2.3; it is a group tag, not a record of a separate human adjudication. The 12-case grade review of Section 3.8 is the only human evaluation conducted within this study.

## References

[1] Alvan, G., Calissendorff, B., Seideman, P., Widmark, K., and Widmark, G. (1980). Absorption of ocular timolol. Clin Pharmacokinet. 5, 95–100. doi: 10.2165/00003088-198005010-00004

[2] Rait, J. L. (1999). Systemic effects of topical ophthalmic beta-adrenoceptor antagonists. Aust N Z J Ophthalmol. 27, 57–64. doi: 10.1046/j.1440-1606.1999.00145.x

[3] Korte, J. M., Kaila, T., and Saari, K. M. (2002). Systemic bioavailability and cardiopulmonary effects of 0.5% timolol eyedrops. Graefes Arch Clin Exp Ophthalmol. 240, 430–435. doi: 10.1007/s00417-002-0462-2

[4] Yoshioka, K., and Kawasaki, T. (2025). Atrioventricular block caused by carteolol eye drops administered to unilateral eye or bilateral eyes: a case report. Cureus. 17, e90018. doi: 10.7759/cureus.90018

[5] Bollinger, A., Jeiziner, C., Meyer zu Schwabedissen, H., Hersberger, K., Allemann, S., and Stäuble, C. (2023). Severe systemic adverse reactions to ophthalmic timolol in a CYP2D6 homozygous *4 allele carrier: a case report. Pharmacogenomics. 24, 739–746. doi: 10.2217/pgs-2023-0122

[6] Pringle, S. D., and MacEwen, C. J. (1987). Severe bradycardia due to interaction of timolol eye drops and verapamil. BMJ. 294, 155. doi: 10.1136/bmj.294.6565.155-a

[7] Rains, J., and Kesterson, J. (2021). Ocular timolol as the causative agent for symptomatic bradycardia in an 89-year-old female. Am J Emerg Med. 42, 263.e5–263.e6. doi: 10.1016/j.ajem.2020.09.030

[8] Abbas, S., Hamadani, S., Ahmad, U., Desai, A., and Kitchloo, K. (2020). Ophthalmic timolol and hospitalization for symptomatic bradycardia and syncope: a case series. Cureus. 12, e7270. doi: 10.7759/cureus.7270

[9] Kiryazov, K., Stefova, M., and Iotova, V. (2013). Can ophthalmic drops cause central nervous system depression and cardiogenic shock in infants? Pediatr Emerg Care. doi: 10.1097/pec.0b013e3182aa1384

[10] Rangan, C., Everson, G., and Cantrell, F. (2008). Central alpha-2 adrenergic eye drops. Pediatr Emerg Care. 24, 167–169. doi: 10.1097/pec.0b013e3181668aee

[11] Hoffmann, U., Kuno, S., Franke, G., Fusch, C., and Haas, J. (2004). Pediatr Crit Care Med. 5, 282–285. doi: 10.1097/01.pcc.0000123548.73664.18

[12] Gunes, A., Balik, H., Yel, S., Kocamaz, H., and Bosnak, M. (2016). Turk J Emerg Med. 16, 169–170. doi: 10.1016/j.tjem.2016.02.002

[13] Sacchi, M., Lizzio, R., Villani, E., Monsellato, G., Lucentini, S., Cremonesi, E., et al. (2020). Medical management of pediatric glaucoma: lessons learned from randomized clinical trials. Graefes Arch Clin Exp Ophthalmol. 258, 1579–1586. doi: 10.1007/s00417-020-04767-9

[14] Xu, L., Wang, X., and Wu, M. (2017). Topical medication instillation techniques for glaucoma. Cochrane Database Syst Rev. 2, CD010520. doi: 10.1002/14651858.cd010520.pub2

[15] Diggory, P., and Franks, W. (1997). Glaucoma therapy may take your breath away. Age Ageing. 26, 63–67. doi: 10.1093/ageing/26.2.63

[16] Masnoon, N., Shakib, S., Kalisch-Ellett, L., and Caughey, G. E. (2017). What is polypharmacy? A systematic review of definitions. BMC Geriatr. 17, 230. doi: 10.1186/s12877-017-0621-2

[17] Xiong, G., Yang, Z., Yi, J., Wang, N., Wang, L., Zhu, H., et al. (2022). DDInter: an online drug-drug interaction database towards improving clinical decision-making and patient safety. Nucleic Acids Res. 50, D1200–D1207. doi: 10.1093/nar/gkab880

[18] Tian, Y., Yi, J., Wang, N., Wu, C., Peng, J., Liu, S., et al. (2024). DDInter 2.0: an enhanced drug interaction resource with expanded data coverage, new interaction types, and improved user interface. Nucleic Acids Res. 53, D1356–D1362. doi: 10.1093/nar/gkae726

[19] Percha, B., and Altman, R. B. (2013). Informatics confronts drug-drug interactions. Trends Pharmacol Sci. 34, 178–184. doi: 10.1016/j.tips.2013.01.006

[20] Yao, H., Peng, Z., Huang, Y., Xiao, S., and Wu, R. (2025). Gaps in the detection of drug-drug interactions between antipsychotic and cardiometabolic medications: a multisource analysis. BMC Med. 23, 622. doi: 10.1186/s12916-025-04420-4

[21] Singh, P., Devadiga, A., Pal, R., Betrabet, P., Sankar, J., Sethi, T., et al. (2026). ContraIndicator: a natural language processing-based approach to potential drug-drug interaction detection in pediatric intensive care. Clin Drug Investig. 46, 331–341. doi: 10.1007/s40261-026-01529-z

[22] Chou, E., Boyce, R. D., Balkan, B., Subbian, V., Romero, A., Hansten, P. D., et al. (2021). Designing and evaluating contextualized drug-drug interaction algorithms. JAMIA Open. 4, ooab023. doi: 10.1093/jamiaopen/ooab023

[23] Clusmann, J., Freyer, O., Ostermann, M., Ferber, D., Ghaffari Laleh, N., Hilgers, L., et al. (2026). Safety and security of large language models in healthcare. Nature. 656, 577–589. doi: 10.1038/s41586-026-10687-1

[24] Leibovitch, L., Ahituv, A., Gorenshtein, A., Aran, D., Sorka, M., Miron, K., et al. (2026). Nat Med. 32, 3741–3747. doi: 10.1038/s41591-026-04601-5

[25] Robertson, S., and Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. Found Trends Inf Retr. 3, 333–389. doi: 10.1561/1500000019

[26] Guo, Z., Xia, L., Yu, Y., Ao, T., and Huang, C. (2024). LightRAG: simple and fast retrieval-augmented generation. arXiv:2410.05779. doi: 10.48550/arXiv.2410.05779

[27] Kawamoto, K., Houlihan, C. A., Balas, E. A., and Lobach, D. F. (2005). Improving clinical practice using clinical decision support systems: a systematic review of trials to identify features critical to success. BMJ. 330, 765. doi: 10.1136/bmj.38398.500764.8F

[28] Bright, T. J., Wong, A., Dhurjati, R., Bristow, E., Bastian, L., Coeytaux, R. R., et al. (2012). Effect of clinical decision-support systems: a systematic review. Ann Intern Med. 157, 29–43. doi: 10.7326/0003-4819-157-1-201207030-00450

[29] van der Sijs, H., Aarts, J., Vulto, A., and Berg, M. (2006). Overriding of drug safety alerts in computerized physician order entry. J Am Med Inform Assoc. 13, 138–147. doi: 10.1197/jamia.M1809

[30] Edrees, H., Amato, M. G., Wong, A., Seger, D. L., and Bates, D. W. (2020). High-priority drug-drug interaction clinical decision support overrides in a newly implemented commercial computerized provider order-entry system: Override appropriateness and adverse drug events. J Am Med Inform Assoc. 27, 893–900. doi: 10.1093/jamia/ocaa034

[31] Ray, C. E., Wilson, G. M., Hughes, A. M., Cunningham Goedken, C., Liu, E. P., Fitzpatrick, M. A., et al. (2026). Alert fatigue measurement in clinical decision support: a systematic review. J Am Med Inform Assoc. 33, 1523–1531. doi: 10.1093/jamia/ocag064

[32] Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., et al. (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 385, e078378. doi: 10.1136/bmj-2023-078378

[33] Vasey, B., Nagendran, M., Campbell, B., Clifton, D. A., Collins, G. S., Denaxas, S., et al. (2022). Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI. Nat Med. 28, 924–933. doi: 10.1038/s41591-022-01772-9

[34] Joint Formulary Committee (2026). Glaucoma and ocular hypertension. In: British National Formulary. London: BMJ Group and Pharmaceutical Press. doi: 10.18578/bnf.270842008

[35] Müller, L., Jensen, B. P., Bachmann, L. M., Wong, D., and Wells, A. P. (2020). New technique to reduce systemic side effects of timolol eye drops: the tissue press method - crossover clinical trial. Clin Exp Ophthalmol. 48, 24–30. doi: 10.1111/ceo.13642

[36] Xu, Z., Liang, J., Cai, W., Luo, Y., Liang, F., Lin, R., et al. (2026). A systemic pharmacovigilance assessment of ophthalmic atropine: signal detection and clinical prioritization from the FAERS database. Front Med (Lausanne). 13, 1798521. doi: 10.3389/fmed.2026.1798521

[37] Jumbe, N., and Miller, M. (2021). Ocular drug transfer following systemic drug administration. In: Ophthalmic Drug Delivery Systems. 3rd ed. Boca Raton: CRC Press; doi: 10.4324/9781003113423-6

[38] Cohen, J. (1960). A coefficient of agreement for nominal scales. Educ Psychol Meas. 20, 37–46. doi: 10.1177/001316446002000104

[39] Landis, J. R., and Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics. 33, 159–174. doi: 10.2307/2529310

[40] Prasad, M., and Ramsey, D. (2026). Adverse events reported with standard-dose and high-dose aflibercept: a FAERS pharmacovigilance study. Vision. 10, 18. doi: 10.3390/vision10020018

[41] Ryu, J. Y., Kim, H. U., and Lee, S. Y. (2018). Deep learning improves prediction of drug-drug and drug-food interactions. Proc Natl Acad Sci U S A. 115, E4304–E4311. doi: 10.1073/pnas.1803294115

[42] Lin, X., Zhang, S., Li, B., Liang, P., and Pang, J. (2026). HSAF-DDI: Heterogeneous Semantic-Aware Drug-Drug Interaction Prediction with Hierarchical Adaptive Fusion. J Chem Inf Model. 66, 10379–10395. doi: 10.1021/acs.jcim.6c01086
