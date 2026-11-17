**Table 2a. Rule inventory: identifier, severity, risk type and match semantics.**

| Rule ID | Sev. | Risk type | Match |
|---|---|---|---|
| additive_beta_blockade | high | PD cardiovascular | all |
| beta_blocker_ccb_additive | high | PD cardiovascular | all |
| beta_blocker_digoxin_additive | high | PD cardiovascular | all |
| additive_alpha2_cns_depression | high | PD CNS | any |
| additive_anticholinergic_effects | medium | PD anticholinergic | any |
| additive_corticosteroid_iop | medium | PD ocular hypertension | any |
| additive_nsaid_bleeding | medium | PD hemorrhagic | any |
| sympathomimetic_alpha_interaction | medium | PD cardiovascular | any |
| qt_prolongation_risk | low | PD cardiotoxic | any |
| pga_antiplatelet_bleeding | low | PD hemorrhagic | any |
| cai_diuretic_metabolic_acidosis | medium | PK metabolic | any |
| cai_topiramate_acidosis | medium | PK metabolic | any |
| dexamethasone_cyp3a4_induction | low | PK CYP3A4 | all |
| topical_corticosteroid_cyp3a4_induction | low | PK CYP3A4 | any |
| systemic_absorption_high_risk | low | Systemic absorption | any |
| systemic_absorption_moderate_risk | low | Systemic absorption | any |
| p_gp_mediated_absorption | low | PK transporter | any |
| calcineurin_inhibitor_cyp3a4 | low | PK CYP3A4 | any |
| macrolide_cyp3a4_inhibition | low | PK CYP3A4 | any |
| azole_cyp3a4_inhibition | low | PK CYP3A4 | any |
| sympathomimetic_maoi_hypertension | high | PD cardiovascular | any |
| beta_blocker_beta2_agonist_antagonism | high | PD respiratory | any |
| immunosuppressant_nsaid_nephrotoxicity | medium | PD renal | any |
| fluoroquinolone_corticosteroid_tendon | low | PD musculoskeletal | any |
| nsaid_antihypertensive_antagonism | high | PD cardiovascular | any |
| nsaid_diuretic_antagonism | medium | PD cardiovascular | any |
| antibiotic_warfarin_enhancement | low | PK anticoagulation | all |
| beta_blocker_cyp2d6_metabolism | medium | PK CYP2D6 | any |
| nsaid_acei_arb_antagonism | medium | PD cardiovascular | any |
| corticosteroid_nti_interaction | medium | PD endocrine | any |
| sympathomimetic_tca_hypertension | high | PD cardiovascular | any |
| anticholinergic_qt_prolongation | medium | PD cardiotoxic | any |
| moderate_abs_antiplatelet | low | PD hemorrhagic | any |
| moderate_abs_beta_blocker | medium | PD cardiovascular | any |
| moderate_abs_anticoagulant | low | PD hemorrhagic | any |
| moderate_abs_cyp2d6 | low | PK CYP2D6 | any |
| moderate_abs_diuretic | low | PK metabolic | any |
| alpha2_agonist_antiplatelet | low | PD hemorrhagic | any |
| low_abs_antiplatelet | low | PD hemorrhagic | any |
| low_abs_anticoagulant | low | PD hemorrhagic | any |

**Table 2b. Rule inventory: ophthalmic and systemic flag predicates.**

| Rule ID | Ophthalmic flags | Systemic flags |
|---|---|---|
| additive_beta_blockade | beta blocker; systemic absorption high | beta blocker systemic |
| beta_blocker_ccb_additive | beta blocker; systemic absorption high | l type calcium channel blocker |
| beta_blocker_digoxin_additive | beta blocker; systemic absorption high | na k atpase inhibitor |
| additive_alpha2_cns_depression | alpha2 agonist | cns depressant |
| additive_anticholinergic_effects | anticholinergic | anticholinergic systemic |
| additive_corticosteroid_iop | corticosteroid | corticosteroid systemic |
| additive_nsaid_bleeding | nsaid | anticoagulant |
| sympathomimetic_alpha_interaction | sympathomimetic | antihypertensive |
| qt_prolongation_risk | fluoroquinolone | qt prolonging |
| pga_antiplatelet_bleeding | prostaglandin analog | antiplatelet |
| cai_diuretic_metabolic_acidosis | cai topical | diuretic |
| cai_topiramate_acidosis | cai topical | cai systemic |
| dexamethasone_cyp3a4_induction | corticosteroid; systemic absorption medium | cyp3a4 substrate |
| topical_corticosteroid_cyp3a4_induction | corticosteroid | cyp3a4 substrate |
| systemic_absorption_high_risk | systemic absorption high | beta blocker systemic |
| systemic_absorption_moderate_risk | systemic absorption medium | narrow therapeutic index |
| p_gp_mediated_absorption | p gp substrate | p gp inhibitor |
| calcineurin_inhibitor_cyp3a4 | calcineurin inhibitor | cyp3a4 inhibitor |
| macrolide_cyp3a4_inhibition | macrolide | cyp3a4 substrate |
| azole_cyp3a4_inhibition | azole | cyp3a4 substrate |
| sympathomimetic_maoi_hypertension | sympathomimetic | maoi |
| beta_blocker_beta2_agonist_antagonism | beta blocker | beta2 adrenergic agonist |
| immunosuppressant_nsaid_nephrotoxicity | calcineurin inhibitor | cox1 cox2 inhibitor |
| fluoroquinolone_corticosteroid_tendon | fluoroquinolone | corticosteroid systemic |
| nsaid_antihypertensive_antagonism | nsaid | antihypertensive |
| nsaid_diuretic_antagonism | nsaid | ncc inhibitor; nkcc2 inhibitor |
| antibiotic_warfarin_enhancement | antibiotic | narrow therapeutic index; vitamin k epoxide reductase inhibitor |
| beta_blocker_cyp2d6_metabolism | beta blocker | cyp2d6 inhibitor |
| nsaid_acei_arb_antagonism | nsaid | ace inhibitor; angiotensin ii receptor antagonist |
| corticosteroid_nti_interaction | corticosteroid | narrow therapeutic index |
| sympathomimetic_tca_hypertension | sympathomimetic | net inhibitor |
| anticholinergic_qt_prolongation | anticholinergic | qt prolonging |
| moderate_abs_antiplatelet | systemic absorption medium | antiplatelet |
| moderate_abs_beta_blocker | systemic absorption medium | beta blocker systemic |
| moderate_abs_anticoagulant | systemic absorption medium | anticoagulant |
| moderate_abs_cyp2d6 | systemic absorption medium | cyp2d6 substrate |
| moderate_abs_diuretic | systemic absorption medium | diuretic |
| alpha2_agonist_antiplatelet | alpha2 agonist | antiplatelet |
| low_abs_antiplatelet | systemic absorption low | antiplatelet |
| low_abs_anticoagulant | systemic absorption low | anticoagulant |

**Table 2c. Patient-factor policies (3 contextual policies, not applied to the pair grade).**

| Policy | Severity | Matching entity-B flags | Match | Rationale | Recommendation |
|---|---|---|---|---|---|
| elderly | medium | narrow_therapeutic_index | all | Age ≥65: reduced clearance, polypharmacy, increased sensitivity. | Escalate monitoring for bradycardia, hypotension and falls risk. |
| renal impairment | medium | narrow_therapeutic_index (with ophthalmic medium absorption) | all | Renal impairment reduces clearance of narrow-therapeutic-index drugs. | Monitor drug levels of narrow-therapeutic-index drugs. |
| polypharmacy | medium | narrow_therapeutic_index | all | ≥5 systemic medications increase DDI risk; include ocular drugs in the review. | Conduct comprehensive medication reconciliation. |

Note: `nsaid_antihypertensive_antagonism` is gated on absorption in the primary analysis (Section 4.2); `dexamethasone_cyp3a4_induction` is low severity and matches medium-absorption corticosteroids after the measured-exposure correction.
