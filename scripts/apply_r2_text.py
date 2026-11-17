# -*- coding: utf-8 -*-
"""Apply the Reviewer 2 revision to the manuscript."""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path('outputs/paper/manuscript.en.md')
text = P.read_text(encoding='utf-8')


def rep(old: str, new: str) -> None:
    global text
    if old not in text:
        sys.exit(f'MISS: {old[:90]}')
    text = text.replace(old, new, 1)


# R2-4: source tiers, not strength of evidence
rep(
    "All 1,307 evidence chunks were filtered to approved release and graded by evidence level: A regulatory label, B meta-analysis or systematic review, C original study, D in vitro, animal or pharmacokinetic first principles, E class-level mechanism inference. The distribution is A = 53, B = 191, C = 215, D = 584, E = 264 (Supplementary Text S1).",
    "All 1,307 evidence chunks were filtered to approved release and assigned a **source tier**: A regulatory label, B meta-analysis or systematic review, C original study, D in vitro, animal or pharmacokinetic first principles, E class-level mechanism inference. The tiers describe provenance, not strength of evidence: a label statement (A) can be less direct than a systematic review (B) for a specific pair, and an E-tier mechanism can be biologically plausible but unverified. The tiers are not weights in the engine. The distribution is A = 53, B = 191, C = 215, D = 584, E = 264 (Supplementary Text S1; definitions in Supplementary Table S16).",
)

# R2-1: rule construction and severity adjudication
rep(
    "Rules are evaluated independently; the only cross-layer composition is the final maximum of the two layers, and combination products are tiered by their highest component tier, with each component's mechanism assessed separately (Supplementary Table S10).",
    "Rules are evaluated independently; the only cross-layer composition is the final maximum of the two layers, and combination products are tiered by their highest component tier, with each component's mechanism assessed separately (Supplementary Table S10).\n\n"
    "**Rule construction and severity adjudication.** Candidate rules were generated from three sources: DDInter 2.0 pairs that link an ophthalmic agent to a systemic drug class, ophthalmic product labels (warnings and drug-interaction sections), and published case reports or reviews. Each candidate was encoded as an entity-flag predicate with match-all or match-any semantics. Severity was assigned in a fixed order: the DDInter level where the pair was recorded; otherwise the label's warning category; otherwise the clinical consequence expected from the mechanism and the therapeutic index of the systemic drug. The rule inventory was reviewed by the study team and the two clinician authors; disagreements were resolved by consensus. There was no formal Delphi panel, blinded adjudication or independent clinical committee. Every rule carries its rationale, citations and an evidence-policy record, and the audit in Supplementary Table S9 records whether the severity is directly supported, inferred or provisional. Of the 40 rules, 2 are supported by direct ophthalmic pair evidence, 5 by contextual ophthalmic evidence, 23 by systemic-route class evidence and 10 by mechanism only. The only post-lock severity change was the dexamethasone CYP3A4 rule, downgraded from medium to low in this revision after the measured exposure was found to be below 1 ng/mL.",
)

# R2-1: matrix construction
rep(
    "Pairs reaching neither a rule nor a defined cell return low with `assessment_status = unassessed`; the grade is retained for continuity but is not evidence of safety (Section 3.4).",
    "Pairs reaching neither a rule nor a defined cell return low with `assessment_status = unassessed`; the grade is retained for continuity but is not evidence of safety (Section 3.4).\n\n"
    "**Matrix construction.** The row keys are ophthalmic classes (21) and the column keys systemic classes (40 declared, 34 used). A cell was defined when at least one source supported a class-level interaction; 104 cells were defined, of which 83 are actionable and 21 are explicitly marked \"none\" (no established interaction). Each cell records a level, a mechanism, one-line advice and an evidence type: a specific rule, a class extrapolation, a textbook statement, expert consensus, or a pharmacological inference. Supplementary Table S14 lists all 104 cells. Four upgrade rules apply only when a class match is combined with a high-absorption or selectivity flag; the absorption-scaling step then forces low, very-low, minimal and none tiers to low on the matrix branch. Cell levels were reviewed with the rule set by the study team; they were not independently adjudicated.",
)

# R2-2: grade definitions
rep(
    "**L3 hard constraint.** Low or very-low absorption with no rule hit and no matrix signal yields low risk (G19). Unknown medications are not silently classified: the engine returns an explicit unknown-drug path and the service raises an error, so out-of-coverage pairs are never assigned a grade by default.",
    "**L3 hard constraint.** Low or very-low absorption with no rule hit and no matrix signal yields low risk (G19). Unknown medications are not silently classified: the engine returns an explicit unknown-drug path and the service raises an error, so out-of-coverage pairs are never assigned a grade by default.\n\n"
    "**Grade definitions and expected management.** The three grades are screening categories, not probabilities. High denotes a mechanism with potential for severe harm at plausible ophthalmic exposure, or a narrow-therapeutic-index victim drug with a substantial exposure change; the expected action is prescriber or pharmacist review, monitoring of the relevant parameter, and consideration of an alternative. Medium denotes a measurable but usually non-severe effect, or a severe mechanism at low exposure; the expected action is review and monitoring. Low denotes no mechanism expected to be clinically significant at ophthalmic exposure, or a wide-therapeutic-index mechanism at low exposure; no specific action is expected beyond usual care. Unassessed denotes no rule and no matrix cell; it is not evidence of safety and requires manual review. Table 6 gives the operational definitions, clinical significance, expected management and an illustrative pair for each category.",
)

# R2-3 + R2-7: patient factors and workflow
rep(
    "Nine agents are not topically administered; they are reported separately in Section 3.4.",
    "Nine agents are not topically administered; they are reported separately in Section 3.4.\n\n"
    "**Patient-specific factors.** The system is pair-level. Age, renal function, hepatic function, QT risk, dose, duration, CYP phenotype and instillation technique are not modifiers of the pair grade. Three contextual patient-factor policies exist - elderly (65 years or older), renal impairment and polypharmacy - but they are returned as separate advisories, not applied to the grade; they are triggered by narrow-therapeutic-index systemic flags and do not use eGFR, genotype or age as numeric inputs. QT risk is represented only through `qt_prolonging` flags and the QT rules; CYP phenotype only through substrate/inhibitor flags; dose, duration and instillation technique are not modelled at all. Supplementary Table S15 maps each factor to its representation, its effect on the output and the remaining gap.\n\n"
    "**Intended workflow.** The intended use is a second-reader check at the point of prescribing or medication review (Figure 6). The user enters the ophthalmic agent and the systemic drug; the service checks registry coverage and returns an explicit error for an unknown agent. For covered pairs, the three layers run and the final grade, decision path, matched rule identifiers, source record and management category are returned. A high grade prompts prescriber or pharmacist review before starting, a medium grade prompts review and monitoring, a low grade requires no specific action beyond usual care, and an unassessed pair is referred for manual review rather than read as low. The workflow is proposed, not evaluated in a clinical setting; no outcome or prescribing data were collected.",
)

# R2-6: route-aware comparison
rep(
    "## 4. Discussion",
    "### 3.9 Comparison with a route-aware DDInter filter\n\n"
    "To separate the contribution of the rules and matrix from a blanket route correction, we constructed a route-aware DDInter filter (RA-DDInter): if the ophthalmic agent's tier is low or lower, the grade is low; otherwise the DDInter severity is retained. RA-DDInter uses the same tier table as OphDDI-CDS and therefore is not an independent exposure model; it is the simplest route-aware resource that can be built from DDInter.\n\n"
    "On the 42 L1 cases for which DDInter has a severity record, raw DDInter agrees exactly on 17 of 42 (0.405), RA-DDInter on 21 of 42 (0.500) and the full cascade on 34 of 42 (0.810); high-risk sensitivity is 5 of 13 (0.385), 3 of 13 (0.231) and 11 of 13 (0.846), and specificity 17 of 29 (0.586), 28 of 29 (0.966) and 29 of 29 (1.000) (Table 7). The route filter raises specificity by suppressing all low-tier pairs, but it also suppresses true high-risk pairs; the rules and matrix recover most of that sensitivity. Across all 1,933 registry-matched pairs, RA-DDInter and the cascade agree on 1,457 (75.4%); the cascade is higher on 180 pairs (rules or matrix upgrades) and lower on 296 (mostly low-tier pairs forced to low by the matrix scaling).\n\n"
    "The comparison has two limits. RA-DDInter is constructed from the same DDInter data and the same tier table, so it isolates the incremental value of the rules and matrix, not the validity of the tier model. And licensed route-aware clinical databases (Lexicomp, Micromedex, Stockley's) were not available to us for a systematic comparison; the 42-case subset is a proof of concept, not a benchmark against a commercial resource.\n\n"
    "## 4. Discussion",
)

# R2-5: exposure is not risk; renumber limitations/future
rep(
    "### 4.3 Limitations",
    "### 4.3 Exposure is not risk\n\n"
    "The absorption tier models systemic exposure; it does not model the probability of a clinical interaction. The relationship between the two depends on the mechanism and the therapeutic index (Supplementary Table S17). For reversible pharmacodynamic effects such as beta-blockade or prostaglandin inhibition, lower exposure usually means a smaller effect, but a potent agent or a narrow-therapeutic-index victim can still be clinically important. For pharmacokinetic interactions, risk depends on the fractional change in the victim drug's exposure, not on the ophthalmic agent's absolute exposure; a small degree of CYP inhibition can matter for warfarin, digoxin, tacrolimus or cyclosporine. For threshold or idiosyncratic reactions, such as sulfonamide hypersensitivity or fluoroquinolone tendon injury, exposure-response is not linear and low exposure does not guarantee absence of risk. Cumulative toxicity, such as corticosteroid-induced ocular hypertension or adrenal suppression, depends on duration, which the pair-level model does not represent.\n\n"
    "This distinction bounds the 76.1% divergence: it is a difference in classification produced by the exposure model, not evidence that the downgraded pairs are safe or that alerts were inappropriate. It also explains the audit's false-negative profile: the five unsupported downgrades are high-tier agents whose risk is not absorption-limited, and the low-tier downgrades are plausible only for mechanisms whose effect scales with exposure. The grade is a screening flag; the management category in Table 6 is the clinical action, and it remains conditional on dose, duration and patient factors.\n\n"
    "### 4.4 Limitations",
)
rep("### 4.4 Future directions", "### 4.5 Future directions")

# R2 limitations additions
rep(
    "**Bounded clinical impact.**",
    "**Rule and matrix construction.** The rule set and the class-matrix levels were built and reviewed by the study team, with consensus adjudication and no formal Delphi panel, blinded review or independent clinical committee. The support level of each rule is now recorded (Supplementary Table S9), and all matrix cells are listed (Supplementary Table S14), but the severity assignments remain expert judgements. The rule layer is also not uniformly gated on absorption, which is why 202 pairs with a low-or-below tier receive medium or high grades through rules (Section 4.2).\n\n"
    "**Patient-level factors.** The system is pair-level. Age, renal and hepatic function, QT risk, dose, duration, CYP phenotype and instillation technique are not modifiers of the grade; three contextual policies are returned as separate advisories (Supplementary Table S15). The workflow in Figure 6 is proposed, not evaluated in a clinical setting.\n\n"
    "**Bounded clinical impact.**",
)

# R2 future additions
rep(
    "**Coverage and scope:** expose the unassessed status in the interface, extend the registry, and transfer the class-matrix architecture to dermatologic, inhaled and intranasal domains.",
    "**Coverage and scope:** expose the unassessed status in the interface, extend the registry, and transfer the class-matrix architecture to dermatologic, inhaled and intranasal domains. **Route-aware comparison:** a formal comparison with licensed route-aware databases (Lexicomp, Micromedex, Stockley's) and a prospective evaluation of the workflow with prescribing and outcome data are the next steps; the present RA-DDInter comparison is a proof of concept. **Patient-level model:** integrating eGFR, genotype, QTc, dose, duration and instillation technique would move the system from pair-level screening to patient-level risk estimation.",
)

P.write_text(text, encoding='utf-8')
print('R2 text applied')
