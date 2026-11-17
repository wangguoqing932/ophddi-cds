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
