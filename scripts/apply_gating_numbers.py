# -*- coding: utf-8 -*-
"""Apply the post-gating number updates to the manuscript."""
from __future__ import annotations

import pathlib
import sys

P = pathlib.Path('outputs/paper/manuscript.en.md')
t = P.read_text(encoding='utf-8')

REPS = [
    ("Absorption-aware assessment graded 76.1% of the 1,933 pairs lower than the database, including 352 that fell from high risk, and low systemic absorption explained 79.9% of those downgrades.",
     "Absorption-aware assessment graded 77.7% of the 1,933 pairs lower than the database, including 352 that fell from high risk, and low systemic absorption explained 80.3% of those downgrades."),
    ("exact agreement was 0.873 under the original frozen labels (103/118; kappa 0.806) and 0.898 after three post-lock label corrections (106/118)",
     "exact agreement was 0.856 under the original frozen labels (101/118; kappa 0.779) and 0.881 after three post-lock label corrections (104/118)"),
    ("the cascade held at 0.964.", "the cascade held at 0.893."),
    ("On the internal validation set (78 cases) sensitivity was 1.000 and specificity 0.984, reported as a development gate because 78 of 118 L1 cases overlap it with identical labels. Against the unadjusted systemic-route labels of the development set (200 cases) the system achieved 0.200 exact agreement",
     "On the internal validation set (78 cases) sensitivity was 0.353 and specificity 1.000 under the gated primary analysis; under the ungated sensitivity analysis it was 1.000 and 0.984. The set is a development gate because 78 of 118 L1 cases overlap it with identical labels, and the drop under the gate is expected because many of its high labels were derived from the gated rule. Against the unadjusted systemic-route labels of the development set (200 cases) the system achieved 0.240 exact agreement"),
    ("Under the original frozen labels, `full_system` agreed exactly on 103 of 118 cases (0.873; Wilson 95% CI 0.801-0.921), with high-risk sensitivity 0.929 (26 of 28; CI 0.774-0.980), specificity 0.978 and kappa 0.806 (bootstrap CI 0.706-0.896), with zero variance across conditions. After the three post-lock label corrections the figures are 106 of 118 (0.898), sensitivity 0.964, specificity 0.989 and kappa 0.845;",
     "Under the original frozen labels, `full_system` agreed exactly on 101 of 118 cases (0.856; Wilson 95% CI 0.781-0.908), with high-risk sensitivity 0.857 (24 of 28; CI 0.685-0.950), specificity 0.978 and kappa 0.779 (bootstrap CI 0.676-0.871), with zero variance across conditions. After the three post-lock label corrections the figures are 104 of 118 (0.881), sensitivity 0.893, specificity 0.989 and kappa 0.818;"),
    ("discordant pairs in favour of the system were 52 to 3 versus `pure_llm` (p = 1.5 x 10^-12), 58 to 5 versus `naive_rag` (p = 1.7 x 10^-12) and 19 to 2 versus `rule_context` (p = 2.2 x 10^-4).",
     "discordant pairs in favour of the system were 48 to 2 versus `pure_llm` (p = 2.3 x 10^-12), 54 to 4 versus `naive_rag` (p = 3.2 x 10^-12) and 20 to 6 versus `rule_context` (p = 0.0094)."),
    ("The 0.142 gap to the best baseline", "The 0.125 gap to the best baseline"),
    ("the guideline subset 47 of 58. Decomposing the guideline subset as described in Section 2.3, the system agrees on 42 of the 47 cases whose label equals the cited rule's severity and on 5 of the 11 hand-overridden cases. The 0.873 headline is therefore a weighted average of rule fidelity (42/47)",
     "the guideline subset 45 of 58. Decomposing the guideline subset as described in Section 2.3, the system agrees on 40 of the 47 cases whose label equals the cited rule's severity and on 5 of the 11 hand-overridden cases. The 0.856 headline is therefore a weighted average of rule fidelity (40/47)"),
    ("Of the 1,933 pairs for which DDInter 2.0 provides a severity record, 1,470 (76.1%) were graded lower by the system. That includes 352 downgraded from high (34 to medium, 318 to low; 18.2% of all pairs) and 1,118 from medium to low. A further 133 (6.9%) were upgraded, so the two perspectives differ for 82.9% of pairs. Of all downgrades, 79.9% (1,174 of 1,470) were attributable to low systemic absorption.",
     "Of the 1,933 pairs for which DDInter 2.0 provides a severity record, 1,502 (77.7%) were graded lower by the system. That includes 352 downgraded from high (34 to medium, 318 to low; 18.2% of all pairs) and 1,150 from medium to low. A further 65 (3.4%) were upgraded, so the two perspectives differ for 81.1% of pairs. Of all downgrades, 80.3% (1,206 of 1,502) were attributable to low systemic absorption."),
    ("Of the 1,933 pairs, 536 (27.7%) were graded by a rule, 1,188 (61.5%) by the matrix, 166 (8.6%) by the G19 hard constraint, and 43 (2.2%) by the default path",
     "Of the 1,933 pairs, 504 (26.1%) were graded by a rule, 1,220 (63.1%) by the matrix, 166 (8.6%) by the G19 hard constraint, and 43 (2.2%) by the default path"),
    ("the assessed subset contains 1,890 pairs, of which 1,433 (75.8%) were downgraded.",
     "the assessed subset contains 1,890 pairs, of which 1,465 (77.5%) were downgraded."),
    ("leaves 1,930 pairs, of which 1,467 (76.0%) were downgraded and 350 fell from high;",
     "leaves 1,930 pairs, of which 1,499 (77.7%) were downgraded and 350 fell from high;"),
    ("and kappa 0.428 against the applied absorption-corrected reference labels (specificity 0.955). Under the re-derived labels the figures are 0.652 (60/92; CI 0.551-0.742), kappa 0.415, specificity 0.952 and high-risk sensitivity 0.276 (8 of 29).",
     "and kappa 0.428 against the applied absorption-corrected reference labels (specificity 0.970). Under the re-derived labels the figures are 0.663 (61/92; CI 0.562-0.751), kappa 0.434, specificity 0.968 and high-risk sensitivity 0.276 (8 of 29)."),
    ("Against uncorrected DDInter labels agreement was 0.370 (34/92).",
     "Against uncorrected DDInter labels agreement was 0.380 (35/92)."),
    ("while the cascade held at 0.964 on the corrected labels used for this comparison.",
     "while the cascade held at 0.893 on the corrected labels used for this comparison."),
    ("or 7, 6 and 15 by majority vote, against 27 for the cascade.",
     "or 7, 6 and 15 by majority vote, against 25 for the cascade."),
    ("the full cascade on 34 of 42 (0.810); high-risk sensitivity is 5 of 13 (0.385), 3 of 13 (0.231) and 11 of 13 (84.6%)",
     "the full cascade on 32 of 42 (0.762); high-risk sensitivity is 5 of 13 (0.385), 3 of 13 (0.231) and 9 of 13 (69.2%)"),
    ("RA-DDInter and the cascade agree on 1,457 (75.4%); the cascade is higher on 180 pairs",
     "RA-DDInter and the cascade agree on 1,489 (77.0%); the cascade is higher on 148 pairs"),
    ("Absorption-aware assessment graded 76.1% of the registry-matched pairs lower than the database and a further 6.9% higher, so the two differ for 82.9% of pairs.",
     "Absorption-aware assessment graded 77.7% of the registry-matched pairs lower than the database and a further 3.4% higher, so the two differ for 81.1% of pairs."),
    ("The cascade reached 0.873 exact agreement on the 118-case author-derived reference set under the frozen labels (103/118; 0.898 after three corrections)",
     "The cascade reached 0.856 exact agreement on the 118-case author-derived reference set under the frozen labels (101/118; 0.881 after three corrections)"),
    ("and specificity (0.955). Its high-risk sensitivity",
     "and specificity (0.970). Its high-risk sensitivity"),
    ("Because 47 of the 58 guideline labels are the cited rule's own severity, 0.873 is best read as internal consistency",
     "Because 47 of the 58 guideline labels are the cited rule's own severity, 0.856 is best read as internal consistency"),
    ("The rule layer is also not uniformly gated on absorption, which is why 202 pairs with a low-or-below tier receive medium or high grades through rules (Section 4.2).",
     "The rule layer is gated on absorption for the high-severity NSAID-antihypertensive rule, but 157 low-tier pairs still receive medium grades through other rules (Section 4.2)."),
    ("The 0.873 headline is therefore an agreement estimate",
     "The 0.856 headline is therefore an agreement estimate"),
    ("graded 76.1% of all 1,933 registry-matched pairs lower, with 79.9% of that shift",
     "graded 77.7% of all 1,933 registry-matched pairs lower, with 80.3% of that shift"),
    ("The cascade reached 0.873 exact agreement on the 118-case author-derived reference set under the frozen labels (103/118; kappa 0.806), 0.898 after three post-lock corrections",
     "The cascade reached 0.856 exact agreement on the 118-case author-derived reference set under the frozen labels (101/118; kappa 0.779), 0.881 after three post-lock corrections"),
]

miss = [a[:80] for a, _ in REPS if a not in t]
if miss:
    print('MISS')
    for m in miss:
        print(' -', m)
    sys.exit(1)
for a, b in REPS:
    t = t.replace(a, b, 1)
P.write_text(t, encoding='utf-8')
print('updated', len(REPS))
