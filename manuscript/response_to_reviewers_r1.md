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
