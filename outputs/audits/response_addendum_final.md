# Final response addenda (post-audit, all fixes verified)

> **2026-11-14 update:** R1-5 independent review completed (one non-author ophthalmologist; 14/30 exact, 14/28 κ0.271; 14 author route-consistent cases reclassified as unsupported). The five-case wording below is now explicitly the **author-identified** subset; the independent count is 19 unsupported. See §3.5, Table 5 and S2.

## R1 — insert before `## Closing`

## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data, the development log and the reference list identified the following issues; all were corrected in the same revision.

1. **The 20 B-only cases are not development-free.** The internal development log shows that B02 and B12 were corrected after engine review, B18 and B19 informed matrix design, and other B cases informed rule-gap diagnosis. Section 2.3 now states that neither half of the 40-case set is an independent test and that the 20/20 corrected figure is partly tautological because both B02 and B12 were moved toward the engine's grade. The Table 3 note that had said B01–B20 were never used in development has been removed. The 18/20 frozen and 20/20 corrected values are unchanged and are reported as descriptive only.

2. **The registry-scale denominator is 1,933 graded-severity pairs, not all matched pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. Section 2.3, Section 3.4 and the Limitations now state this, and the 77.7% result is described as applying to pairs with a graded severity; its generalization to `Unknown` pairs is unknown. A denominator audit (`scripts/audit_ddinter_denominator.py`; `outputs/audits/ddinter_denominator_audit.json`) regenerates the 4,546 / 2,613 / 1,933 counts.

3. **The 80.3% figure is a composition statistic, not a causal decomposition.** Of the 1,502 downgrades, 1,206 involved low-tier ophthalmic agents; of these, 698 were assigned low by G19 and 72 by absorption-forced matrix scaling, while 436 were decided by a rule or matrix cell whose level does not depend on the tier. The text now uses "involved" and labels the figure as a composition statistic.

4. **The five unsupported downgradings are the clearest unsupported subset, not the whole clinically critical set.** They comprise three DDInter-high and two DDInter-medium pairs. Twelve disagreements are on the unassessed default path (10 route-consistent, 2 unsupported), adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080) whose low grade is not evidence of safety. The earlier sentence in this response letter that called the five the "clinically critical subset" has been corrected; the Table S2 note now states that all 12 default-path disagreements, including these four, are not evidence of safety.

5. **The timolol evidence line was overstated.** The cited studies support approximately 78% systemic bioavailability relative to intravenous timolol in one crossover study, not a 50–78% range or a comparison with oral doses; Table S5b now states this. The timolol tier remains high because the reported exposure is well above 10% of an oral therapeutic dose.

6. **The internal development metrics were corrected.** The previously reported sensitivity of 0.353 was 6/17 from an old case-ID mapping, not the current engine's 15/17 = 0.882; the 0.895 specificity came from the ungated analysis and had been mixed with the gated 0.240 agreement. The corrected gated values are sensitivity 0.882 (15/17), specificity 0.984, and 0.240 / 0.069 / 0.977 on the 200-case development set. The only two high-label cases lost to the gate are G137 and G138.

7. **The expert summary was rebuilt from the deposited records.** Inter-rater kappa is 0.840 (not 0.846); R03 is low/low (not medium); the grade displayed for R10 and R11 was medium; expert-versus-displayed agreement is 2/12 and 1/12 (not 0.417 and 0.333). The manuscript and Table S3 now use the transcribed per-case record; the exercise remains descriptive and non-independent.

8. **Table 4 and Table S8 now show both label distributions.** The tables previously showed only the corrected distribution (28 high / 51 medium / 39 low) without saying so, while the primary analysis uses the frozen labels (28 / 50 / 40). Both distributions are now labelled, and Section 2.3 no longer quotes an unlabelled distribution.

9. **Configuration 2 prompt comparability is now stated.** Configuration 2 `rule_context` used the pre-correction context block, and `pure_llm` and `naive_rag` were not re-run after the tier correction, whereas configuration 1 `rule_context` was re-run. The baseline comparison therefore mixes a corrected `rule_context` row with uncorrected rows and is not a clean test of retrieval augmentation (Section 2.4, Section 3.6, Figure 2 legend).

10. **Reference metadata were re-checked.** [45] is the 2nd edition (Routledge); missing titles, volume or page numbers in [13–16,29] were supplied; the duplicate "Sacchi, M." in [17] was removed (PubMed lists a single Sacchi). Reference [37] remains "3, 333–389": the Crossref/Zotero record "4(1–2), 1–174" is a publisher metadata collision with 10.1561/1500000013 and is not the correct pagination (Semantic Scholar/DBLP give 3:333–389). Of the 45 DOIs, 44 are Crossref-verified, the arXiv DOI [36] resolves through DataCite, and all 45 entries are present in the Zotero audit library. The compiled PDF and DOCX have been rebuilt so that they match the source.

## R2 — insert before `## Closing`

## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data and the figures identified the following issues; all were corrected in the same revision.

1. **The registry-scale denominator is 1,933 graded-severity pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. The 77.7% result applies to pairs with a graded severity; Section 2.3, Section 3.4 and the Limitations state this.

2. **The five unsupported downgradings are not the whole clinically critical set.** They are the clearest unsupported subset (three DDInter-high, two DDInter-medium); 12 disagreements are on the unassessed default path, adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080). The manuscript and Table S2 now say so; the Table S2 note states that all 12 default-path disagreements are not evidence of safety.

3. **Figure 6 and the demo interface were aligned.** The previous interface screenshot displayed `Confidence 100%` and `0.2 s`, neither of which is defined in the manuscript. Figure 6 has been redrawn as a three-panel schematic reporting `assessment status = assessed`, the matched rule, the path `rule engine` and the recommendation, with no undefined confidence or runtime. The demo interface no longer renders the two undefined fields; it shows the assessment status instead.

4. **Table and example corrections.** Table 6's unassessed example is now timolol + warfarin (the previous sildenafil pair is an assessed matrix-none cell); Table 7's comparator is labelled "DDInter (no absorption correction)"; the S18b C-versus-D example is timolol ophthalmic C versus systemic D, replacing two examples that belonged to the none-versus-D/X group.

5. **Lexicomp reproducibility and citation.** The Lexicomp comparison is reproducible from `scripts/compare_lexicomp_route_aware.py` and the deposited aggregate results; `scripts/build_r2_tables.py` was corrected so that the regenerated Table 7 includes the Lexicomp cross-reference instead of the obsolete sentence that licensed route-aware databases were unavailable. The 2018 edition and the OpenMed-provided UpToDate interface are stated in Section 3.9 and Table S18b; because Lexicomp is a proprietary database accessed through a third-party interface, we cite the edition and access route rather than redistribute case-level ratings.

6. **The repository manifest was regenerated for the deposit layout.** After the final edits, `MANIFEST.sha256` was rebuilt; the previous manifest no longer matched `configs/rules.yaml`, the seed registries, the evidence base and several deposited reference files. Local verification requires the deposit checkout and CRLF-to-LF conversion, as stated in Data availability.
