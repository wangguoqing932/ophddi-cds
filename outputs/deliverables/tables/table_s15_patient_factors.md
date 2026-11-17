| Patient factor | How it is represented | Effect on the output | Gap |
|---|---|---|---|
| Age | No age input. An `elderly` patient-factor policy (≥65 years) exists as a contextual advisory; paediatric susceptibility is captured only through agent flags and evidence (e.g., alpha-2 agonists). | The pair grade is unchanged; the advisory is returned separately. | Age is not a modifier of the grade; no paediatric dosing or age-specific threshold is modelled. |
| Renal function | A `renal_impairment` policy links medium-absorption agents to narrow-therapeutic-index systemic drugs; no eGFR or creatinine input. | Contextual advisory only; the pair grade is unchanged. | Renal clearance is not quantified; dialysis and acute kidney injury are not represented. |
| Hepatic function | Not modelled. | No effect. | No hepatic flag, policy or dose adjustment. |
| QT risk | `qt_prolonging` flags and the two QT rules; no QTc value or patient-level QT history. | Can raise the grade through a rule; no patient-specific QT risk. | QTc, electrolytes, congenital long-QT and concurrent QT drugs are not integrated. |
| Dose and duration | Not modelled; the system assumes labelled ophthalmic dosing. | No effect. | Cumulative exposure, duration, adherence and overdosing are not represented. |
| CYP phenotype | `cyp2d6_substrate` and `cyp3a4_substrate` flags and the CYP rules; no genotype input. | Can raise the grade through a rule; no phenotype-specific effect. | Metaboliser status, CYP2D6 inhibitors and genotype-guided dosing are not integrated. |
| Instillation technique | Not modelled. Punctal occlusion and nasolacrimal drainage are cited in the evidence and recommendations. | No effect. | Technique, punctal occlusion, drop size and patient adherence are not inputs; they are discussed as exposure modifiers. |

The system is therefore pair-level with three contextual patient-factor advisories, not a patient-level risk model. This is stated in the Intended use section and in the Limitations.
