# table6_expert_cases

| case | ophthalmic | systemic | L1 case | gold shown | engine grade | system shown | expert1 | expert2 |
|---|---|---|---|---|---|---|---|---|
| R01 | Ketorolac | Enoxaparin | B02 (frozen) | medium | medium | medium | low | low |
| R02 | Brimonidine | Tramadol | B12 (frozen) | high | high | high | medium | medium |
| R03 | Dexamethasone | Rifampicin | C17 (frozen) | medium | medium | medium | low | low |
| R04 | Atropine | Tramadol | — | high | high | high | medium | medium |
| R05 | Scopolamine | Amitriptyline | — | high | high | high | medium | medium |
| R06 | Atropine | Oxycodone | — | high | high | high | medium | medium |
| R07 | Levofloxacin | Sotalol | — | low | low | low | low | low |
| R08 | Betaxolol | Verapamil | — | medium | medium | medium | medium | high |
| R09 | Ketorolac | Rivaroxaban | — | medium | medium | medium | low | low |
| R10 | Fluorometholone | Prednisone | B18 (frozen) | low | low | medium | low | low |
| R11 | Fluorometholone | Glimepiride | C20 (frozen) | low | low | medium | low | low |
| R12 | Ketorolac | Warfarin | — | medium | medium | medium | low | low |

Note: `engine grade` is the deposited deterministic cascade's grade for the pair, identical at review time and in the deposited re-run (the cascade's rules, class-matrix levels and registries are unchanged since the 3 August 2026 commit; the only later configuration edit, on 23 September 2026, repaired a malformed advice string and altered no level). `system shown` is the value printed on the questionnaire the experts graded. The two columns differ for R10 and R11: the displayed medium was a class-level conservative hint written by the study team (the question text read "the system grades medium (class-level)"), not the engine's output; the engine grades both pairs low. Expert values are each read from the deposited transcription of that expert's returned questionnaire; expert 1's form is also deposited as a scan. Inter-expert agreement is 11 of 12 (kappa 0.840). R03 is recorded as low/low, per the scanned forms; the kappa values reported in the manuscript are computed from the values in this table.
