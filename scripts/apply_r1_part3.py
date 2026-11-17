# -*- coding: utf-8 -*-
"""Apply the Reviewer 1 revision, part 3: Discussion, Conclusions, Declarations."""
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


R41 = """### 4.1 Principal findings

Three perspectives on ophthalmic-systemic risk (systemic-route database severity, evidence-graded rules and prescribing clinicians) assign grades differently, and this study measures that difference on overlapping pair sets. Absorption-aware assessment graded 76.1% of the registry-matched pairs lower than the database and a further 6.9% higher, so the two differ for 82.9% of pairs. Evidence-graded rules and clinical judgment also diverged: the two ophthalmologists agreed closely with each other (kappa 0.840) yet rated most cases one tier below the assigned grades (Section 3.8). Because the panel was not independent, the cases were built around the system's outputs, and two clinicians cannot represent clinical opinion generally, this is a perspective comparison rather than a validation. The exercise cannot distinguish a genuine perspective gap from case-selection effects; it shows only that the two raters did not reproduce the assigned grades.

The quantitative results bound that claim rather than carry it. The cascade reached 0.873 exact agreement on the 118-case author-derived reference set under the frozen labels (103/118; 0.898 after three corrections), and 0.900 on the 40 cases without development exposure (36/40; CI 0.769-0.960). It outperformed three baselines (0.419-0.731) with significant McNemar tests. On the audit set and within the primary configuration it led on exact agreement (0.674 versus 0.535-0.630) and specificity (0.955). Its high-risk sensitivity was, however, low in absolute terms (0.320 applied, 0.276 re-derived), below `pure_llm` and `naive_rag` (0.848 each) though above `rule_context` (0.264), and its advantage over those two was not significant. In configuration 2 one baseline exceeded it. Because 47 of the 58 guideline labels are the cited rule's own severity, 0.873 is best read as internal consistency rather than independent agreement; the audit sensitivity bounds what the system can claim as a safety screen today.

"""

R42_FIRST = """Against general-purpose DDI databases, our system makes the ophthalmic absorption factor an explicit modelling component: a tier on every agent, an absorption-scaling step inside the matrix layer, and a hard constraint. The final grade is the maximum of the rule and matrix layers. That maximum is the honest limitation of the design. Because the rule layer is not uniformly gated, 202 pairs with a low-or-below tier receive medium (107) or high (95) grades through rules that require no absorption flag; all 95 high grades come from a single rule (`nsaid_antihypertensive_antagonism`). Within the 1,933 DDInter-matched pairs the corresponding figures are 115 and 68. Gating that rule would lower frozen-label agreement from 0.873 to 0.856 (101/118), and gating all four NSAID rules to 0.822 (97/118). We report the behaviour rather than re-engineer it to fit the reference labels; whether to gate these rules is a calibration decision for outcome-linked evidence, not agreement with an author-derived set.

"""

R43 = """### 4.3 Limitations

**Absorption-tier assignment.** The tiers are the most load-bearing variable. This revision resolves the 13 registry-versus-curation discrepancies and replaces the previous per-agent source column with a structured evidence table (Supplementary Table S5): 13 agents have a measured exposure value, 11 an explicit label statement and 89 a class-level inference marked uncertain. Dexamethasone and its two fixed combinations were re-tiered from high to medium on measured plasma concentrations below 1 ng/mL; this correction reduced frozen-label agreement by two cases and increased it by one, and we report the net change rather than retain a tier chosen to fit the labels. The remaining uncertainty is substantial: 89 of 113 tiers are class inferences, and the ordinal bands are not a substitute for measured exposure. Nine agents are not topical; the principal analysis is repeated on the 104 topical agents (Section 3.4).

**Unassessed pairs.** The default path returns low with `assessment_status = unassessed`; 43 of 1,933 registry-matched pairs (2.2%) follow it, including 35 DDInter-medium and 2 DDInter-high pairs. These are coverage gaps, not evidence of safety. The model does not encode dose, duration, patient susceptibility beyond three patient-factor policies, or local ocular interactions; those remain clinical inputs.

**Bounded clinical impact.** The scarcity of direct evidence admits two explanations: clinically detectable systemic effects may be uncommon, or publication and ascertainment bias may operate; the present data cannot distinguish them. If the true risk gradient clusters at the low end the system may over-grade, while audit sensitivity of 0.320 (0.276 re-derived) shows it can also under-grade. No outcome data are available, so predictive value for adverse events cannot be estimated. The 76.1% divergence is a property of the stated absorption model, not evidence that alerts were inappropriate or that prescribing would improve.

**Validation.** The L1 reference set is heterogeneous. Twenty of its 118 labels are study-team annotations, 47 of the 58 guideline labels are the cited rule's severity, and the remainder was author-annotated, so it is a literature-derived proxy rather than an independently adjudicated standard. Only the 40 frozen cases are procedurally independent, and three of their labels were corrected toward the engine's grades after the lock, so the subset is reported both ways (Section 3.8). In addition, 78 of 118 L1 cases overlap the development set with identical labels. No independently adjudicated test set exists; the two-expert review is the only human channel beyond annotation and cannot serve as an independent test. The 0.873 headline is therefore an agreement estimate against an author-derived reference set, not a clinical performance estimate.

"""

R44 = """### 4.4 Future directions

Four directions follow. **Independent adjudication:** a prospectively locked test set adjudicated by blinded reviewers, including clinical pharmacy expertise, is the next requirement; the present 40-case subset is too small. **Clinical calibration:** a larger expert panel or outcome-linked retrospective data could determine whether a one-tier offset applies to specific tiers or classes, with the audit false-negative pairs as first targets. **False-negative surveillance:** pharmacovigilance mining and prospective monitoring of high-absorption agents would test mechanism-derived rules against outcomes. **Coverage and scope:** expose the unassessed status in the interface, extend the registry, and transfer the class-matrix architecture to dermatologic, inhaled and intranasal domains.

"""

R5 = """## 5. Conclusions

We developed OphDDI-CDS, an absorption-first deterministic cascade for ophthalmic-systemic DDI screening, and used it to compare three ways of assigning risk. Against DDInter severity, absorption-aware assessment graded 76.1% of all 1,933 registry-matched pairs lower, with 79.7% of that shift attributable to low topical systemic absorption. The 13 registry-versus-curation-file tier discrepancies were resolved and the rules were audited; two rest on direct ophthalmic pair evidence and 10 on mechanism only. An exploratory grade review likewise found one-directional disagreement with the assigned grades, reported as a perspective gap rather than an error rate (Section 3.8). The cascade reached 0.873 exact agreement on the 118-case author-derived reference set under the frozen labels (103/118; kappa 0.806), 0.898 after three post-lock corrections, and 0.900 on the 40 cases without development exposure. On a semi-independent audit set it reached 0.674 exact agreement, falling to 0.548 on the subset free of its own absorption assumption, but a high-risk sensitivity of only 0.320 (8 of 25; 0.276 re-derived). That sensitivity, together with a reference set that is part study-team and part author annotation, bounds what the system can claim today. Ophthalmic DDI risk lacks a shared grading standard: database severity, evidence-graded rules and clinical prior disagree directionally in every sample studied, and evaluation here should measure that disagreement rather than assume any one is correct. Prospective, outcome-linked calibration is the next step.

"""

ETHICS = """### Ethics statement

Ethics approval and consent to participate are not applicable to this study. It used only publicly available secondary data (the DDInter severity tables, published drug labels, DrugBank records and the peer-reviewed literature). It involved no patients, no patient-level data, no human tissue or biological specimens, and no clinical intervention. Under the Declaration of Helsinki and the Chinese Measures for Ethical Review of Life Science and Medical Research Involving Humans, secondary analysis of published data does not constitute human-subjects research. The committee competent for this institution is the Ethics Committee of the First Affiliated Hospital of Xinjiang Medical University; the authors determined that no submission to it was required, and no formal determination was issued.

The only human involvement was an anonymous professional-opinion exercise: two ophthalmologists, both clinicians of the Department of Ophthalmology of the First Affiliated Hospital of Xinjiang Medical University, rated 12 hypothetical drug-pair vignettes constructed by the study team on 3 August 2026. The vignettes described no real patient, contained no patient data and no identifiable information, and the ratings are reported under pseudonymous case identifiers (R01-R12). Because the exercise collected no personal data and posed no intervention or risk to the participants, it does not constitute human-subjects research, and consent beyond agreeing to take part was not required; the completed questionnaires were returned anonymously to the study team. One of the two is a member of the corresponding author's research team. The pair is therefore not an independent external panel, and the exercise is reported as a descriptive perspective comparison rather than as independent validation.

The system is a research decision-support tool and is not intended to replace clinical judgment (Section 2.6).

"""

replace_block("### 4.1 Principal findings", "### 4.2 What we add", R41)
replace_block("Against general-purpose DDI databases", "Against LLM and retrieval-augmented approaches", R42_FIRST)
replace_block("### 4.3 Limitations", "### 4.4 Future directions", R43)
replace_block("### 4.4 Future directions", "## 5. Conclusions", R44)
replace_block("## 5. Conclusions", "## Keywords", R5)
replace_block("### Ethics statement", "### Consent statement", ETHICS)

# Data availability: reconcile archive statements
old = "A versioned release of the code matching this manuscript, with its own persistent identifier, will be deposited on acceptance."
new = "The version matching the submitted manuscript is archived at DOI 10.5281/zenodo.23439606; this revision will be deposited as a new version of the same record."
if old not in text:
    sys.exit('MARKER MISS: archive sentence')
text = text.replace(old, new, 1)

# Add the new audit files to the deposit list
old = "a per-agent absorption-tier table with a source column for each agent; the path-attribution audit reporting which layer produced each grade;"
new = ("a per-agent absorption-tier table with formulation, exposure evidence, source and certainty "
       "(`data/curation/absorption_tier_evidence.csv`); the rule-provenance audit "
       "(`data/curation/rule_provenance_audit.csv`); the revision statistics "
       "(`outputs/recomputed/revision_r1_stats.json`); the path-attribution audit reporting which layer "
       "produced each grade and which pairs are unassessed;")
if old not in text:
    sys.exit('MARKER MISS: deposit list')
text = text.replace(old, new, 1)

P.write_text(text, encoding='utf-8')
print('part 3 applied')
