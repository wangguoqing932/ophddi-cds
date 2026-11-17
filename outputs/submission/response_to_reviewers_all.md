# Response to Reviewers

**Manuscript:** 2032864 — OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening  
**Journal:** Frontiers in Pharmacology — Drugs Outcomes Research and Policies  
**Date:** 14 November 2026

This document combines the point-by-point responses to Reviewer 1 (10 comments) and Reviewer 2 (7 comments). The two letters are also provided as separate files.

## Contents

1. Response to Reviewer 1
2. Response to Reviewer 2

---


# Response to Reviewer 1

**Manuscript:** 2032864 — *OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening*
**Journal:** Frontiers in Pharmacology — Drugs Outcomes Research and Policies
**Date:** 10 November 2026

We thank Reviewer 1 for a rigorous and constructive report. The revision is not a text-only response. We re-derived every affected number from the deposited prediction files, corrected the pharmacological inputs, changed the engine to expose an unassessed status, rebuilt Tables 3 and 5, regenerated Figures 1 and 2, and added a rule-level provenance audit. The primary analysis now uses the labels as frozen before the three post-lock corrections, and the word "accuracy" has been replaced by "exact agreement" against an author-derived reference set. All new numbers can be regenerated with `scripts/revision_r1_stats.py`, `scripts/recompute_development_metrics.py` and `scripts/build_revision_tables.py`.

## Summary of changes

| Reviewer item | What changed | Where |
|---|---|---|
| 1. Reference-standard independence | Frozen labels are the primary analysis (101/118, 0.856); corrected labels are a sensitivity analysis (104/118, 0.881); the 40-case frozen blind set is reported separately (36/40, 0.900), with the 20 B-only cases at 18/20 frozen and 20/20 corrected; "accuracy" replaced by "exact agreement". | §3.3, Table 3, Supplementary Table S1 |
| 2. Absorption evidence | All 13 registry-versus-curation discrepancies resolved; 8 curation values corrected to the registry and 5 products re-tiered (3 dexamethasone products high to medium; 2 carbonic-anhydrase inhibitors low to very low); new per-agent evidence table with formulation, dosing, exposure evidence, source and certainty (13 measured, 11 label, 89 class-inferred). | §2.2, §4.4, Tables S5/S5b/S10 |
| 3. Low-risk safeguards | Default path now returns `assessment_status = unassessed`; 176/1,933 pairs (9.1%) flagged and listed; full path attribution; dose, duration, susceptibility and local interactions stated as unmodelled; gating sensitivity reported. | §2.2, §2.6, §3.4, §4.2, Table S11 |
| 4. Route scope | Principal analysis repeated on 104 topical agents (1,930 pairs, 77.7%); 9 non-topical agents reported separately; anti-VEGF agents justified individually; fixed combinations decomposed per component. | §2.2, §3.4, Tables S10/S12 |
| 5. External audit | Both applied and re-derived reference sets reported in full; sensitivity 8/25 (0.320) and 8/29 (0.276); 30 disagreements classified into 21 route-consistent, 5 unsupported undergradings and 4 over-grades. | §3.5, Table 5, Table S2 |
| 6. LLM comparison | Renamed `rule_context`; two configurations described without causal budget language; retrieval overlap measured before the between-method comparison for all methods. | §2.4, §3.6, Table S13 |
| 7. Numerical statements | High-risk assignment corrected to 2.2%, 10.9% and 6.5%; majority-vote range corrected to 6-15. | §3.6 |
| 8. Clinical implications | 1% prevalence/PPV calculation removed; claims narrowed to classification divergence, not alert correction or prescribing safety. | §4.1, §4.4, §5 |
| 9. Clinician exercise | Speculative explanations removed; the exercise is described as purely descriptive and not representative of clinical opinion. | §2.5, §3.8, §4.1 |
| 10. Provenance and reproducibility | 40-rule audit (2 direct, 5 contextual, 23 class-extrapolated, 10 mechanism-only); digoxin citation corrected; archive statement reconciled; supplementary sections renumbered without gaps; ethics wording reconciled. | §2.2, §4.4, Declarations, Tables S9 |

## Point-by-point response

### Reviewer 1, comment 1

> The headline accuracy is not an independent validation result. Forty-seven guideline-derived reference labels reproduce the severity assigned by the corresponding rules, 78 of the 118 cases overlap the internal development set, and three labels were changed to match the engine after the dataset was locked. Although these issues are acknowledged, describing the overall 90.7% agreement as "accuracy" against a "gold" standard remains potentially misleading. Please present it consistently as agreement with an author-derived reference set, report the original frozen labels as the primary analysis of that subset, and separately report the cases without development exposure. A new, independently adjudicated test set is needed to support clinical performance claims.

**Response.** We agree, and the revision changes the primary analysis rather than adding another caveat.

First, the terminology is now "exact agreement" against an "author-derived reference set"; "accuracy" and "gold" are no longer used for this set. Second, the primary analysis uses the labels as frozen on 31 July 2026. Under those labels the cascade agrees exactly on 101 of 118 cases (0.856; Wilson 95% CI 0.781-0.908), with high-risk sensitivity 0.857 (24/28; CI 0.685-0.943), specificity 0.978 and kappa 0.779 (bootstrap CI 0.678-0.870). The three post-lock corrections are reported as a sensitivity analysis: 104 of 118 (0.881), sensitivity 0.893, specificity 0.989, kappa 0.818. Third, the 40-case frozen blind set is reported separately: 36 of 40 (0.900; CI 0.769-0.960), sensitivity 0.818 (9/11), specificity 0.966; under the corrected labels, 39 of 40. Within it, the 20 B-only cases scored 18/20 frozen and 20/20 corrected; the 20 C-only cases, which entered the class-matrix loop in v2.1-v2.3, scored 18/20 and 19/20. Fourth, the decomposition of the headline is now explicit: 40 of 47 rule-fidelity cases, 5 of 11 hand-overridden cases, and 56 of 60 T1 and frozen cases. The manuscript states that no independently adjudicated test set exists, that the 20 B-only cases are reported separately but are not development-free and are too small for a clinical performance claim, and that a prospectively locked, independently adjudicated set is the next requirement.

**Changes:** Abstract; §2.3; §3.3 (rewritten); §4.1; §4.4 (Validation); §5; Table 3; Supplementary Table S1 (now lists all 17 frozen-label disagreements, including the three errata cases and the two created by the absorption gate on `nsaid_antihypertensive_antagonism`, see comment 3).

### Reviewer 1, comment 2

> The absorption categories need defensible, drug-specific evidence. These categories drive the principal findings, yet most entries provide only a generic DrugBank identifier or "PubMed," without the pharmacokinetic evidence or operational thresholds supporting the assignment. Fractional bioavailability, plasma concentration and exposure relative to an oral dose should not be treated as interchangeable. Please document the formulation, concentration, dosing conditions, measured exposure and source supporting each category, or explicitly identify the assignment as uncertain. The 13 remaining discrepancies between the registry and curation file should be resolved before publication, rather than deferred to future work.

**Response.** We resolved the 13 discrepancies and rebuilt the evidence base rather than deferring either issue.

The six tier bands now have an explicit operational definition in §2.2: high (at least 10% of an oral therapeutic exposure, or plasma concentrations within the systemic therapeutic range), medium (1-10%), low (below 1% but detectable), very low (below assay quantification), minimal (intravitreal macromolecular agents and intraocular agents with negligible systemic exposure) and none (viscoelastics and tear substitutes). We state that fractional bioavailability, plasma concentration and relative exposure are not interchangeable; the exposure metric is recorded for the 13 measured rows, the 11 label-statement rows record the label claim without a value, and the 89 class-inferred rows are marked uncertain.

Supplementary Table S5 now covers all 113 agents with a certainty label and source: 13 have a measured exposure value, 11 an explicit label statement, and 89 are class-level inferences marked uncertain. Supplementary Table S5b gives the formulation, concentration, dosing, exposure evidence and source for the 24 measured/label agents. The new Table S10 lists the 13 resolved discrepancies, the component-wise assignment of all fixed combinations, and the certainty counts.

Of the 13 discrepancies, eight curation-file values were corrected to the registry assignment (five timolol combinations, atropine, sulfacetamide/prednisolone, aceclidine). Five products were re-tiered on measured evidence: dexamethasone and its two fixed combinations moved from high to medium because peak plasma dexamethasone after 0.1% four times daily is below 1 ng/mL (TobraDex label, section 12.3), and dorzolamide and brinzolamide moved from low to very low because plasma concentrations are below assay quantification (Dorzolamide and Azopt labels, section 12.3). This correction changed individual case agreement in both directions; we report the net effect rather than retain a tier chosen to fit the labels.

**Changes:** §2.2 (Absorption tiers, rewritten); §4.4; Tables S5/S5b/S10; `data/curation/absorption_tier_evidence.csv`; `scripts/build_absorption_evidence_table.py`.

### Reviewer 1, comment 3

> The low-risk decision requires stronger safeguards. Low systemic absorption is not equivalent to absent exposure or established clinical safety. In addition, a registered pair without a matching rule or matrix cell currently defaults to low risk, which conflates insufficient knowledge with evidence of negligible risk. Please distinguish "unassessed/insufficient evidence" from "low risk" and quantify how many pairs follow each pathway. Explain how local ocular interactions, dose, duration and patient susceptibility are handled. The inconsistent absorption gating also needs attention: 95 low-or-below absorption pairs receive high grades through a single rule.

**Response.** We implemented the distinction in the engine, not only in the text.

Pairs that reach neither a rule nor a matrix cell now return low with `assessment_status = "unassessed"` and `note = "no matching rule or matrix cell; grade is not evidence of safety"`; defined `none` cells are assessed low, and low/very-low pairs with no signal are handled by G19. A regression test (`tests/test_assessment_status.py`) verifies the behaviour. The status is now propagated through `SafetyAgent` into `RiskAssessment` and surfaced in the interface as an UNASSESSED warning, so the service no longer presents these pairs as ordinary low risk. Of the 1,933 graded-severity pairs, 176 (9.1%) follow the default path; they include 151 DDInter-medium, 10 DDInter-high and 15 DDInter-low pairs and are listed individually in Supplementary Table S11. The full path distribution is 504 pairs by rule (26.1%), 507 by a defined matrix cell (26.2%), 746 by the G19 hard constraint (38.6%) and 176 by the default path (9.1%). Excluding the unassessed pairs, 1,341 of 1,757 assessed pairs (76.3%) were downgraded.

Dose, duration, patient susceptibility beyond three patient-factor policies, and local ocular interactions are not encoded; this is now stated in §2.6 and §4.4, together with the consequence that the tool cannot substitute for those clinical inputs.

On gating: we changed the behaviour rather than explaining it away. `nsaid_antihypertensive_antagonism` is now gated on absorption and cannot fire when the ophthalmic tier is low or lower. Across the full 113 x 232 grid, 157 low-or-below-tier pairs still receive medium grades through other rules, but none receives high (the ungated rule produced 95 high grades, all from this single rule). Within the 1,933 graded-severity pairs the corresponding figures are 83 pairs, all medium; the ungated counterpart was 115 pairs (47 medium, 68 high). Removing the gate raises frozen-label agreement from 0.856 (101/118) to 0.873 (103/118) and corrected-label agreement from 0.881 (104/118) to 0.898 (106/118), and restores the 95 high grades; we report this as the ungated sensitivity analysis in Supplementary Table S19. The agreement gain is expected because 47 of the 58 guideline labels encode the rule's own severity, so the ungated rule is partly fitting its own source. We keep the gate as the primary behaviour because it is consistent with the absorption model.

**Changes:** `src/ophthalmic_ddi_cds_agent/kg_layer.py`; `tests/test_assessment_status.py`; §2.2 (L2/L3); §2.6; §3.4; §4.2; §4.4; Table S11.

### Reviewer 1, comment 4

> The scope should be restricted or explicitly separated by route. Nine registry entries are intravitreal, intraocular or surgical agents, although the study and comparator prompts predominantly describe eye drops. Please repeat the principal analysis using the 104 topical agents and report other routes separately. Assigning all six intravitreal anti-VEGF agents to one "minimal absorption" category also requires individual justification. Combination products should be assessed for each active ingredient's mechanisms, rather than relying solely on a dominant-component absorption category.

**Response.** The principal analysis is now repeated on the 104 topical agents and the non-topical entries are reported separately.

Restricting to topical agents leaves 1,930 pairs: 1,499 (77.7%) were downgraded, 350 fell from high, and 1,203 of the downgrades (80.3%) involved low-tier ophthalmic agents. The nine non-topical agents contribute only three DDInter-matched pairs (all aflibercept; all three downgraded, two from high), which are reported separately in Supplementary Table S12. The conclusion is therefore a property of the topical-ophthalmic pairs in the registry, not of the three non-topical pairs.

The six intravitreal anti-VEGF agents are no longer a single class default. Each is listed individually in Table S5 with its molecular format and available serum-exposure evidence: ranibizumab (Fab, 48 kDa), aflibercept (115 kDa fusion protein), bevacizumab (149 kDa IgG1), brolucizumab (26 kDa scFv), faricimab (150 kDa bispecific) and conbercept (143 kDa fusion protein). All remain minimal on the available evidence (measured, label-statement or class-inferred); conbercept is class-inferred rather than label-stated, and brolucizumab rests on a label statement.

Fixed combinations are decomposed into their active components. The product's tier is the highest component tier, and the rule layer matches on the union of component mechanisms, so a combination is not represented by a single dominant component. Table S10 lists all 12 combinations with their component tiers.

**Changes:** §2.2; §3.4; Tables S10/S12; `data/curation/absorption_tier_evidence.csv`.

### Reviewer 1, comment 5

> The external audit needs a consistent reference standard and a clearer safety analysis. Thirty audit labels incorporate the system's own absorption assumption, and the stated correction procedure was applied inconsistently. The re-derived reference labels should be clearly distinguished from the originally applied labels, with complete results for both. The system identifies only 8 of 25 reference-high pairs, falling to 8 of 29 under the re-derived labels. Please provide a focused, independently reviewed analysis of these disagreements, separating plausible route-related downgrading from unsupported undergrading. These are reference-label disagreements; without outcome data, they should not be equated directly with missed clinical adverse events.

**Response.** Both reference sets are now reported in full, and the disagreement analysis separates route-consistent from unsupported undergrading.

Under the applied labels the cascade reaches 62 of 92 (0.674; CI 0.573-0.761), kappa 0.428, specificity 0.970 and high-risk sensitivity 8 of 25 (0.320; CI 0.172-0.516). Under the re-derived labels it reaches 61 of 92 (0.663; CI 0.562-0.751), kappa 0.434, specificity 0.968 and sensitivity 8 of 29 (0.276). Table 5 gives both sets in full, together with the 62 label-independent cases (34/62, 0.548 applied) and the 26 retrieval-overlap exclusions. Supplementary Table S2 lists all 30 disagreements with tier, path, matched rules and direction.

The author classification divides the 30 disagreements into 21 route-consistent downgrades (medium-, low- or minimal-tier agents, consistent with the absorption model; 15 medium, 4 low and 2 minimal), 5 unsupported undergradings of high-tier agents (timolol + theophylline, timolol + epinephrine, scopolamine + topiramate, timolol + spironolactone, carteolol + diazepam) and 4 over-grades (apraclonidine + midazolam, apraclonidine + loperamide, tacrolimus + ibuprofen, bromfenac + enalapril). The five high-absorption-tier undergradings are the clearest author-identified subset (three DDInter-high and two DDInter-medium), but they are not the whole clinically critical set: 12 disagreements are on the unassessed default path (10 route-consistent, 2 unsupported), adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080) whose low grade is not evidence of safety.

To test that classification, we asked an independent ophthalmologist (not an author; blinded to the author class, decision path and matched rules) to reclassify all 30 from the same pair, reference label, system grade, tier and direction. Exact agreement was 14 of 30 (46.7%); on the 28 cases within the author's three classes, 14 of 28 (50.0%, kappa 0.271). The reviewer classified 14 of the 21 author route-consistent downgrades as unsupported undergrading, kept all five author unsupported undergradings as unsupported, and considered two of the four author over-grades to be supported upgrades. The independent view is therefore more conservative and does not reproduce the 21/5 split; it reinforces, rather than resolves, the false-negative concern. We retain the author classification as a descriptive categorization and report both columns in Supplementary Table S2. These are disagreements with reference labels, not counts of missed adverse events.

We also considered whether these disagreements correspond to recognized clinical events. In a scoping PubMed search of the 13 highest-risk pairs (13 November 2026; both drug names plus an ophthalmic/topical/eye term), 10 of 13 returned no ophthalmic record at all; the three non-zero results were pharmacology, review or animal studies, not case reports of the interaction. This scarcity is consistent with the view that several of these combinations are uncommon and may have limited clinical significance at ophthalmic exposure. We do not use it to reclassify any case: absence of a published case is not evidence of safety, under-reporting is likely, and the independent review in fact classified more downgrades as unsupported, not fewer. The search is reported as context, not as an outcome standard, in the Supplementary Table S2 note and the audit record.

**Changes:** §2.3; §3.5 (rewritten); Table 5; Supplementary Table S2.

### Reviewer 1, comment 6

> The LLM comparison cannot establish an effect of output budget or reasoning. The second setting changes the model, token allowance and sampling procedure simultaneously. Statements attributing the findings to "more room" or a larger output budget therefore exceed the design. Either compare budgets within the same model and sampling protocol or describe the results strictly as differences between two configurations. The comparator called "LightRAG" receives configured rule outputs rather than performing the stated graph-retrieval evaluation; it should be renamed accordingly. Retrieval overlap with reference labels should be addressed prospectively and consistently across methods, rather than relying principally on post hoc exclusion.

**Response.** We removed the causal budget claim and renamed the comparator.

The two settings are now called configuration 1 (`deepseek-chat`, 10-token cap, five temperature conditions) and configuration 2 (`glm-5.3-flash`, `max_tokens` 3000, temperature 0.0, majority vote over five repeats). The manuscript states that they differ in model, token allowance and sampling simultaneously, so the comparison describes two configurations and does not isolate the effect of output budget or reasoning. All "more room", "larger budget" and "artefact of the decision rule adopted with more room" language has been removed.

The comparator is renamed `rule_context`. The manuscript explains that it adds a knowledge-graph context block rendered from the registries and rule configuration, including matched rule identifiers and severities, and therefore receives part of the rule layer rather than performing a graph-retrieval evaluation. The internal method id `lightrag` is retained in the deposited code for continuity only.

Retrieval overlap is now measured before the between-method comparison and reported for every method: `naive_rag` contains the pair's own DDInter statement for 26 of 92 audit cases (19 of the 62 kept cases and 7 of the 30 corrected cases); `pure_llm` and `rule_context` have no DDInter-statement retrieval channel by construction. Results with and without the 26 cases are reported for the cascade in Table 5 and for all methods in Table S13, not only for the affected method. We also removed the previous claim that `lightrag` shows "a weaker version of the same effect", because it does not retrieve from the DDInter corpus.

**Changes:** §2.4; §3.6 (rewritten); Table 5; Table S13; Figure 2.

### Reviewer 1, comment 7

> Several numerical statements require correction. In Section 3.6, the statement that the adequate-budget baselines assign high risk to 2% of audit cases is inconsistent with Table 3. Given 25 high-reference cases and specificity of 1.000, the reported sensitivities imply 2, 10 and 6 high predictions out of 92-approximately 2.2%, 10.9% and 6.5%, respectively. Likewise, the reported majority-vote range of "7 to 15" correctly identified high-risk L1 cases should be 6 to 15, because sensitivity of 0.214 corresponds to 6/28.

**Response.** Both corrections are implemented and verified against the prediction files.

In configuration 2 the three baselines assign high risk to 2 of 92 (2.2%), 10 of 92 (10.9%) and 6 of 92 (6.5%) audit cases; the previous "2%" is removed. On the L1 set the number of correctly identified reference-high cases ranges from 4 to 9 across repeats for `naive_rag` and the majority-vote counts are 7, 6 and 15 for `pure_llm`, `naive_rag` and `rule_context`; the previous "7 to 15" is corrected to "6 to 15".

**Changes:** §3.6.

### Reviewer 1, comment 8

> The clinical implications should remain narrower than the current discussion. The 75.3% downgrade rate demonstrates divergence produced by the chosen model; it does not establish correction of inappropriate alerts or improved prescribing safety. Similarly, sensitivity and specificity measured against severity labels cannot establish predictive value for actual adverse events. The illustrative 1% prevalence calculation should either be removed or explicitly framed as a hypothetical calculation about reference-label classification, without implying clinical event prediction.

**Response.** We removed the prevalence calculation and narrowed the claims.

The 1% prevalence/PPV paragraph is deleted. The manuscript now states that no outcome data are available, so predictive value for adverse events cannot be estimated. The 77.7% figure is described as a property of the stated absorption model, not evidence that alerts were inappropriate or that prescribing would improve. The earlier phrase "would reach a prescriber at a different grade" has been removed; the manuscript now describes the result as "a difference in classification" (Sections 3.3 and 4.3). The Discussion states that sensitivity and specificity against severity labels cannot establish predictive value for clinical events.

**Changes:** §3.4; §4.1; §4.4 (Bounded clinical impact); §5.

### Reviewer 1, comment 9

> The clinician exercise should remain purely descriptive. Both reference and displayed system grades were visible, one clinician belonged to the research team, and two displayed grades differed from the actual engine outputs. These limitations are disclosed appropriately, but explanations attributing disagreement to clinicians' recall or expectations of rare events were not tested. Please remove these speculative explanations and avoid treating agreement between two clinicians as evidence of general clinical opinion. Future assessment should use blinded, independent reviewers, including clinical pharmacy expertise.

**Response.** The speculative explanations are removed, and the exercise is described as purely descriptive.

The sentences attributing the divergence to the rarity of serious events, clinicians' recall of non-selective beta-blockers, or expectations of rare events are deleted. The manuscript states that two clinicians are a purposive panel, not a sample of clinical opinion; that the design cannot distinguish a perspective gap from case-selection effects; and that the exercise shows only that the two raters did not reproduce the assigned grades. The Discussion and Conclusions no longer treat inter-rater agreement as evidence of general clinical opinion. The future-directions section calls for blinded, independent reviewers including clinical pharmacy expertise.

**Changes:** §2.5; §3.8; §4.1; §4.5.

### Reviewer 1, comment 10

> Rule provenance and reproducibility need final correction. Source-record availability does not establish that a source supports the specific interaction, route and assigned severity. Please verify these elements for every rule, including the acknowledged digoxin citation mismatch. Also reconcile statements that a versioned archive already exists with statements that it will be deposited on acceptance; correct supplementary cross-references to nonexistent sections; and clarify the institutional basis for the ethics determination concerning the clinician-rating exercise. The statement that there were "no human participants" should be reconciled with the participation of two clinicians.

**Response.** We audited all 40 rules and corrected the specific mismatches, then reconciled the archive, cross-reference and ethics statements.

The rule audit scores every rule on three questions: whether the source concerns the named ophthalmic agent, whether it supports the pair, and whether it supports the assigned severity and route. The result is 2 rules with direct ophthalmic pair evidence, 5 with contextual ophthalmic evidence, 23 with systemic-route class evidence extrapolated to the ophthalmic agent, and 10 with mechanism-only support; severity is directly supported for 2, inferred for 28 and provisional for 10. Table S9 lists every rule.

The digoxin citation mismatch is corrected: the Schuman 2000 citation, which addresses topical-plus-systemic beta-blockade but not digoxin, has been removed; the rule carries only its DDInter pair record and is labelled class-extrapolated. Three further citation errors were corrected: the warfarin rule cited timolol; the two low-absorption antiplatelet/anticoagulant rules cited latanoprost. Those two are relabelled as absorption priors rather than pair-level DDI evidence.

The archive statements are reconciled. The version matching the submitted manuscript is archived at DOI 10.5281/zenodo.23439606 (record v3.0-frontiers, 17 October 2026); the revision will be deposited as a new version of the same record. The contradictory "will be deposited on acceptance" sentence has been replaced.

The supplementary material has been renumbered without gaps: Supplementary Texts S1-S10 and Tables S1-S19, and the manuscript was checked with `scripts/audit_manuscript.py` for dangling section, table and text references.

The ethics statement now says that the study involved no patients, no patient-level data and no clinical intervention; that the authors determined under the Declaration of Helsinki and the Chinese Measures for Ethical Review of Life Science and Medical Research Involving Humans that no submission was required; that the competent committee is the Ethics Committee of the First Affiliated Hospital of Xinjiang Medical University; and that no formal determination was issued. The two clinicians took part in an anonymous professional-opinion exercise with no personal data and no intervention; the "no human participants" phrasing has been replaced by "no patients", and the exercise is described as descriptive and non-independent.

**Changes:** §2.2 (Rule construction, adjudication and provenance); §4.4; Declarations (Ethics, Data availability); Supplementary Text S2; Tables S9/S10; `configs/rules.yaml`; `data/curation/rule_provenance_audit.csv`.

## Response to the Reviewer's checklist

**(a) Figures and tables.** Figure 1 now shows the corrected tier distribution (12 high, 20 medium, 59 low, 11 very low, 7 minimal, 4 none). Figure 2 now shows the frozen-label primary analysis in panel (a) and configuration 2 in panel (b), with the comparator renamed. Table 3 has been rebuilt to separate frozen, corrected, frozen-blind, audit-applied and audit-re-derived results. Table 5 now reports both audit label sets, the label-independent subset, the retrieval-overlap exclusion and the disagreement classification.

**(b) Reference list.** The list was re-audited against the claims it supports. Four citation mismatches were corrected (digoxin, warfarin, two low-absorption rules), and three verified reviews of ocular pharmacokinetics and systemic absorption were added [1-3]. The rule-level provenance audit (Table S9) is now the explicit record of what each source supports, rather than a claim that every rule is independently verified.

**(c) Statistical methods.** The primary analysis now uses the frozen labels; the corrected labels are a sensitivity analysis. The audit reports both applied and re-derived labels with Wilson intervals and kappa. The PPV calculation was removed. Exact McNemar tests remain the inferential test, with the discordant-pair counts reported. We state that no power calculation was performed and that the 20 B-only cases are too small for a clinical performance claim.

**(d) Statistician.** We agree that an independent statistical review would be valuable and would welcome it. The revision separates descriptive from inferential analyses, states the aggregation rule for each table (mean over five temperature conditions vs majority vote over five repeats), and removes the unsupported predictive-value calculation.

**(e) Replication.** The revision adds `scripts/revision_r1_stats.py` (all revision statistics), `scripts/build_revision_tables.py` (Tables 3 and 5 and S9-S13), `scripts/build_absorption_evidence_table.py` (per-agent tier evidence), `data/curation/rule_provenance_audit.csv`, `data/curation/absorption_tier_evidence.csv`, and `tests/test_assessment_status.py`. All deterministic-cascade and prediction-file numbers in the revised manuscript and supplement can be regenerated without model access; the Lexicomp comparison is deposited as aggregate results, not case-level ratings.

## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data, the development log and the reference list identified the following issues; all were corrected in the same revision.

1. **The 20 B-only cases are not development-free.** The internal development log shows that B02 and B12 were corrected after engine review, B18 and B19 informed matrix design, and other B cases informed rule-gap diagnosis. Section 2.3 now states that neither half of the 40-case set is an independent test and that the 20/20 corrected figure is partly tautological because both B02 and B12 were moved toward the engine's grade. The Table 3 note that had said B01–B20 were never used in development has been removed. The 18/20 frozen and 20/20 corrected values are unchanged and are reported as descriptive only.

2. **The registry-scale denominator is 1,933 graded-severity pairs, not all matched pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. Section 2.3, Section 3.4 and the Limitations now state this, and the 77.7% result is described as applying to pairs with a graded severity; its generalization to `Unknown` pairs is unknown. A denominator audit (`scripts/audit_ddinter_denominator.py`; `outputs/audits/ddinter_denominator_audit.json`) regenerates the 4,546 / 2,613 / 1,933 counts.

3. **The 80.3% figure is a composition statistic, not a causal decomposition.** Of the 1,502 downgrades, 1,206 involved low-tier ophthalmic agents; of these, 698 were assigned low by G19 and 72 by absorption-forced matrix scaling, while 436 were decided by a rule or matrix cell whose level does not depend on the tier. The text now uses "involved" and labels the figure as a composition statistic.

4. **The five unsupported downgradings are the clearest author-identified subset, not the whole clinically critical set.** They comprise three DDInter-high and two DDInter-medium pairs. Twelve disagreements are on the unassessed default path (10 route-consistent, 2 unsupported), adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080) whose low grade is not evidence of safety. The independent review was more conservative still: it classified 14 of the 21 author route-consistent downgrades as unsupported, so the author 21/5 split is descriptive and is not reproduced (14/30 exact; kappa 0.271). Both columns are now in Table S2.

5. **The timolol evidence line was overstated.** The cited studies support approximately 78% systemic bioavailability relative to intravenous timolol in one crossover study, not a 50–78% range or a comparison with oral doses; Table S5b now states this. The timolol tier remains high because the reported exposure is well above 10% of an oral therapeutic dose.

6. **The internal development metrics were corrected.** The previously reported sensitivity of 0.353 was 6/17 from an old case-ID mapping, not the current engine's 15/17 = 0.882; the 0.895 specificity came from the ungated analysis and had been mixed with the gated 0.240 agreement. The corrected gated values are sensitivity 0.882 (15/17), specificity 0.984, and 0.240 / 0.069 / 0.977 on the 200-case development set. The only two high-label cases lost to the gate are G137 and G138.

7. **The expert summary was rebuilt from the deposited records.** Inter-rater kappa is 0.840 (not 0.846); R03 is low/low (not medium); the grade displayed for R10 and R11 was medium; expert-versus-displayed agreement is 2/12 and 1/12 (not 0.417 and 0.333). The manuscript and Table S3 now use the transcribed per-case record; the exercise remains descriptive and non-independent.

8. **Table 4 and Table S8 now show both label distributions.** The tables previously showed only the corrected distribution (28 high / 51 medium / 39 low) without saying so, while the primary analysis uses the frozen labels (28 / 50 / 40). Both distributions are now labelled, and Section 2.3 no longer quotes an unlabelled distribution.

9. **Configuration 2 prompt comparability is now stated.** Configuration 2 `rule_context` used the pre-correction context block, and `pure_llm` and `naive_rag` were not re-run after the tier correction, whereas configuration 1 `rule_context` was re-run. The baseline comparison therefore mixes a corrected `rule_context` row with uncorrected rows and is not a clean test of retrieval augmentation (Section 2.4, Section 3.6, Figure 2 legend).

10. **Reference metadata were re-checked.** [45] is the 2nd edition (Routledge); missing titles, volume or page numbers in [13–16,29] were supplied; the duplicate "Sacchi, M." in [17] was removed (PubMed lists a single Sacchi). Reference [37] remains "3, 333–389": the Crossref/Zotero record "4(1–2), 1–174" is a publisher metadata collision with 10.1561/1500000013 and is not the correct pagination (Semantic Scholar/DBLP give 3:333–389). Of the 45 DOIs, 44 are Crossref-verified, the arXiv DOI [36] resolves through DataCite, and all 45 entries are present in the Zotero audit library. The compiled PDF and DOCX have been rebuilt so that they match the source.

## Closing

We are grateful for the reviewer's insistence on separating development agreement from independent evaluation, on documenting the pharmacological inputs, and on reconciling the provenance record. The revision is materially narrower in its claims and more auditable in its inputs. We hope it is now suitable for publication as a methodological development study.

---

# Response to Reviewer 2

**Manuscript:** 2032864 — *OphDDI-CDS: An Absorption-First Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening*
**Journal:** Frontiers in Pharmacology — Drugs Outcomes Research and Policies
**Date:** 11 November 2026

We thank Reviewer 2 for a constructive and clinically grounded report. The revision adds the requested methodological detail, makes the grade definitions and intended workflow explicit, separates exposure from risk, and adds a route-aware comparison. It also states more plainly what the system does not do. The changes are integrated with the Reviewer 1 revision in a single manuscript; this document responds only to Reviewer 2.

## Summary of changes

| Reviewer item | What changed | Where |
|---|---|---|
| 1. Rule and matrix construction | Added the candidate-generation, encoding, severity-assignment and adjudication procedure; added the full 104-cell matrix table; state that adjudication was by study-team consensus, without a formal Delphi panel. | §2.2; Supplementary Text S10; Tables S9 and S14 |
| 2. Grade definitions and clinical significance | Added operational definitions, clinical significance, expected management and an illustrative pair for high, medium, low and unassessed. | §2.2; Table 6 |
| 3. Patient-specific factors | Added a factor-by-factor table covering age, renal and hepatic function, QT risk, dose, duration, CYP phenotype and instillation technique, with representation, effect on output and gap. | §2.2; Supplementary Table S15; §4.4 |
| 4. A-E grading | Reframed A-E as a source hierarchy, not a strength-of-evidence grade; added definitions of what each tier can and cannot support. | §2.1; Supplementary Table S16 |
| 5. Exposure versus risk | Added a mechanism-specific analysis of when reduced exposure does and does not reduce clinical interaction risk. | §4.3; Supplementary Table S17 |
| 6. Route-aware comparison | Added a route-aware DDInter filter (RA-DDInter) on the 42 L1 cases and across the 1,933 pairs with a graded DDInter severity, plus a comparison with Lexicomp (route-specific product entries, 2018 UpToDate/OpenMed instance) on the same 42 cases; the 2018 edition is stated as a limitation. | §3.9; Table 7; Supplementary Tables S18 and S18b |
| 7. Intended workflow | Added a workflow figure and a stepwise description of how high, medium, low and unassessed outputs are expected to influence management. | §2.2; Figure 6 |

## Point-by-point response

### Reviewer 2, comment 1

> The development of the 40 mechanism rules and the class matrix should be described more clearly, including how severity grades were assigned and adjudicated.

**Response.** We added a dedicated methods passage and two supporting tables.

Candidate rules were generated from three sources: DDInter 2.0 pairs linking an ophthalmic agent to a systemic drug class, ophthalmic product labels (warnings and drug-interaction sections), and published case reports or reviews. Each candidate was encoded as an entity-flag predicate with match-all or match-any semantics, and the highest-severity hit is retained. Severity was assigned in a fixed order: the DDInter level where the pair was recorded; otherwise the label's warning category; otherwise the clinical consequence expected from the mechanism and the therapeutic index of the systemic drug. The rule inventory was reviewed by the study team and the two clinician authors; disagreements were resolved by consensus. We state explicitly that there was no formal Delphi panel, blinded review or independent clinical committee. Supplementary Table S9 records two separate dimensions: evidence grade (2 direct ophthalmic pair, 5 contextual ophthalmic, 23 systemic-route class, 10 mechanism-only) and severity support (2 direct, 28 inferred, 10 provisional).

The class matrix is now documented in the same way. The 21 ophthalmic row keys and 34 systemic column keys (33 with defined cells, drawn from the 40 systemic classes) were defined from the registry classes; 83 actionable cells were defined from the rule set, class extrapolation, expert consensus or pharmacological inference; 21 additional cells in the `other` column are explicitly marked "none" (defined as not established, not default-low). Each cell in the configuration records a level, mechanism, advice and evidence type; Supplementary Table S14 reports the level, mechanism and evidence type for all 104 cells, and Supplementary Text S10 gives the construction and adjudication protocol. Cell levels were reviewed with the rule set by the study team and were not independently adjudicated.

**Changes:** §2.2 (Rule construction, adjudication and provenance; L2 class matrix); Supplementary Text S10; Supplementary Tables S9 and S14; Figure 1.

### Reviewer 2, comment 2

> The definitions of low, medium, and high risk should be linked more explicitly to clinical significance and expected management.

**Response.** We added a main-text table that defines each grade operationally and links it to clinical significance and expected management.

High denotes a mechanism with potential for severe harm at plausible ophthalmic exposure, or a narrow-therapeutic-index victim drug with a substantial exposure change; the expected action is prescriber or pharmacist review, monitoring of the relevant parameter, and consideration of an alternative. Medium denotes a measurable but usually non-severe effect, or a severe mechanism at low exposure; the expected action is review and monitoring. Low denotes no mechanism expected to be clinically significant at ophthalmic exposure, or a wide-therapeutic-index mechanism at low exposure; no specific action is expected beyond usual care. Unassessed denotes no rule and no matrix cell; it is not evidence of safety and requires manual review. The table also states that grades are screening categories, not probabilities of harm.

**Changes:** §2.2 (Grade definitions and expected management); Table 6.

### Reviewer 2, comment 3

> The current framework is largely pairwise. The authors should clarify how patient-specific factors such as age, renal or hepatic function, QT risk, dose, CYP phenotype, and instillation technique are considered.

**Response.** We now state plainly that the system is pair-level and that these factors are not modifiers of the pair grade.

Three contextual patient-factor policies exist - elderly (65 years or older), renal impairment and polypharmacy - but they are returned as separate advisories, not applied to the grade; they are triggered by narrow-therapeutic-index systemic flags and do not use eGFR, genotype or age as numeric inputs. QT risk is represented only through `qt_prolonging` flags and the QT rules; CYP phenotype only through substrate/inhibitor flags. Hepatic function, dose, duration and instillation technique are not modelled at all. Supplementary Table S15 maps each factor to its representation, its effect on the output and the remaining gap. The Limitations state that the system is not a patient-level risk model and that integrating eGFR, genotype, QTc, dose, duration and instillation technique is future work.

**Changes:** §2.2 (Patient-specific factors); Supplementary Table S15; §4.4 (Patient-level factors); §4.5.

### Reviewer 2, comment 4

> The A-E evidence grading appears to combine source type with strength of evidence. The rationale for this hierarchy should be clarified.

**Response.** We agree that the previous wording conflated source type with strength of evidence. The A-E scale is now described as a **source tier**, not a strength-of-evidence grade.

A is a regulatory label, B a systematic review or meta-analysis, C an original study or case report, D in vitro, animal or pharmacokinetic first-principles evidence, and E class-level mechanism inference. The tiers describe provenance: a label statement (A) can be less direct than a systematic review (B) for a specific pair, and an E-tier mechanism can be biologically plausible but unverified. The tiers are not weights in the engine and do not enter the grade. Supplementary Table S16 records what each tier can and cannot support; Supplementary Text S1 reports the distribution (A = 53, B = 191, C = 215, D = 584, E = 264).

**Changes:** §2.1; Supplementary Table S16; Supplementary Text S1.

### Reviewer 2, comment 5

> The manuscript should better distinguish reduced systemic exposure from reduced clinical interaction risk, as this relationship may differ according to mechanism and therapeutic index.

**Response.** We added a dedicated Discussion subsection and a mechanism table.

The absorption tier models systemic exposure, not the probability of a clinical interaction. For reversible pharmacodynamic effects such as beta-blockade or prostaglandin inhibition, lower exposure usually means a smaller effect, but a potent agent or a narrow-therapeutic-index victim can still be clinically important. For pharmacokinetic interactions, risk depends on the fractional change in the victim drug's exposure, not on the ophthalmic agent's absolute exposure; a small degree of CYP inhibition can matter for warfarin, digoxin, tacrolimus or cyclosporine. For threshold or idiosyncratic reactions, such as sulfonamide hypersensitivity or fluoroquinolone tendon injury, exposure-response is not linear and low exposure does not guarantee absence of risk. Cumulative toxicity depends on duration, which the pair-level model does not represent.

The text now states that the 77.7% divergence is a difference in classification produced by the cascade, not evidence that the downgraded pairs are safe. Of the 1,502 downgrades, 161 are on the unassessed default path and are not attributable to the exposure model; among the 1,757 assessed pairs the share is 76.3%. The five high-absorption-tier downgrades are the clearest author-identified subset (three DDInter-high and two DDInter-medium), but 12 disagreements are on the unassessed default path, adding four DDInter-high pairs whose low grade is not evidence of safety. An independent review of the same 30 cases was more conservative: it agreed with the author class on 14/30 and reclassified 14 of the 21 author route-consistent cases as unsupported (R1 response, comment 5).

**Changes:** §4.3 (Exposure is not risk); Supplementary Table S17; §4.4.

### Reviewer 2, comment 6

> A comparison with at least one route-aware clinical interaction resource would help clarify the added value of OphDDI-CDS.

**Response.** We added two quantitative comparisons. The first is a route-aware DDInter filter (RA-DDInter). The second is a comparison with Lexicomp, a commercial route-aware resource, using ophthalmic-specific product entries where available.

RA-DDInter applies a single route-aware rule: if the ophthalmic agent's tier is low or lower, the grade is low; otherwise the DDInter severity is retained. On the 42 L1 cases for which DDInter has a severity record, raw DDInter agrees exactly on 17 of 42 (0.405), RA-DDInter on 21 of 42 (0.500) and the full cascade on 32 of 42 (0.762); high-risk sensitivity is 5 of 13 (0.385), 3 of 13 (0.231) and 9 of 13 (0.692). The route filter raises specificity by suppressing all low-tier pairs, but it also suppresses true high-risk pairs; the rules and matrix recover most of that sensitivity. Across the 1,933 pairs with a graded DDInter severity, RA-DDInter and the cascade agree on 1,489 (77.0%); the cascade is higher on 148 pairs and lower on 296.

We also queried Lexicomp on 11 November 2026 through the 2018 UpToDate interface (application version 1.1, OpenMed-provided) for the same 42 pairs. Each pair was queried by drug name only; the ophthalmic product entry was used whenever the interface exposed one, and the generic ingredient entry was used and flagged for the seven cases across three agents (apraclonidine, bromfenac, voriconazole) that had no ophthalmic-specific entry. No cascade grade or reference label was sent to the interface, and ratings were retrieved before the comparison was computed. The ophthalmic-specific entry was available for 35 cases. Lexicomp returned C for 15 pairs, B for one, X for one (voriconazole + ticagrelor, which the cascade grades low) and no interaction for 25. Its ophthalmic entry was lower than the systemic entry in all 21 of the 35 pairs with both entries, including 18 with no interaction at the ophthalmic entry but C/D/X at the systemic entry. Because the five-level scale is not severity-equivalent to our three-level grade, the three-level comparison is mapping-dependent: exact agreement was 17 of 42 with C mapped to medium and 18 of 42 with C mapped to high, and high-risk sensitivity was 0 of 13 and 8 of 13, respectively. Under a binary definition of any actionable interaction (C/D/X), Lexicomp flagged 16 of 42 pairs, capturing 16 of 32 reference non-low pairs (sensitivity 0.500) and none of the 10 reference-low pairs (specificity 1.000; exact 26 of 42, κ 0.323). The direction of the route-specific discordance is consistent with the exposure premise, but product-level entries may not capture systemic absorption from topical NSAIDs, so the absence of an interaction is not evidence of safety.

The comparison has three limits, which the manuscript states. RA-DDInter uses the same DDInter data and the same tier table, so it isolates the incremental value of the rules and matrix, not the validity of the tier model. The 42 reference labels are a subset of the frozen author-derived L1 reference set, not a separate adjudication, so agreement with Lexicomp measures alignment with our exposure model rather than clinical truth. And the accessible Lexicomp instance is the 2018 UpToDate interface, not a current licensed release; a comparison with a current release remains a future direction.

**Changes:** §3.9; Table 7; Supplementary Tables S18 and S18b; §4.4; §4.5.

### Reviewer 2, comment 7

> The intended clinical workflow should be described more clearly, including how low, medium, and high outputs are expected to influence management.

**Response.** We added a workflow figure and a stepwise description.

The intended use is a second-reader check at the point of prescribing or medication review (Figure 6). The user enters the ophthalmic agent and the systemic drug; the service checks registry coverage and returns an explicit error for an unknown agent. For covered pairs, the three layers run and the final grade, decision path, matched rule identifiers, source record and management category are returned. A high grade prompts prescriber or pharmacist review before starting, a medium grade prompts review and monitoring, a low grade requires no specific action beyond usual care, and an unassessed pair is referred for manual review rather than read as low. The workflow is proposed, not evaluated in a clinical setting; no outcome or prescribing data were collected.

**Changes:** §2.2 (Intended workflow); Figure 6; Table 6; §4.4.

## Response to the Reviewer's checklist

**(a) Figures and tables.** Figure 6 (workflow) and Tables 6 and 7 were added. The existing tables were rebuilt in the Reviewer 1 revision, and the new tables follow the same formatting rules. The visual layout was checked page by page.

**(b) Reference list.** The list was audited in the Reviewer 1 revision; four citation mismatches were corrected and three verified reviews of ocular pharmacokinetics were added. No new literature reference was required for the Reviewer 2 additions because they document the existing rule and matrix files; the Lexicomp database is identified by its 2018 UpToDate interface, application version and access date in §3.9 and Supplementary Table S18b, so the comparison is traceable without adding a numbered reference.

**(c) Statistical methods.** The Reviewer 2 comments did not require new inferential statistics. The route-aware comparisons are descriptive (agreement, sensitivity, specificity on a fixed 42-case subset). Because the Lexicomp five-level scale is not severity-equivalent to the three-level grade, we report the mapping, a C-to-high sensitivity analysis, and a binary "any actionable interaction" analysis rather than a single exact-agreement figure. The Reviewer 1 revision removed the unsupported PPV calculation and clarified the aggregation rules.

**(d) Statistician.** We agree with the reviewer that a statistician is not required for this revision; the analyses are descriptive or use standard exact tests, and the revision states that no power calculation was performed.

**(e) Replication.** The rule file, matrix file, rule-provenance audit and matrix-cell table are deposited; the workflow figure is drawn from the engine's decision paths. The new scripts are `scripts/build_r2_tables.py`, `scripts/draw_figure6_workflow.py` and `scripts/compare_lexicomp_route_aware.py`.

## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data and the figures identified the following issues; all were corrected in the same revision.

1. **The registry-scale denominator is 1,933 graded-severity pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. The 77.7% result applies to pairs with a graded severity; Section 2.3, Section 3.4 and the Limitations state this.

2. **The five unsupported downgradings are not the whole clinically critical set.** They are the clearest author-identified subset (three DDInter-high, two DDInter-medium); 12 disagreements are on the unassessed default path, adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080). The manuscript and Table S2 now say so; the Table S2 note states that all 12 default-path disagreements are not evidence of safety. The independent review was more conservative and classified 14 additional downgrades as unsupported (14/30 agreement; R1 response, comment 5).

3. **Figure 6 and the demo interface were aligned.** The previous interface screenshot displayed `Confidence 100%` and `0.2 s`, neither of which is defined in the manuscript. Figure 6 has been redrawn as a three-panel schematic reporting `assessment status = assessed`, the matched rule, the path `rule engine` and the recommendation, with no undefined confidence or runtime. The demo interface no longer renders the two undefined fields; it shows the assessment status instead.

4. **Table and example corrections.** Table 6's unassessed example is now timolol + warfarin (the previous sildenafil pair is an assessed matrix-none cell); Table 7's comparator is labelled "DDInter (no absorption correction)"; the S18b C-versus-D example is timolol ophthalmic C versus systemic D, replacing two examples that belonged to the none-versus-D/X group.

5. **Lexicomp reproducibility and citation.** The Lexicomp comparison is reproducible from `scripts/compare_lexicomp_route_aware.py` and the deposited aggregate results; `scripts/build_r2_tables.py` was corrected so that the regenerated Table 7 includes the Lexicomp cross-reference instead of the obsolete sentence that licensed route-aware databases were unavailable. The 2018 edition and the OpenMed-provided UpToDate interface are stated in Section 3.9 and Table S18b; because Lexicomp is a proprietary database accessed through a third-party interface, we cite the edition and access route rather than redistribute case-level ratings.

6. **The repository manifest was regenerated for the deposit layout.** After the final edits, `MANIFEST.sha256` was rebuilt; the previous manifest no longer matched `configs/rules.yaml`, the seed registries, the evidence base and several deposited reference files. Local verification requires the deposit checkout and CRLF-to-LF conversion, as stated in Data availability.

## Closing

We are grateful for the reviewer's clinical perspective. The revision is more explicit about how the rules and matrix were built, what the grades mean at the bedside, which patient factors are and are not represented, and where the exposure model stops short of clinical risk. We hope the manuscript is now suitable for publication as a proof-of-concept methodological study.
