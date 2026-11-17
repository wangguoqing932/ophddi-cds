"""
Bulk generate evidence chunks for all major ophthalmic DDI pathways.
Target: 100+ evidence chunks covering all flag-based interaction categories.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def generate() -> list[dict]:
    chunks = []
    ev_id = [0]

    def next_id() -> str:
        ev_id[0] += 1
        return f"ev_{ev_id[0]:04d}"

    # ===== 1. BETA-BLOCKER ADDITIVE =====
    chunks.append({
        "evidence_id": next_id(), "title": "Additive beta-blockade: topical + systemic beta blockers",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "A",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0001", "topical_ophthalmic_0002", "topical_ophthalmic_0003",
                        "topical_ophthalmic_0004", "topical_ophthalmic_0005"],
        "entities_b": ["sys_med_0001", "sys_med_0002", "sys_med_0003", "sys_med_0004",
                        "sys_med_0005", "sys_med_0006", "sys_med_0007", "sys_med_0008"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Topical ophthalmic beta-blockers are systemically absorbed (34-80% via nasolacrimal duct). "
                "Concurrent use with oral beta-blockers produces additive beta-adrenergic blockade. "
                "This can cause bradycardia, hypotension, heart block, bronchospasm, and masking of hypoglycemia. "
                "Non-selective beta-blockers (timolol, levobunolol) have higher systemic risk than beta1-selective (betaxolol). "
                "Risk is highest in elderly, COPD, and diabetic patients. Punctal occlusion reduces systemic absorption by ~60%.",
        "url": "https://go.drugbank.com/drugs/DB00373", "weight": 3,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Beta-blocker interaction with calcium channel blockers (CV add-on)",
        "source": "PubMed / DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0001", "topical_ophthalmic_0003", "topical_ophthalmic_0005"],
        "entities_b": ["sys_med_0012", "sys_med_0013"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Topical beta-blockers combined with non-DHP calcium channel blockers (verapamil, diltiazem) "
                "increase risk of bradycardia, AV block, and heart failure through additive negative chronotropic effects. "
                "ECG and heart rate monitoring recommended. DHP-CCBs (amlodipine, nifedipine) have lower interaction risk.",
        "url": "", "weight": 1,
    })

    # ===== 2. ALPHA-2 AGONIST CNS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Brimonidine CNS depression with psychotropics/opioids",
        "source": "FDA Label / DrugBank", "source_type": "regulatory", "evidence_level": "A",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0012", "topical_ophthalmic_0013"],
        "entities_b": ["sys_med_0070", "sys_med_0071", "sys_med_0072",
                        "sys_med_0085", "sys_med_0086", "sys_med_0089",
                        "sys_med_0099", "sys_med_0101", "sys_med_0167"],
        "risk_types": ["pharmacodynamic", "cns_depression"],
        "text": "Brimonidine is an alpha2-adrenergic agonist that can cause CNS depression including somnolence, "
                "dizziness, hypotension, and apnea. Contraindicated in children <2 years. Concurrent use with CNS "
                "depressants (opioids, antipsychotics, benzodiazepines, hypnotics) produces additive sedation. "
                "MAO inhibitors are also contraindicated with brimonidine due to risk of hypertensive crisis.",
        "url": "", "weight": 3,
    })

    # ===== 3. ANTICHOLINERGIC =====
    chunks.append({
        "evidence_id": next_id(), "title": "Systemic anticholinergic effects of ophthalmic mydriatics",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0073", "topical_ophthalmic_0074", "topical_ophthalmic_0075",
                        "topical_ophthalmic_0076", "topical_ophthalmic_0077"],
        "entities_b": ["sys_med_0069", "sys_med_0082", "sys_med_0083",
                        "sys_med_0046", "sys_med_0209", "sys_med_0112"],
        "risk_types": ["pharmacodynamic", "anticholinergic"],
        "text": "Ophthalmic anticholinergics (atropine, cyclopentolate, homatropine, scopolamine) are systemically "
                "absorbed via nasolacrimal duct. Additive anticholinergic effects with systemic anticholinergics "
                "(diphenhydramine, TCAs, antiparkinson drugs) can cause delirium, hyperthermia, ileus, urinary "
                "retention, and tachycardia. Elderly patients are most vulnerable. Tropicamide has shortest duration "
                "and lowest systemic risk. Phenylephrine (alpha-agonist mydriatic) does not share this interaction.",
        "url": "", "weight": 2,
    })

    # ===== 4. CORTICOSTEROID IOP =====
    chunks.append({
        "evidence_id": next_id(), "title": "Corticosteroid-induced IOP elevation: topical + systemic",
        "source": "PubMed / Comprehensive review", "source_type": "literature", "evidence_level": "A",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0051", "topical_ophthalmic_0052", "topical_ophthalmic_0053",
                        "topical_ophthalmic_0054", "topical_ophthalmic_0055"],
        "entities_b": ["sys_med_0055", "sys_med_0056", "sys_med_0057"],
        "risk_types": ["pharmacodynamic", "ocular_hypertension"],
        "text": "Topical ophthalmic corticosteroids (prednisolone, dexamethasone, fluorometholone, loteprednol, "
                "rimexolone) and systemic corticosteroids both elevate intraocular pressure by increasing aqueous "
                "outflow resistance. Additive IOP elevation can accelerate glaucomatous optic neuropathy. "
                "Loteprednol has lower IOP risk due to site-specific esterase activation in ocular tissues. "
                "IOP monitoring is recommended in patients on concurrent topical and systemic corticosteroids.",
        "url": "", "weight": 3,
    })

    # ===== 5. NSAID + ANTICOAGULANT =====
    chunks.append({
        "evidence_id": next_id(), "title": "Ocular bleeding risk: topical NSAIDs + anticoagulants",
        "source": "FDA Label / PubMed", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0056", "topical_ophthalmic_0057", "topical_ophthalmic_0058",
                        "topical_ophthalmic_0059", "topical_ophthalmic_0060"],
        "entities_b": ["sys_med_0027", "sys_med_0028", "sys_med_0029", "sys_med_0030",
                        "sys_med_0031", "sys_med_0032", "sys_med_0033"],
        "risk_types": ["pharmacodynamic", "hemorrhagic"],
        "text": "Topical ophthalmic NSAIDs inhibit COX-1 and COX-2 enzymes reducing thromboxane A2 production. "
                "While systemic absorption is low (typically <5%), concurrent use with anticoagulants (warfarin, "
                "DOACs) or antiplatelets (aspirin, clopidogrel, ticagrelor) may increase risk of subconjunctival "
                "hemorrhage and intraoperative bleeding during ocular surgery. Risk is highest with ketorolac "
                "and lowest with nepafenac (prodrug). Pre-operative discontinuation should be considered.",
        "url": "", "weight": 2,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Topical NSAIDs + systemic NSAIDs: additive GI/renal risk",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0056", "topical_ophthalmic_0058", "topical_ophthalmic_0059"],
        "entities_b": ["sys_med_0052", "sys_med_0053", "sys_med_0054"],
        "risk_types": ["pharmacodynamic", "toxicity"],
        "text": "Although topical ophthalmic NSAIDs have minimal systemic absorption, concurrent use with systemic "
                "NSAIDs may marginally increase the risk of gastrointestinal irritation and renal impairment in "
                "susceptible patients. The interaction is theoretical rather than well-documented for the ophthalmic route.",
        "url": "", "weight": 1,
    })

    # ===== 6. PHENYLEPHRINE CARDIOVASCULAR =====
    chunks.append({
        "evidence_id": next_id(), "title": "Phenylephrine ophthalmic: hypertensive risk with CVD drugs",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0078"],
        "entities_b": ["sys_med_0009", "sys_med_0010", "sys_med_0011",
                        "sys_med_0005", "sys_med_0003"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Ophthalmic phenylephrine 2.5-10% is systemically absorbed especially in children and elderly. "
                "It can reduce antihypertensive efficacy of CCBs and can cause hypertensive crisis in patients "
                "on non-selective beta-blockers (propranolol, carvedilol) via unopposed alpha-adrenergic stimulation. "
                "Avoid high concentrations in patients with hypertension, cardiac disease, or aneurysms.",
        "url": "", "weight": 2,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Dipivefrin/prodrug epinephrine: CV effects",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0093"],
        "entities_b": ["sys_med_0001", "sys_med_0002", "sys_med_0003",
                        "sys_med_0009", "sys_med_0012", "sys_med_0013"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Dipivefrin is a prodrug of epinephrine that can cause mydriasis and may increase blood pressure. "
                "Interaction profile is similar to phenylephrine. Use with beta-blockers may cause initial hypertensive "
                "episode followed by bradycardia (beta-blockade unopposed alpha effect).",
        "url": "", "weight": 1,
    })
    # Decongestants CV
    chunks.append({
        "evidence_id": next_id(), "title": "Ophthalmic decongestants: CV interactions",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0091", "topical_ophthalmic_0092"],
        "entities_b": ["sys_med_0009", "sys_med_0010", "sys_med_0005", "sys_med_0003"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Topical decongestants (naphazoline, tetrahydrozoline) are alpha-adrenergic agonists that can "
                "cause systemic vasoconstriction. May reduce antihypertensive efficacy and interact with "
                "beta-blockers. Avoid in patients with poorly controlled hypertension.",
        "url": "", "weight": 1,
    })

    # ===== 7. CAI METABOLIC =====
    chunks.append({
        "evidence_id": next_id(), "title": "Topical CAI + diuretics: additive metabolic acidosis",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "B",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0014", "topical_ophthalmic_0015"],
        "entities_b": ["sys_med_0022", "sys_med_0023", "sys_med_0025", "sys_med_0026"],
        "risk_types": ["pharmacokinetic", "metabolic"],
        "text": "Topical carbonic anhydrase inhibitors (dorzolamide, brinzolamide) can be systemically absorbed "
                "and inhibit renal carbonic anhydrase leading to bicarbonate excretion. When combined with "
                "diuretics (HCTZ, furosemide, acetazolamide) there is additive risk of hyperchloremic metabolic "
                "acidosis. Elderly patients and those with renal impairment are at highest risk. Monitor serum "
                "electrolytes and bicarbonate during concurrent therapy.",
        "url": "", "weight": 2,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Topical CAI + topiramate: metabolic acidosis",
        "source": "PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0014", "topical_ophthalmic_0015"],
        "entities_b": ["sys_med_0092"],
        "risk_types": ["pharmacokinetic", "metabolic"],
        "text": "Both topical CAIs and topiramate (which has weak CAI activity) can cause metabolic acidosis via "
                "carbonic anhydrase inhibition. Concurrent use may have additive effects on serum bicarbonate "
                "reduction. More common in patients with pre-existing renal impairment or on ketogenic diet.",
        "url": "", "weight": 1,
    })

    # ===== 8. PROSTAGLANDIN ANALOG + ANTIPLATELET =====
    chunks.append({
        "evidence_id": next_id(), "title": "Prostaglandin analogs: ocular inflammation and bleeding risk",
        "source": "FDA Label / DrugBank", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0006", "topical_ophthalmic_0007",
                        "topical_ophthalmic_0008", "topical_ophthalmic_0009",
                        "topical_ophthalmic_0010", "topical_ophthalmic_0011"],
        "entities_b": ["sys_med_0027", "sys_med_0028", "sys_med_0029",
                        "sys_med_0031", "sys_med_0032", "sys_med_0033"],
        "risk_types": ["pharmacodynamic", "hemorrhagic"],
        "text": "Prostaglandin analogs (latanoprost, travoprost, bimatoprost, tafluprost) are generally safe with "
                "anticoagulants due to minimal systemic absorption (<5%). However, they can cause conjunctival "
                "hyperemia and ocular inflammation. In patients on anticoagulation, there may be increased risk of "
                "subconjunctival hemorrhage, though clinical significance is low. Monitor for ocular surface bleeding.",
        "url": "", "weight": 1,
    })

    # ===== 9. FLUOROQUINOLONE QT =====
    chunks.append({
        "evidence_id": next_id(), "title": "QT prolongation: topical fluoroquinolones + antiarrhythmics",
        "source": "FDA Safety Communication", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0029", "topical_ophthalmic_0030",
                        "topical_ophthalmic_0031", "topical_ophthalmic_0032",
                        "topical_ophthalmic_0033", "topical_ophthalmic_0034"],
        "entities_b": ["sys_med_0044", "sys_med_0007"],
        "risk_types": ["pharmacodynamic", "qt_prolongation"],
        "text": "Systemic fluoroquinolones prolong QT interval via hERG potassium channel blockade. While topical "
                "ophthalmic fluoroquinolones have negligible systemic absorption (<1%), the FDA class warning applies. "
                "Caution in patients on class III antiarrhythmics (amiodarone, sotalol) with pre-existing QTc "
                "prolongation or electrolyte abnormalities. Use non-fluoroquinolone alternatives when possible.",
        "url": "", "weight": 1,
    })

    # ===== 10. CYP450 MEDIATED =====
    chunks.append({
        "evidence_id": next_id(), "title": "CYP3A4 induction: dexamethasone + CYP3A4 substrates",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0052"],
        "entities_b": ["sys_med_0041", "sys_med_0043", "sys_med_0049",
                        "sys_med_0061", "sys_med_0055", "sys_med_0056"],
        "risk_types": ["pharmacokinetic", "cyp_metabolism"],
        "text": "Dexamethasone is a CYP3A4 substrate and weak inducer. Chronic topical ophthalmic use could "
                "theoretically reduce plasma levels of CYP3A4 substrates (atorvastatin, simvastatin, midazolam, "
                "clarithromycin, oral contraceptives). However, clinical significance is minimal due to low "
                "systemic dose. Awareness warranted during long-term therapy (>2 weeks).",
        "url": "", "weight": 1,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Cyclosporine ophthalmic: CYP3A4/P-gp interactions",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0061"],
        "entities_b": ["sys_med_0061", "sys_med_0064", "sys_med_0012", "sys_med_0013"],
        "risk_types": ["pharmacokinetic", "cyp_metabolism"],
        "text": "Cyclosporine ophthalmic emulsion (Restasis) has negligible systemic absorption with blood levels "
                "below detection limits. CYP3A4-mediated interactions with clarithromycin, itraconazole, verapamil, "
                "or diltiazem are not clinically significant for the ophthalmic route.",
        "url": "", "weight": 1,
    })

    # ===== 11. ANTIBIOTIC + WARFARIN =====
    chunks.append({
        "evidence_id": next_id(), "title": "Topical antibiotics and warfarin interaction",
        "source": "DrugBank / FDA", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0029", "topical_ophthalmic_0030",
                        "topical_ophthalmic_0035", "topical_ophthalmic_0040"],
        "entities_b": ["sys_med_0027"],
        "risk_types": ["pharmacokinetic", "anticoagulation"],
        "text": "Some systemic antibiotics enhance warfarin effect by reducing gut flora vitamin K production. "
                "Topical ophthalmic antibiotics have minimal systemic absorption and are not expected to cause "
                "clinically significant INR elevation. However, monitor INR in patients on warfarin during "
                "prolonged topical antibiotic use as a precaution.",
        "url": "", "weight": 1,
    })

    # ===== 12. MIOTICS + CHOLINERGIC =====
    chunks.append({
        "evidence_id": next_id(), "title": "Cholinergic miotics: systemic effects with other cholinergic drugs",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0018", "topical_ophthalmic_0019", "topical_ophthalmic_0020"],
        "entities_b": ["sys_med_0097", "sys_med_0209", "sys_med_0210"],
        "risk_types": ["pharmacodynamic", "cholinergic"],
        "text": "Ophthalmic cholinergic miotics (pilocarpine, carbachol, ecothiopate) can cause systemic "
                "cholinergic effects: bradycardia, hypersalivation, bronchospasm, and increased GI motility. "
                "Concurrent use with other cholinergic drugs (donepezil, rivastigmine for Alzheimer's) may "
                "produce additive cholinergic toxicity. Ecothiopate (irreversible AChE inhibitor) carries "
                "highest risk. Avoid in patients with asthma, bradycardia, or GI obstruction.",
        "url": "", "weight": 2,
    })
    chunks.append({
        "evidence_id": next_id(), "title": "Pilocarpine interaction with beta-blockers",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0018"],
        "entities_b": ["sys_med_0001", "sys_med_0002", "sys_med_0003"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Pilocarpine can cause bradycardia via muscarinic receptor activation. Combined use with "
                "beta-blockers may produce additive or synergistic bradycardia. Monitor heart rate.",
        "url": "", "weight": 1,
    })

    # ===== 13. LOCAL ANESTHETICS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Ophthalmic local anesthetics: systemic effects",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0079", "topical_ophthalmic_0080",
                        "topical_ophthalmic_0081", "topical_ophthalmic_0082"],
        "entities_b": ["sys_med_0044", "sys_med_0072", "sys_med_0105"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Topical ophthalmic anesthetics (proparacaine, tetracaine, lidocaine, benoxinate) have minimal "
                "systemic absorption with short application. However, repeated or excessive use can lead to "
                "systemic levels causing CNS and cardiac effects. Additive effects with antiarrhythmics "
                "(amiodarone, flecainide) are theoretical but warrant caution in susceptible patients.",
        "url": "", "weight": 1,
    })

    # ===== 14. ANTI-VEGF SYSTEMIC EFFECTS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Intravitreal anti-VEGF and systemic anticoagulation",
        "source": "PubMed / FDA Label", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0086", "topical_ophthalmic_0087",
                        "topical_ophthalmic_0088", "topical_ophthalmic_0089",
                        "topical_ophthalmic_0090", "topical_ophthalmic_0113"],
        "entities_b": ["sys_med_0027", "sys_med_0028", "sys_med_0029",
                        "sys_med_0031", "sys_med_0032", "sys_med_0033"],
        "risk_types": ["pharmacodynamic", "hemorrhagic"],
        "text": "Intravitreal anti-VEGF injections (ranibizumab, aflibercept, bevacizumab, conbercept) carry a "
                "known risk of intraocular hemorrhage, typically self-limiting. Concurrent use of anticoagulants "
                "or antiplatelets does not significantly increase the risk of serious hemorrhagic complications "
                "based on large retrospective studies. Continuation of anticoagulation is generally recommended "
                "during anti-VEGF therapy as the CV risk of stopping anticoagulation outweighs the ocular risk.",
        "url": "", "weight": 2,
    })

    # ===== 15. SYSTEMIC ABSORPTION GENERAL =====
    chunks.append({
        "evidence_id": next_id(), "title": "Systemic absorption of topical ophthalmic drugs: mechanisms and modifiers",
        "source": "Cardiology in Review 2024 / Textbook", "source_type": "literature", "evidence_level": "A",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0001", "topical_ophthalmic_0003", "topical_ophthalmic_0012",
                        "topical_ophthalmic_0073", "topical_ophthalmic_0051", "topical_ophthalmic_0014"],
        "entities_b": [],
        "risk_types": ["pharmacokinetic", "systemic_absorption"],
        "text": "34-80% of topically applied ophthalmic dose enters systemic circulation via nasolacrimal duct "
                "drainage through nasal mucosa. Absorption occurs through conjunctival blood vessels and nasal "
                "mucosa. Factors increasing absorption: large drop volume, low viscosity, punctal occlusion not used. "
                "Factors reducing absorption: punctal occlusion (60% reduction), eye closure, gel formulations, "
                "proper instillation technique. Drug classes with highest systemic absorption: beta-blockers "
                "(timolol ~80%), anticholinergics (atropine), brimonidine, CAIs.",
        "url": "", "weight": 3,
    })

    # ===== 16. FLUOROQUINOLONE + CORTICOSTEROID COMBINATIONS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Antibiotic-corticosteroid fixed combinations: dual mechanism coverage",
        "source": "FDA Label / DrugBank", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0099", "topical_ophthalmic_0100", "topical_ophthalmic_0102"],
        "entities_b": ["sys_med_0027", "sys_med_0031", "sys_med_0055", "sys_med_0056"],
        "risk_types": ["pharmacodynamic", "hemorrhagic_steroid"],
        "text": "Fixed-combination ophthalmic preparations containing both antibiotic and corticosteroid "
                "(TobraDex, Maxitrol) combine the interaction profiles of both components: NSAID-like bleeding "
                "risk is not applicable, but corticosteroid IOP elevation risk applies. See individual component "
                "monographs for interaction details. Systemic absorption is low but cumulative corticosteroid "
                "effect may be significant with prolonged use.",
        "url": "", "weight": 1,
    })

    # ===== 17. ANTISEPTICS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Povidone-iodine ophthalmic: thyroid interaction",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0103"],
        "entities_b": ["sys_med_0066", "sys_med_0200"],
        "risk_types": ["pharmacodynamic", "thyroid"],
        "text": "Povidone-iodine ophthalmic solution releases free iodine that can be absorbed through the "
                "cornea and conjunctiva. In patients with thyroid disorders (on levothyroxine or methimazole), "
                "repeated exposure to iodine could theoretically affect thyroid function. Single-use preoperative "
                "application is safe. Caution with repeated daily use in thyroid disease patients.",
        "url": "", "weight": 1,
    })

    # ===== 18. MITOMYCIN C =====
    chunks.append({
        "evidence_id": next_id(), "title": "Mitomycin C ophthalmic: systemic toxicity risk with other alkylating agents",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0107"],
        "entities_b": ["sys_med_0058", "sys_med_0155"],
        "risk_types": ["pharmacodynamic", "toxicity"],
        "text": "Mitomycin C used during glaucoma surgery is applied topically to the surgical site with minimal "
                "systemic absorption. However, concurrent use with other myelosuppressive agents (methotrexate, "
                "cyclophosphamide) could theoretically increase bone marrow suppression risk. Standard intraoperative "
                "application is safe without dose adjustment.",
        "url": "", "weight": 1,
    })

    # ===== 19. ALLERGY EYE DROPS INTERACTIONS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Antihistamine/mast cell stabilizer ophthalmic: interactions",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0063", "topical_ophthalmic_0064", "topical_ophthalmic_0065",
                        "topical_ophthalmic_0066", "topical_ophthalmic_0067", "topical_ophthalmic_0068",
                        "topical_ophthalmic_0069", "topical_ophthalmic_0070",
                        "topical_ophthalmic_0071", "topical_ophthalmic_0072"],
        "entities_b": ["sys_med_0087", "sys_med_0088", "sys_med_0069"],
        "risk_types": ["pharmacodynamic", "antihistamine"],
        "text": "Topical ophthalmic antihistamines (olopatadine, ketotifen, epinastine, azelastine, bepotastine, "
                "alcaftadine) are generally well-tolerated with minimal systemic absorption (<5%). Additive "
                "sedation with systemic antihistamines (diphenhydramine, cetirizine) is not expected at "
                "ophthalmic doses. Mast cell stabilizers (cromolyn, nedocromil, lodoxamide) have no known "
                "systemic drug interactions due to negligible absorption.",
        "url": "", "weight": 1,
    })

    # ===== 20. CYCLOPLEGICS IN CHILDREN =====
    chunks.append({
        "evidence_id": next_id(), "title": "Pediatric cycloplegia: systemic anticholinergic toxicity",
        "source": "PubMed / FDA Label", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0073", "topical_ophthalmic_0074"],
        "entities_b": ["sys_med_0069", "sys_med_0211"],
        "risk_types": ["pharmacodynamic", "anticholinergic"],
        "text": "Children are especially sensitive to systemic anticholinergic effects from ophthalmic cycloplegics. "
                "Cyclopentolate 1% can cause CNS disturbances including ataxia, incoherent speech, and visual "
                "hallucinations. Both atropine and cyclopentolate can cause hyperthermia, flushing, and tachycardia. "
                "Use with other anticholinergics (diphenhydramine, memantine) may exacerbate these effects. "
                "Use lowest effective concentration in children.",
        "url": "", "weight": 2,
    })

    # ===== 21. ANTIMETABOLITE + ANTIFIBROTIC =====
    chunks.append({
        "evidence_id": next_id(), "title": "5-FU ophthalmic: potential interaction with warfarin",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0108"],
        "entities_b": ["sys_med_0027"],
        "risk_types": ["pharmacokinetic", "anticoagulation"],
        "text": "Systemic 5-fluorouracil is known to increase warfarin effect via CYP2C9 inhibition. While "
                "ophthalmic 5-FU is applied at very low doses (subconjunctival) for glaucoma surgery, theoretical "
                "risk of INR elevation exists. Monitor INR if high-dose or repeated subconjunctival 5-FU is used "
                "in patients on warfarin.",
        "url": "", "weight": 1,
    })

    # ===== 22. CONTRAST DYES =====
    chunks.append({
        "evidence_id": next_id(), "title": "Ophthalmic diagnostic dyes: allergic and interaction profile",
        "source": "DrugBank / PubMed", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0083", "topical_ophthalmic_0084"],
        "entities_b": ["sys_med_0069"],
        "risk_types": ["pharmacodynamic", "allergic"],
        "text": "Fluorescein injection can cause nausea, vomiting, and rarely anaphylaxis. Antihistamine "
                "premedication may mask early allergic symptoms. Indocyanine green contains iodine and should "
                "be used with caution in patients with shellfish/iodine allergy (theoretical).",
        "url": "", "weight": 1,
    })

    # ===== 23. COMBINATION PRODUCT PK =====
    chunks.append({
        "evidence_id": next_id(), "title": "Fixed-combination glaucoma drugs: systemic absorption considerations",
        "source": "FDA Label / DrugBank", "source_type": "regulatory", "evidence_level": "B",
        "evidence_relation": "pharmacokinetic",
        "entities_a": ["topical_ophthalmic_0021", "topical_ophthalmic_0022", "topical_ophthalmic_0023",
                        "topical_ophthalmic_0024", "topical_ophthalmic_0025",
                        "topical_ophthalmic_0026", "topical_ophthalmic_0027", "topical_ophthalmic_0028"],
        "entities_b": ["sys_med_0001", "sys_med_0002", "sys_med_0003",
                        "sys_med_0022", "sys_med_0023"],
        "risk_types": ["pharmacokinetic", "systemic_absorption"],
        "text": "Fixed-combination glaucoma drugs contain two active ingredients (e.g., timolol + latanoprost, "
                "brimonidine + brinzolamide). The systemic absorption profile reflects both components. "
                "Timolol-containing combinations carry beta-blocker systemic risks. CAI-containing combinations "
                "carry metabolic acidosis risk with diuretics. Brimonidine combinations carry CNS depression risk.",
        "url": "", "weight": 2,
    })

    # ===== 24. HYPEROSMOTICS =====
    chunks.append({
        "evidence_id": next_id(), "title": "Ophthalmic hyperosmotics: no significant systemic DDI",
        "source": "DrugBank", "source_type": "literature", "evidence_level": "C",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0105", "topical_ophthalmic_0106"],
        "entities_b": ["sys_med_0022", "sys_med_0023"],
        "risk_types": ["pharmacodynamic", "electrolyte"],
        "text": "Topical hyperosmotic agents (sodium chloride 5%, glycerin) draw water from corneal epithelium "
                "via osmosis. Systemic absorption is minimal. No clinically significant drug interactions "
                "are known. Theoretical electrolyte disturbance with chronic use in patients on diuretics "
                "is not clinically relevant.",
        "url": "", "weight": 1,
    })

    # ===== 25. ANTIHYPERTENSIVE MECHANISM SUMMARY =====
    chunks.append({
        "evidence_id": next_id(), "title": "Anti-VEGF systemic vascular effects",
        "source": "PubMed", "source_type": "literature", "evidence_level": "B",
        "evidence_relation": "pharmacodynamic",
        "entities_a": ["topical_ophthalmic_0086", "topical_ophthalmic_0087", "topical_ophthalmic_0088"],
        "entities_b": ["sys_med_0027", "sys_med_0031", "sys_med_0009", "sys_med_0014", "sys_med_0018"],
        "risk_types": ["pharmacodynamic", "cardiovascular"],
        "text": "Intravitreal anti-VEGF agents can enter the systemic circulation in small amounts and transiently "
                "reduce plasma VEGF levels. This has been associated with a small increase in arterial "
                "thromboembolic events in some meta-analyses. Patients with recent stroke or MI should be "
                "evaluated carefully. However, the systemic safety profile of intravitreal anti-VEGF is favorable "
                "and concurrent CV medication (anticoagulants, antiplatelets, antihypertensives) can continue.",
        "url": "", "weight": 2,
    })

    print(f"[evidence] Generated {len(chunks)} evidence chunks")
    return chunks


def main() -> None:
    seed_dir = PROJECT_ROOT / "data" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    path = seed_dir / "evidence_chunks.jsonl"
    chunks = generate()
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"[evidence] Wrote {len(chunks)} chunks to {path}")


if __name__ == "__main__":
    main()
