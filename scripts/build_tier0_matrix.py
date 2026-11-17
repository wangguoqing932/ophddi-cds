#!/usr/bin/env python3
"""Build Tier 0 edge matrix: classify each of the 37 DDI rules as 0A/0B/exclude."""
import json, yaml
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds")
rules_yaml = ROOT / "configs" / "rules.yaml"
output = ROOT / "outputs" / "tier0_edge_matrix.json"

rules = yaml.safe_load(rules_yaml.read_text(encoding="utf-8"))

# ---- Tier 0 classification criteria ----
# 0A: direct ophthalmic evidence + actionable outcome → automatic alert (high/medium)
# 0B: mechanism extrapolation or contextual risk → conditional review only
# exclude: theoretical only, CYP-only with no ophthalmic evidence, or no specific outcome

edges = []

classifications = {
    # ===== 0A: DIRECT OPHTHALMIC EVIDENCE + ACTIONABLE OUTCOME =====
    "additive_beta_blockade": {
        "tier": "0A",
        "output_class": "clinical_ddi",
        "clinical_outcome": "Bradycardia, heart block, bronchospasm, hypotension, syncope",
        "action": "Monitor HR/BP. Prefer beta1-selective (betaxolol) with punctal occlusion.",
        "evidence_tier": "direct_ophthalmic",
        "source_role": "direct_pair",
        "patient_context": None,
        "entity_scope": "Systemic beta-blockers + verapamil/diltiazem (non-DHP CCBs with AV nodal effects)",
        "rationale": "FDA Timolol label: contraindicated in bradycardia/AV block/cardiac failure. PMID 30773033: timolol+CCB syncope case. PMID 27534869: ~80% systemic absorption. DrugBank DB00373."
    },
    "beta_blocker_cyp2d6_metabolism": {
        "tier": "0A",
        "output_class": "precaution",
        "clinical_outcome": "Increased plasma timolol → exaggerated beta-blockade (bradycardia, hypotension)",
        "action": "Contextual precaution: CYP2D6 PMs at higher risk. Monitor for excessive beta-blockade with strong CYP2D6 inhibitors (paroxetine, fluoxetine).",
        "evidence_tier": "direct_ophthalmic",
        "source_role": "direct_pair",
        "patient_context": "CYP2D6_poor_metabolizer",
        "entity_scope": "Timolol (ophthalmic) + paroxetine/fluoxetine (strong CYP2D6 inhibitors)",
        "rationale": "PMID 27534869 specifically addresses ophthalmic timolol + CYP2D6 inhibitor interaction: ~80% systemic absorption bypasses first-pass metabolism. Patients lacking functional CYP2D6 or taking potent CYP2D6 inhibitors at heightened risk of serious cardiac effects."
    },

    # ===== 0B: CONDITIONAL REVIEW / MECHANISM EXTRAPOLATION =====
    "additive_alpha2_cns_depression": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "CNS depression — primarily pediatric risk; additive sedation with CNS depressants is theoretical",
        "action": "Contraindicated in children <2y (single-drug toxicity, not DDI). Caution with CNS depressants in all ages.",
        "evidence_tier": "direct_ophthalmic_for_pediatric_toxicity",
        "source_role": "exposure_support",
        "patient_context": "pediatric",
        "rationale": "FDA label: brimonidine contraindicated <2y due to apnea/bradycardia/coma. This is SINGLE-DRUG toxicity from systemic absorption, not an established DDI with CNS depressants. Pediatric contraindication belongs as patient factor rule. DDI claim with fentanyl/benzodiazepines lacks combination-level evidence."
    },
    "additive_anticholinergic_effects": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Additive anticholinergic burden: delirium, tachycardia, hyperthermia",
        "action": "Use lowest concentration. Consider tropicamide. Punctal occlusion. Review total anticholinergic burden.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "elderly, polypharmacy",
        "rationale": "Atropine ~64% systemic bioavailability; scopolamine absorption similar to IM. Single-drug systemic toxicity documented but specific DDI evidence with systemic anticholinergics is limited. Category-level pharmacodynamic addition is plausible."
    },
    "additive_corticosteroid_iop": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Elevated IOP — primarily from ophthalmic steroid; additive risk from systemic steroid requires combination evidence",
        "action": "Monitor IOP. Prefer loteprednol. Limit duration. Higher concern with glaucoma history or known steroid responder.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "glaucoma_history, steroid_responder, long_duration",
        "rationale": "Ophthalmic steroids (especially dexamethasone, 50-100% absorption) can elevate IOP. Whether adding systemic steroid produces clinically significant ADDITIONAL IOP elevation requires combination-level evidence. Single-drug IOP risk is well-documented; DDI claim needs more support."
    },
    "sympathomimetic_alpha_interaction": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Possible reduced antihypertensive efficacy from ophthalmic phenylephrine",
        "action": "Monitor BP. Not an established clinical DDI — theoretical concern from systemic absorption.",
        "evidence_tier": "class_extrapolated",
        "source_role": "exposure_support",
        "patient_context": "uncontrolled_hypertension",
        "rationale": "Phenylephrine 10-40 mmHg systolic BP elevation documented. But 'reduces antihypertensive efficacy' is a generic claim, not a specific verified DDI. More appropriate to focus on phenylephrine + MAOI/linezolid/TCA for hypertension risk."
    },
    "cai_diuretic_metabolic_acidosis": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Metabolic acidosis — primarily dorzolamide in renal impairment; additive diuretic effect needs specific mechanism distinction",
        "action": "Monitor bicarbonate and electrolytes. Renal impairment is a required context. Distinguish loop/thiazide/K-sparing diuretic mechanisms.",
        "evidence_tier": "direct_ophthalmic_for_cai_monotherapy",
        "source_role": "class_support",
        "patient_context": "renal_impairment",
        "rationale": "PMID 29333622: dorzolamide-associated NAGMA (pH 7.26, HCO3 17.3) in renal impairment. This is primarily a dorzolamide single-drug risk in vulnerable populations. The 'dorzolamide + all diuretics' DDI claim needs specific combination evidence distinguishing loop vs thiazide vs K-sparing mechanisms."
    },
    "cai_topiramate_acidosis": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Additive metabolic acidosis risk — mechanism-based extrapolation",
        "action": "Caution advised. Monitor bicarbonate levels, especially in renal impairment.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "renal_impairment",
        "rationale": "Both agents inhibit carbonic anhydrase. Mechanism is pharmacologically sound but lacks joint ophthalmic CAI + topiramate clinical/regulatory evidence. Mechanism extrapolation, not direct DDI evidence."
    },
    "sympathomimetic_maoi_hypertension": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Hypertensive crisis (well-documented for systemic route; theoretical from ophthalmic route)",
        "action": "Clinical review advised. Monitor BP. Avoid combination in patients with hypertension or cardiac disease.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "hypertension, cardiovascular_disease",
        "rationale": "Phenylephrine + MAOI hypertensive crisis well-documented for systemic route. Ophthalmic route absorption is lower but non-zero via nasolacrimal drainage. No direct ophthalmic case reports found for MAOI. For linezolid, similar concern."
    },
    "sympathomimetic_tca_hypertension": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Potentiated hypertensive effect of phenylephrine via NE reuptake inhibition",
        "action": "Clinical DDI: monitor BP. Avoid combination in patients with hypertension or cardiac disease.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "hypertension, cardiovascular_disease",
        "rationale": "TCAs/SNRIs inhibit NE reuptake, potentiating phenylephrine. DDInter Major. Direct ophthalmic evidence is limited."
    },
    "beta_blocker_beta2_agonist_antagonism": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Bronchospasm in asthma/COPD — primarily from non-selective BB contraindication, not a DDI per se",
        "action": "Prefer beta1-selective. Use punctal occlusion. Asthma/COPD is contraindication context, not a DDI.",
        "evidence_tier": "direct_ophthalmic_for_monotherapy_contraindication",
        "source_role": "exposure_support",
        "patient_context": "asthma, COPD",
        "rationale": "Non-selective ophthalmic beta-blockers are contraindicated in asthma per FDA label (single-drug risk). The 'DDI with beta-2 agonist' is conceptually distinct from 'contraindicated in asthmatics on beta-2 agonist therapy'. Should be framed as patient-specific contraindication, not drug-pair DDI."
    },
    "nsaid_antihypertensive_antagonism": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Reduced antihypertensive efficacy via renal prostaglandin inhibition",
        "action": "Monitor BP when using topical NSAIDs in hypertensive patients, especially flurbiprofen (74% bioavailability).",
        "evidence_tier": "class_extrapolated",
        "source_role": "exposure_support",
        "patient_context": "hypertension, heart_failure, CKD",
        "rationale": "Flurbiprofen has ~74% systemic bioavailability. DDInter Major for systemic route. Direct ophthalmic evidence limited."
    },
    "nsaid_acei_arb_antagonism": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Reduced antihypertensive effect, worsened renal function in HF/CKD",
        "action": "Contextual precaution: monitor BP and renal function.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "heart_failure, CKD",
        "rationale": "NSAIDs blunt ACEi/ARB effect. DDInter Major. Primarily systemic NSAID concern."
    },
    "nsaid_diuretic_antagonism": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Reduced diuretic efficacy, worsened heart failure control",
        "action": "Contextual precaution: monitor fluid status and BP.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "heart_failure",
        "rationale": "NSAIDs inhibit renal prostaglandin-mediated natriuresis. Primarily systemic NSAID concern."
    },
    "additive_nsaid_bleeding": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Increased ocular surface bleeding risk, especially perioperative",
        "action": "Caution with anticoagulants before ocular surgery. Flurbiprofen has 74% absorption.",
        "evidence_tier": "class_extrapolated",
        "source_role": "exposure_support",
        "patient_context": "perioperative, anticoagulated",
        "rationale": "FDA Ketorolac label: bleeding risk. Clinical significance primarily perioperative."
    },
    "immunosuppressant_nsaid_nephrotoxicity": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Additive renal vasoconstriction",
        "action": "Monitor renal function. Ophthalmic CNI absorption is minimal.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "renal_impairment",
        "rationale": "CNIs + NSAIDs: additive renal vasoconstriction. Ophthalmic CNI absorption is minimal; risk primarily from systemic NSAID."
    },
    "corticosteroid_nti_interaction": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Altered glucose control in diabetics, altered anticoagulant efficacy",
        "action": "Contextual precaution: monitor glucose. Monitor INR in warfarin patients. Dexamethasone has 50-100% absorption.",
        "evidence_tier": "class_extrapolated",
        "source_role": "exposure_support",
        "patient_context": "diabetes, anticoagulated",
        "rationale": "Systemically absorbed ophthalmic corticosteroids (especially dexamethasone) may affect NTI drug outcomes. Limited direct ophthalmic combination evidence."
    },
    "antibiotic_warfarin_enhancement": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Enhanced warfarin effect via gut flora vitamin K alteration",
        "action": "Monitor INR when starting/stopping topical ophthalmic antibiotics in warfarin patients.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "anticoagulated",
        "rationale": "DDInter Major for systemic antibiotics. Ophthalmic antibiotics have low systemic absorption but INR monitoring is prudent."
    },
    "anticholinergic_qt_prolongation": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Tachycardia exacerbating QT-prolonging drug effects (theoretical)",
        "action": "Theoretical mechanism signal. Monitor ECG if symptoms develop.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": None,
        "rationale": "Atropine ~64% bioavailability → tachycardia. Theoretical exacerbation of QT-prolonging drugs. No direct ophthalmic case reports."
    },
    "fluoroquinolone_corticosteroid_tendon": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Increased tendon rupture risk (3-5x with concurrent systemic use)",
        "action": "FDA class warning applies. Ophthalmic FQs have low systemic absorption; risk primarily from systemic corticosteroid.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "elderly, renal_impairment",
        "rationale": "FDA Boxed Warning for systemic FQ+corticosteroid. Ophthalmic FQ absorption is low."
    },
    "qt_prolongation_risk": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "QT prolongation (theoretical from ophthalmic fluoroquinolone dose)",
        "action": "Caution with antiarrhythmics. Consider alternatives if QTc prolonged.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "prolonged_QTc, electrolyte_disturbance",
        "rationale": "FDA fluoroquinolone safety communication. Low systemic absorption from ophthalmic route limits significance."
    },
    "moderate_abs_beta_blocker": {
        "tier": "0B",
        "output_class": "precaution",
        "clinical_outcome": "Additive beta-blockade — lower risk than non-selective agents",
        "action": "Contextual precaution: monitor HR/BP. Betaxolol is safer than timolol.",
        "evidence_tier": "direct_ophthalmic",
        "source_role": "class_support",
        "patient_context": None,
        "rationale": "Betaxolol (beta1-selective, moderate absorption) with systemic beta-blockers."
    },
    "moderate_abs_antiplatelet": {
        "tier": "0B",
        "output_class": "theoretical_mechanism",
        "clinical_outcome": "Marginal increased bleeding risk (theoretical)",
        "action": "Low concern. Monitor for ocular surface bleeding post-surgery.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "perioperative",
        "rationale": "Moderate absorption drugs + antiplatelets. Risk primarily theoretical."
    },
    "moderate_abs_anticoagulant": {
        "tier": "0B",
        "output_class": "theoretical_mechanism",
        "clinical_outcome": "Theoretical increased bleeding risk",
        "action": "Low concern. Precaution with ocular surgery.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": "perioperative",
        "rationale": "Brimonidine/betaxolol/dorzolamide moderate absorption + anticoagulants. Limited evidence."
    },
    "moderate_abs_cyp2d6": {
        "tier": "0B",
        "output_class": "theoretical_mechanism",
        "clinical_outcome": "CYP2D6 substrate competition (theoretical)",
        "action": "Theoretical. Not clinically significant for ophthalmic route.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": None,
        "rationale": "Betaxolol CYP2D6 metabolism. Clinical significance low for ophthalmic dose."
    },
    "moderate_abs_diuretic": {
        "tier": "0B",
        "output_class": "theoretical_mechanism",
        "clinical_outcome": "Additive electrolyte effects (theoretical for non-CAI drugs)",
        "action": "Theoretical for non-CAI drugs. Dorzolamide already covered by CAI-diuretic rule.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": None,
        "rationale": "Dorzolamide/brimonidine with diuretics. CAI activity is primary concern."
    },
    "alpha2_agonist_antiplatelet": {
        "tier": "0B",
        "output_class": "theoretical_mechanism",
        "clinical_outcome": "No direct pharmacodynamic interaction expected",
        "action": "Generally safe. No dose adjustment needed.",
        "evidence_tier": "class_extrapolated",
        "source_role": "mechanism_support",
        "patient_context": None,
        "rationale": "Brimonidine + antiplatelets. No known antiplatelet mechanism. Low systemic absorption."
    },

    # ===== EXCLUDE =====
    "systemic_absorption_high_risk": {
        "tier": "exclude",
        "reason": "NOT a DDI edge. 'High systemic absorption' is a drug property, not a drug-pair interaction. Merge as weighting/exposure attribute into specific rules (additive_beta_blockade, cai_diuretic, etc.)."
    },
    "systemic_absorption_moderate_risk": {
        "tier": "exclude",
        "reason": "Same as above — 'moderate absorption + NTI' is a generic screening heuristic, not a verifiable DDI edge."
    },
    "topical_corticosteroid_cyp3a4_induction": {
        "tier": "exclude",
        "reason": "Dexamethasone is weak CYP3A4 inducer. Minimal significance from ophthalmic dose. No ophthalmic DDI evidence."
    },
    "pga_antiplatelet_bleeding": {
        "tier": "exclude",
        "reason": "Prostaglandin analogs have minimal systemic absorption. No validated bleeding risk from ophthalmic PGA use."
    },
    "p_gp_mediated_absorption": {
        "tier": "exclude",
        "reason": "Clinical significance for topical ophthalmic route not established. Theoretical transporter mechanism only."
    },
    "calcineurin_inhibitor_cyp3a4": {
        "tier": "exclude",
        "reason": "Ophthalmic CNI absorption is negligible. Systemic CYP3A4 inhibitor interaction is a systemic drug concern, not ophthalmic DDI."
    },
    "macrolide_cyp3a4_inhibition": {
        "tier": "exclude",
        "reason": "Topical ophthalmic macrolides have very low systemic absorption. CYP3A4 inhibition is a systemic macrolide concern."
    },
    "azole_cyp3a4_inhibition": {
        "tier": "exclude",
        "reason": "Topical ophthalmic azoles have low systemic absorption. CYP inhibition is a systemic azole concern."
    },
    "low_abs_antiplatelet": {
        "tier": "exclude",
        "reason": "Low absorption drugs have negligible antiplatelet interaction. No clinical action needed."
    },
    "low_abs_anticoagulant": {
        "tier": "exclude",
        "reason": "Low absorption drugs have negligible anticoagulant interaction. No clinical action needed."
    },
}

# Build edge matrix
edge_list = []
for rule in rules["rules"]:
    rid = rule["id"]
    cls = classifications.get(rid, {"tier": "unclassified", "reason": "Not reviewed"})
    
    edge = {
        "rule_id": rid,
        "entity_a_flags": rule.get("entity_a_flags", []),
        "entity_b_flags": rule.get("entity_b_flags", []),
        "severity": rule.get("severity"),
        "risk_type": rule.get("risk_type"),
        "clinical_outcome": cls.get("clinical_outcome", ""),
        "action": cls.get("action", ""),
        "risk_behavior": "automatic_alert" if cls["tier"] == "0A" else ("conditional_review" if cls["tier"] == "0B" else "excluded"),
        "output_class": cls.get("output_class", "theoretical_mechanism"),
        "evidence_tier": cls.get("evidence_tier", ""),
        "source_role": cls.get("source_role", ""),
        "entity_scope": cls.get("entity_scope", ""),
        "patient_context": cls.get("patient_context"),
        "tier": cls["tier"],
        "rationale": cls.get("rationale", cls.get("reason", "")),
        "citations": rule.get("citations", [])
    }
    edge_list.append(edge)

# Patient factor rules
pf_edges = []
for pf_id, pf in rules.get("patient_factor_rules", {}).items():
    pf_edge = {
        "rule_id": f"patient_factor:{pf_id}",
        "tier": "0B",
        "risk_behavior": "conditional_review",
        "clinical_outcome": {
            "elderly": "Reduced clearance, polypharmacy → increased drug exposure and sensitivity",
            "renal_impairment": "Reduced renal clearance → elevated drug levels, metabolic acidosis risk with CAIs",
            "polypharmacy": "≥5 medications → cumulative DDI risk from ocular + systemic drug burden"
        }.get(pf_id, ""),
        "action": {
            "elderly": "Escalate monitoring for bradycardia, hypotension, falls risk.",
            "renal_impairment": "Monitor drug levels of NTI drugs. Monitor bicarbonate with CAIs.",
            "polypharmacy": "Conduct comprehensive medication reconciliation."
        }.get(pf_id, ""),
        "evidence_tier": "class_extrapolated",
        "citations": pf.get("citations", [])
    }
    pf_edges.append(pf_edge)

report = {
    "title": "Tier 0 Edge Matrix — Ophthalmic DDI CDS",
    "generated": datetime.now().isoformat(),
    "summary": {
        "total_rules": len(rules["rules"]),
        "tier_0A_automatic_alert": sum(1 for e in edge_list if e["tier"] == "0A"),
        "tier_0B_conditional_review": sum(1 for e in edge_list if e["tier"] == "0B"),
        "excluded": sum(1 for e in edge_list if e["tier"] == "exclude"),
        "patient_factor_rules": len(pf_edges)
    },
    "edges": edge_list,
    "patient_factors": pf_edges
}

output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Tier 0 matrix written to {output}")
print(f"  0A (automatic alert):     {report['summary']['tier_0A_automatic_alert']}")
print(f"  0B (conditional review):  {report['summary']['tier_0B_conditional_review']}")
print(f"  Excluded:                 {report['summary']['excluded']}")
print(f"  Patient factors:          {report['summary']['patient_factor_rules']}")
