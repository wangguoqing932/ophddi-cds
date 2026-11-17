# -*- coding: utf-8 -*-
"""Apply the Reviewer 1 revision to outputs/paper/manuscript.en.md.

Structured, idempotent block replacements. Each entry is (start marker, end marker,
new text); the block from the start marker up to (but not including) the end marker
is replaced. Missing markers abort the run so nothing is silently half-applied.
"""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path('outputs/paper/manuscript.en.md')
text = P.read_text(encoding='utf-8')

ABSTRACT = """## Abstract

**Background.** Ophthalmic eye drops reach the systemic circulation, yet general-purpose drug-drug interaction (DDI) databases grade severity as though every drug were swallowed. Whether that assumption holds at registry scale, and how far it departs from the judgment of prescribing clinicians, is unknown. **Methods.** We built OphDDI-CDS, a deterministic cascade of 40 mechanism rules, an absorption-scaled class matrix and a hard constraint, covering 113 ophthalmic and 232 systemic agents. We compared its grades with systemic-route database severity across 1,933 registry-matched pairs, with three language-model baselines on 118 author-annotated cases, and with two clinicians on 12 cases. **Results.** Absorption-aware assessment graded 76.1% of the 1,933 pairs lower than the database, including 352 that fell from high risk, and low systemic absorption accounted for 79.7% of those downgrades. On the 118-case author-derived reference set, exact agreement was 0.873 under the original frozen labels (103/118; kappa 0.806) and 0.898 after three post-lock label corrections (106/118); on the 40 cases without development exposure it was 0.900 (36/40). The three baselines reached 0.419 to 0.731 under the same frozen labels. In a second configuration that also changed model and sampling, the baselines converged on a rarely-high-risk policy: agreement rose to 0.576 to 0.737 while high-risk sensitivity fell to 0.214 to 0.536, whereas the cascade held at 0.964 on the corrected labels. On a semi-independent 92-case DDInter audit the cascade reached 0.674 exact agreement but a high-risk sensitivity of only 0.320 (8 of 25) under the applied labels and 0.276 (8 of 29) under re-derived labels, its principal limitation; on the 62 cases whose labels do not depend on its own absorption assumption, agreement was 0.548 (34 of 62). One second-configuration baseline scored higher on the full audit set (0.728), an advantage confined to the 26 cases whose DDInter statement it can retrieve: with those excluded it falls to 0.652 (43 of 66) against 0.712 (47 of 66) for the cascade. Two clinicians agreed with each other on 11 of 12 cases (kappa 0.840) yet rated most cases below the assigned grades, a descriptive comparison rather than a validation. **Conclusions.** Database severity, evidence-graded rules and clinical intuition assign ophthalmic DDI risk differently, and none of the three is a ground truth. An absorption-first deterministic cascade makes those disagreements enumerable, traceable and auditable, but its false-negative profile requires prospective, outcome-linked calibration.

"""

BLOCKS = [
    # Abstract
    ("## Abstract\n", "## 1. Introduction", ABSTRACT),
]

for start, end, new in BLOCKS:
    i = text.find(start)
    j = text.find(end, i + len(start))
    if i < 0 or j < 0:
        sys.exit(f'MARKER MISS: {start!r} / {end!r}')
    text = text[:i] + new + text[j:]

REPLACEMENTS = [
    # §2.1 route scope
    ("Evaluation followed a four-phase protocol: rule consistency, development-phase validation, a semi-independent external audit against DDInter, and a two-expert grade review.",
     "Evaluation followed a four-phase protocol: rule consistency, development-phase validation, a semi-independent external audit against DDInter, and a two-expert grade review. The principal registry-scale analysis was repeated on the 104 topically administered agents; the nine intravitreal, intraocular and surgical agents are reported separately."),
    # §2.2 combination products
    ("and combination products are tiered by their dominant component.",
     "and combination products are tiered by their highest component tier, with each component's mechanism assessed separately (Supplementary Table S10)."),
    # §2.2 L2 default
    ("Pairs reaching neither a rule nor a defined cell fall through to the default-low path.",
     "Pairs reaching neither a rule nor a defined cell return low with `assessment_status = unassessed`; the grade is retained for continuity but is not evidence of safety (Section 3.4)."),
    # §2.3 frozen labels primary
    ("The labels and blind proposals were drafted without reference to system outputs, with one exception. On 31 July 2026, after the lock and before the questionnaire, B02 (high→medium), B12 (medium→high) and C17 (low→medium) were corrected to the engine's grades (Section 3.8, results both ways).",
     "The labels and blind proposals were drafted without reference to system outputs, with one exception. On 31 July 2026, after the lock and before the questionnaire, B02 (high→medium), B12 (medium→high) and C17 (low→medium) were corrected to the engine's grades. The primary analysis uses the labels as frozen, before those corrections; the corrected labels are reported as a sensitivity analysis (Section 3.3), and the 40-case blind subset, which has no overlap with the development set, is reported separately."),
    # §2.3 audit numbers
    ("Re-deriving the gold under the stated rule changes 10 of 92 labels, giving 60 of 92 (0.652) with sensitivity 8 of 29, against 62 of 92 (0.674) and 8 of 25 under the applied gold.",
     "Re-deriving the reference labels under the stated rule changes 10 of 92 labels, giving 60 of 92 (0.652) with sensitivity 8 of 29, against 62 of 92 (0.674) and 8 of 25 under the applied labels. Both sets are reported in full in Table 5."),
    # §2.4 comparator rename
    ("`lightrag` adds a knowledge-graph context block rendered by `PreciseKG.full_kg_context()`, which reads the registries and rule configuration rather than the vector index.",
     "`rule_context` (method id `lightrag` in the deposited code, retained for continuity) adds a knowledge-graph context block rendered by `PreciseKG.full_kg_context()`, which reads the registries and rule configuration rather than the vector index."),
    # §2.4 configuration language
    ("A second setting used `glm-5.3-flash` with `max_tokens` 3000, temperature 0.0 and a majority vote over five repeated samples. Because it changes model, budget and sampling together, it is reported as a second setting rather than as an isolated test of reasoning.",
     "Configuration 2 used `glm-5.3-flash` with `max_tokens` 3000, temperature 0.0 and a majority vote over five repeated samples. It differs from configuration 1 in model, token allowance and sampling simultaneously; comparisons between them therefore describe two configurations, not the effect of output budget or of reasoning."),
    # §2.5 descriptive caveat
    ("Ratings were collected on 3 August 2026 and transcribed on 8 August; expert 1's questionnaire is deposited as a scan and both sets as transcribed records.",
     "Ratings were collected on 3 August 2026 and transcribed on 8 August; expert 1's questionnaire is deposited as a scan and both sets as transcribed records. Two clinicians are a purposive panel, not a sample of clinical opinion, and the exercise is reported as descriptive."),
    # §2.6 scope caveat
    ("The system is a research-grade, mechanism-based second reader. It is not intended to replace clinical or pharmacy judgment, out-of-coverage medications are rejected with an explicit error, and it is not marketed as a medical device.",
     "The system is a research-grade, mechanism-based second reader. It is not intended to replace clinical or pharmacy judgment, out-of-coverage medications are rejected with an explicit error, and it is not marketed as a medical device. The model does not encode dose, duration, patient susceptibility beyond three patient-factor policies, or local ocular interactions; those remain clinical-judgment inputs. Pairs outside rule and matrix coverage are returned as unassessed rather than as low risk."),
    # §3.2 dev set
    ("Against the unadjusted systemic-route gold of the development set (200 cases) the system achieved 0.210 exact accuracy (sensitivity 0.069, specificity 0.895)",
     "Against the unadjusted systemic-route labels of the development set (200 cases) the system achieved 0.200 exact agreement (sensitivity 0.069, specificity 0.895)"),
    # §3.7 rename
    ("`lightrag` accuracy ranged from 0.712 to 0.771 (SD 0.020)",
     "`rule_context` accuracy ranged from 0.712 to 0.771 (SD 0.020)"),
    # §3.8 numbers and descriptive caveat
    ("Reporting both ways gives 39 of 40 and 107 of 118 under the corrected labels, and 36 of 40 and 104 of 118 under the pre-correction labels.",
     "None of the twelve pairs involves an agent whose tier or rule changed in this revision, so the engine grades shown to the experts are unchanged. Reporting both ways gives 39 of 40 and 106 of 118 under the corrected labels, and 36 of 40 and 103 of 118 under the frozen labels used in the primary analysis."),
    ("The exercise is not a validation: both grades were visible, one expert is a study-team member, the cases were constructed around the system's outputs, and the sample is purposive. Case-level ratings are in Supplementary Table S3. What it supports is a perspective gap between clinical prior and evidence-based grading, not an error rate.",
     "The exercise is not a validation: both grades were visible, one expert is a study-team member, the cases were constructed around the system's outputs, and the sample is purposive. Two clinicians cannot represent clinical opinion generally, and the design cannot separate a perspective gap from case-selection effects. Case-level ratings are in Supplementary Table S3. What it supports is that the two raters did not reproduce the assigned grades, not an error rate."),
]

missing = []
for old, new in REPLACEMENTS:
    if old not in text:
        missing.append(old[:90])
    else:
        text = text.replace(old, new, 1)

if missing:
    print('MISSING REPLACEMENTS:')
    for m in missing:
        print('  -', m)
    sys.exit(1)

P.write_text(text, encoding='utf-8')
print('applied', len(REPLACEMENTS), 'replacements + abstract')
