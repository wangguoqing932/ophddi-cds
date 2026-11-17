# -*- coding: utf-8 -*-
"""Apply the Reviewer 1 revision, part 2: methods provenance/tiers and Results 3.3-3.6."""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path('outputs/paper/manuscript.en.md')
text = P.read_text(encoding='utf-8')


def replace_block(start: str, end: str, new: str) -> None:
    global text
    i = text.find(start)
    j = text.find(end, i + len(start)) if i >= 0 else -1
    if i < 0 or j < 0:
        sys.exit(f'MARKER MISS: {start[:70]!r} / {end[:70]!r}')
    text = text[:i] + new + text[j:]


PROVENANCE = """**Rule provenance.** Every rule carries a source record, but the record types are heterogeneous and support different claims. We audited all 40 rules on three questions: whether the cited source concerns the named ophthalmic agent, whether it supports the pair, and whether it supports the assigned severity and route (Supplementary Table S9). Two rules rest on direct ophthalmic pair evidence (additive beta-blockade with systemic beta-blockers; timolol with verapamil), five on contextual ophthalmic evidence, 23 on systemic-route class evidence extrapolated to the ophthalmic agent, and 10 on mechanism only, with no pair-level clinical source. Severity is directly supported for two rules, inferred for 28 and provisional for 10. Four citations that named an unrelated drug have been corrected: the digoxin rule cited a study of topical-plus-systemic beta-blockade, which does not address digoxin, and now carries only its DDInter pair record and is labelled class-extrapolated; the warfarin rule cited timolol; and two low-absorption antiplatelet/anticoagulant rules cited latanoprost, a prostaglandin analogue. Those two are relabelled as absorption priors rather than pair-level DDI evidence. "Citation-verified" in this paper therefore means what Table S9 records, not that every rule has a verified pair-specific source.

"""

TIERS = """**Absorption tiers.** Each agent carries one of six ordinal exposure bands. The bands are defined operationally as the expected systemic exposure after topical ocular administration relative to an oral therapeutic dose: high (at least 10%, or plasma concentrations within the systemic therapeutic range), medium (1-10%), low (below 1% but detectable), very low (below assay quantification), minimal (macromolecular intravitreal agents with serum concentrations far below systemic therapeutic exposure) and none (viscoelastics and tear substitutes with no expected systemic absorption). The registry contains 12 high, 20 medium, 61 low, 9 very-low, 7 minimal and 4 none. The evidence behind each row is given in Supplementary Table S5: 13 agents have a measured exposure value, 11 an explicit label statement, and 89 a class-level inference; every row carries a certainty label, and the 89 class-inferred rows are marked uncertain. We do not treat fractional bioavailability, plasma concentration and exposure relative to an oral dose as interchangeable: the band is an ordinal assignment, and the metric behind each row is recorded. The 13 registry-versus-curation-file discrepancies reported in the previous version have been resolved rather than deferred. Ten curation-file values were corrected to the registry assignment; three agents were re-tiered on measured evidence (dexamethasone and its two fixed combinations moved from high to medium because peak plasma dexamethasone after 0.1% four times daily is below 1 ng/mL). Combination products are assigned the highest tier of their components, and each component is listed separately (Supplementary Table S10). The L3 hard constraint tests low and very-low tiers; minimal and none are mapped to low in the matrix layer. Nine agents are not topically administered; they are reported separately in Section 3.4.

"""

R33 = """### 3.3 Agreement with the author-derived reference set (118 cases)

On this set the reference labels and the rules draw on the same literature, so agreement measures the internal consistency of an evidence-graded encoding rather than accuracy against an independent standard (Table 3, Figure 2; Supplementary Table S7). We use "exact agreement" rather than "accuracy" throughout.

Under the original frozen labels, `full_system` agreed exactly on 103 of 118 cases (0.873; Wilson 95% CI 0.801-0.921), with high-risk sensitivity 0.929 (26 of 28; CI 0.774-0.980), specificity 0.978 and kappa 0.806 (bootstrap CI 0.706-0.896), with zero variance across conditions. After the three post-lock label corrections the figures are 106 of 118 (0.898), sensitivity 0.964, specificity 0.989 and kappa 0.845; the corrected version is reported as a sensitivity analysis, not the primary result. On the 40 cases with no development exposure, agreement was 36 of 40 (0.900; CI 0.769-0.960), sensitivity 0.818 (9 of 11) and specificity 0.966; this is the subset closest to an independent test, and it is also reported under the corrected labels (39 of 40).

The baselines were weaker under the same frozen labels: `rule_context` 0.731 (SD 0.020), `pure_llm` 0.478 (0.026) and `naive_rag` 0.419 (0.017), with high-risk sensitivities 0.750, 0.779 and 0.764. Exact McNemar tests at condition 0 were significant against each baseline: discordant pairs in favour of the system were 52 to 3 versus `pure_llm` (p = 1.5 x 10^-12), 58 to 5 versus `naive_rag` (p = 1.7 x 10^-12) and 19 to 2 versus `rule_context` (p = 2.2 x 10^-4). The gradient held across all five temperature conditions. The 0.142 gap to the best baseline is the margin over a comparator that already receives the matched rules (Section 2.4), so it should not be read as the contribution of retrieval augmentation alone.

Per subset, the frozen blind cases reached 36 of 40, the mechanism subset 20 of 20 and the guideline subset 47 of 58. Decomposing the guideline subset as described in Section 2.3, the system agrees on 42 of the 47 cases whose label equals the cited rule's severity and on 5 of the 11 hand-overridden cases. The 0.873 headline is therefore a weighted average of rule fidelity (42/47), agreement with hand-adjudicated labels (5/11) and agreement on the 60 T1 and frozen cases (56/60). It should not be read as a single independent agreement estimate. No independently adjudicated test set exists; the 40-case subset is the only portion without development exposure, and it is too small to support a clinical performance claim.

"""

R34 = """### 3.4 Registry-scale divergence

This result does not depend on the reference labels, since both sides are pre-specified: DDInter supplies a systemic-route severity rating and the cascade an absorption-aware grade. Of the 1,933 pairs for which DDInter 2.0 provides a severity record, 1,470 (76.1%) were graded lower by the system. That includes 352 downgraded from high (34 to medium, 318 to low; 18.2% of all pairs) and 1,118 from medium to low. A further 133 (6.9%) were upgraded, so the two perspectives differ for 82.9% of pairs. Of all downgrades, 79.7% (1,171 of 1,470) were attributable to low systemic absorption. This is a difference in classification, not evidence that either perspective is wrong.

The decision paths are unevenly distributed. Of the 1,933 pairs, 536 (27.7%) were graded by a rule, 1,188 (61.5%) by the matrix, 166 (8.6%) by the G19 hard constraint, and 43 (2.2%) by the default path, which now returns `assessment_status = unassessed`; those 43 are not evidence of low risk. Excluding them, the assessed subset contains 1,890 pairs, of which 1,433 (75.8%) were downgraded. The 43 unassessed pairs are listed in Supplementary Table S11; they include 35 DDInter-medium and 2 DDInter-high pairs, so the default path is a coverage gap rather than a safety finding.

Restricting to the 104 topically administered agents leaves 1,930 pairs, of which 1,467 (76.0%) were downgraded and 350 fell from high; the three pairs involving the nine intravitreal, intraocular or surgical agents are reported separately in Supplementary Table S12. The divergence is therefore a property of topical ophthalmic prescribing, not of the non-topical entries.

Two caveats bound this measurement. It quantifies divergence, not error: the two perspectives rarely coincide for the topical route, but that does not make the database ratings wrong. And the tiers driving the downgrades are an ordinal exposure model with measured values for 13 agents, label statements for 11 and class inference for 89 (Section 2.2), so the measurement is a property of an explicitly stated model rather than an independent pharmacokinetic measurement.

"""

R35 = """### 3.5 Semi-independent DDInter audit (92 cases)

On the audit set `full_system` reached 0.674 exact agreement (62/92; Wilson CI 0.573-0.761) and kappa 0.428 against the applied absorption-corrected reference labels (specificity 0.955). Under the re-derived labels the figures are 0.652 (60/92; CI 0.551-0.742), kappa 0.415, specificity 0.952 and high-risk sensitivity 0.276 (8 of 29). Both sets are reported in full in Table 5 and Supplementary Table S2; the applied labels are the primary analysis and the re-derived labels are the pre-specified sensitivity analysis. Against uncorrected DDInter labels agreement was 0.370 (34/92). Restricting to the 62 cases kept at third-party DDInter severity gives 34 of 62 (0.548); of the 30 corrected cases the system agreed on 28 (93%). Baselines on the applied labels were `pure_llm` 0.630, `rule_context` 0.591 and `naive_rag` 0.535; under re-derived labels they were 0.630, 0.576 and 0.598. McNemar tests were significant versus `rule_context` (8 versus 1; p = 0.039) but not versus `naive_rag` (27 versus 17; p = 0.174) or `pure_llm` (18 versus 15; p = 0.728). The cascade's advantage lies in specificity and exact agreement, not sensitivity.

High-risk sensitivity was 0.320 under the applied labels (8 of 25; CI 0.172-0.516) and 0.276 under the re-derived labels (8 of 29). That this figure is low in absolute terms is the principal limitation. The 30 disagreements with the applied labels fall into three groups: 21 are downgrades of low- or medium-tier agents, consistent with the absorption model; 5 are downgrades of high-tier agents through matrix or rule paths that the absorption model does not justify (timolol with theophylline, timolol with epinephrine, scopolamine with topiramate, timolol with spironolactone, carteolol with diazepam); and 4 are over-grades (apraclonidine with midazolam, apraclonidine with loperamide, tacrolimus with ibuprofen, bromfenac with enalapril). The five unsupported downgrades are the clinically critical subset and are listed with their decision paths in Supplementary Table S2. These are disagreements with reference labels; without outcome data they are not counts of missed adverse events.

Flurbiprofen illustrates how the absorption model interacts with third-party labels. It is formulated at 0.03%, the lowest concentration of any ophthalmic NSAID in the registry, so correcting its tier moved its methotrexate pair and three related anticoagulant pairs further from the DDInter label rather than closer. That divergence is between a systemic-route label and a low-absorption agent, and for a screening tool this false-negative profile is the clinically critical number.

"""

R36 = """### 3.6 Second configuration (different model, token allowance and sampling)

The primary comparison used `deepseek-chat` with a 10-token cap. We also ran the three baselines in a second configuration (`glm-5.3-flash`, `max_tokens` 3000, temperature 0.0, majority vote over five repeated samples). The two configurations differ in model, token allowance and sampling simultaneously, so the comparison describes two settings; it does not isolate the effect of output budget or of reasoning.

Label agreement was higher in configuration 2: on the 118-case set `pure_llm` rose from 0.475 to 0.576 and `naive_rag` from 0.415 to 0.585, while `rule_context` was unchanged at 0.737. High-risk sensitivity fell sharply and specificity rose to approximately 1.000 (Table 3): sensitivity moved from 0.771/0.757/0.779 to 0.250/0.214/0.536, while the cascade held at 0.964 on the corrected labels used for this comparison. The mechanism is a shift in the predicted label distribution, not better discrimination. In configuration 2 `pure_llm` and `naive_rag` assigned high risk to 5.9% of cases and `rule_context` to 12.7%, where the reference labels contain 23.7%; on the audit set the three assigned 2.2%, 10.9% and 6.5% high, where the reference labels contain 27.2%. Because both sets are dominated by low and medium grades, this conservatism inflates exact agreement. The baselines identified 5 to 8, 4 to 9 and 14 to 15 of the 28 reference-high cases across repeats, or 7, 6 and 15 by majority vote, against 27 for the cascade. We therefore read the agreement increase as a property of configuration 2, not as evidence that reasoning improves ophthalmic DDI screening.

Two further results bear on the primary comparison. First, the ordering between retrieval methods reverses. Under the 10-token configuration `naive_rag` scored below `pure_llm`; in configuration 2 it scores at or above it on both sets (0.585 versus 0.576; 0.728 versus 0.609). The 10-token ordering is therefore a property of the constrained configuration. Second, on the audit set configuration-2 `naive_rag` reaches 0.728 exact agreement and 0.400 sensitivity, both above the cascade. That advantage is confined to cases whose own DDInter statement the retriever can reach. With those 26 excluded it falls to 43 of 66 (0.652), below the cascade's 47 of 66 (0.712), and its sensitivity falls from 9 of 10 to 1 of 15. Its sensitivity is also unstable across repeats (0.280 to 0.480), whereas the cascade returns the same grade every time. At temperature 0.0 the baselines still varied by 0.013 to 0.034 in exact agreement, which is why configuration 2 uses a majority vote.

**Retrieval overlap.** The 1,307-chunk corpus contains 500 DDInter severity statements, and the audit reference labels for the 62 third-party cases are the DDInter values. We therefore measured, before comparing methods, how often each method's top-3 passages contain the pair's own statement: 26 of 92 cases overall (19 of the 62 kept cases and 7 of the 30 corrected cases). `pure_llm` and `rule_context` have no DDInter-statement retrieval channel and zero overlap by construction; `naive_rag` has 26. Results with and without these 26 cases are reported for all methods in Table 5, not only for the affected method.

"""

# Methods blocks
replace_block("Citation coverage is narrower than", "**L2 class matrix.**", PROVENANCE)
replace_block("**Absorption tiers.**", "The evidence base was embedded", TIERS)

# Results blocks
replace_block("### 3.3 Agreement with", "### 3.4 Registry-scale divergence", R33)
replace_block("### 3.4 Registry-scale divergence", "### 3.5 Semi-independent DDInter audit", R34)
replace_block("### 3.5 Semi-independent DDInter audit", "### 3.6 Reasoning-model baselines", R35)
replace_block("### 3.6 Reasoning-model baselines", "### 3.7 Determinism", R36)

P.write_text(text, encoding='utf-8')
print('part 2 applied')
