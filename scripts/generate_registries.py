"""
Generate Entity A & B registry CSVs for ophthalmic-ddi-cds project.
"""
from __future__ import annotations

import csv
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_entity_a() -> list[list[str]]:
    return [
        # Glaucoma - Beta Blockers
        ["topical_ophthalmic_0001", "Timolol", "timolol maleate", "glaucoma_beta_blocker", "beta_adrenergic_antagonist", "beta_blocker|systemic_absorption_high|cardiovascular_risk", "DrugBank DB00373, PubMed"],
        ["topical_ophthalmic_0002", "Betaxolol", "betaxolol hydrochloride", "glaucoma_beta_blocker", "beta1_selective_adrenergic_antagonist", "beta_blocker|beta1_selective|systemic_absorption_medium", "DrugBank DB00195, PubMed"],
        ["topical_ophthalmic_0003", "Levobunolol", "levobunolol hydrochloride", "glaucoma_beta_blocker", "non_selective_beta_adrenergic_antagonist", "beta_blocker|systemic_absorption_high", "DrugBank DB01210, PubMed"],
        ["topical_ophthalmic_0004", "Carteolol", "carteolol hydrochloride", "glaucoma_beta_blocker", "beta_adrenergic_antagonist", "beta_blocker|isa_activity|systemic_absorption_high", "DrugBank DB00521, PubMed"],
        ["topical_ophthalmic_0005", "Metipranolol", "metipranolol hydrochloride", "glaucoma_beta_blocker", "non_selective_beta_adrenergic_antagonist", "beta_blocker|systemic_absorption_high", "DrugBank DB01214, PubMed"],
        # Prostaglandin Analogs
        ["topical_ophthalmic_0006", "Latanoprost", "latanoprost", "glaucoma_prostaglandin_analog", "FP_receptor_agonist", "prostaglandin_analog|systemic_absorption_low", "DrugBank DB00654, PubMed"],
        ["topical_ophthalmic_0007", "Travoprost", "travoprost", "glaucoma_prostaglandin_analog", "FP_receptor_agonist", "prostaglandin_analog|systemic_absorption_low", "DrugBank DB00387, PubMed"],
        ["topical_ophthalmic_0008", "Bimatoprost", "bimatoprost", "glaucoma_prostaglandin_analog", "prostamide_FP_receptor_agonist", "prostaglandin_analog|systemic_absorption_low", "DrugBank DB00905, PubMed"],
        ["topical_ophthalmic_0009", "Tafluprost", "tafluprost", "glaucoma_prostaglandin_analog", "FP_receptor_agonist", "prostaglandin_analog|systemic_absorption_low", "DrugBank DB08866, PubMed"],
        ["topical_ophthalmic_0010", "Latanoprostene bunod", "latanoprostene bunod", "glaucoma_prostaglandin_analog", "FP_receptor_agonist_nitric_oxide_donating", "prostaglandin_analog|no_donor|systemic_absorption_low", "DrugBank DB14882, PubMed"],
        ["topical_ophthalmic_0011", "Unoprostone", "unoprostone isopropyl", "glaucoma_prostaglandin_analog", "FP_receptor_agonist", "prostaglandin_analog|systemic_absorption_low", "DrugBank DB06402, PubMed"],
        # Alpha2 Agonists
        ["topical_ophthalmic_0012", "Brimonidine", "brimonidine tartrate", "glaucoma_alpha2_agonist", "alpha2_adrenergic_agonist", "alpha2_agonist|systemic_absorption_medium|cns_depressant", "DrugBank DB00484, PubMed"],
        ["topical_ophthalmic_0013", "Apraclonidine", "apraclonidine hydrochloride", "glaucoma_alpha2_agonist", "alpha2_adrenergic_agonist", "alpha2_agonist|systemic_absorption_medium|cns_depressant", "DrugBank DB00935, PubMed"],
        # CAIs
        ["topical_ophthalmic_0014", "Dorzolamide", "dorzolamide hydrochloride", "glaucoma_cai_topical", "carbonic_anhydrase_inhibitor", "cai_topical|systemic_absorption_medium|metabolic_acidosis_risk", "DrugBank DB00869, PubMed"],
        ["topical_ophthalmic_0015", "Brinzolamide", "brinzolamide", "glaucoma_cai_topical", "carbonic_anhydrase_inhibitor", "cai_topical|systemic_absorption_medium|metabolic_acidosis_risk", "DrugBank DB01194, PubMed"],
        # ROCK Inhibitors
        ["topical_ophthalmic_0016", "Netarsudil", "netarsudil dimesylate", "glaucoma_rock_inhibitor", "rho_associated_protein_kinase_inhibitor", "rock_inhibitor|systemic_absorption_low", "DrugBank DB13931, PubMed"],
        ["topical_ophthalmic_0017", "Ripasudil", "ripasudil hydrochloride hydrate", "glaucoma_rock_inhibitor", "rho_associated_protein_kinase_inhibitor", "rock_inhibitor|systemic_absorption_low", "DrugBank DB16487, PubMed"],
        # Miotics
        ["topical_ophthalmic_0018", "Pilocarpine", "pilocarpine hydrochloride", "glaucoma_miotic", "muscarinic_receptor_agonist", "miotic|systemic_absorption_medium|cholinergic", "DrugBank DB01085, PubMed"],
        ["topical_ophthalmic_0019", "Carbachol", "carbachol", "glaucoma_miotic", "cholinergic_agonist", "miotic|systemic_absorption_medium|cholinergic", "DrugBank DB00411, PubMed"],
        ["topical_ophthalmic_0020", "Ecothiopate", "ecothiopate iodide", "glaucoma_miotic", "irreversible_acetylcholinesterase_inhibitor", "miotic|systemic_absorption_high|cholinergic_crisis_risk", "DrugBank DB01057, PubMed"],
        # Fixed Combinations
        ["topical_ophthalmic_0021", "Timolol/Latanoprost", "Timolol+Latanoprost fixed combination", "glaucoma_fixed_combination", "beta_blocker+FP_agonist", "beta_blocker|prostaglandin_analog|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0022", "Timolol/Travoprost", "Timolol+Travoprost fixed combination", "glaucoma_fixed_combination", "beta_blocker+FP_agonist", "beta_blocker|prostaglandin_analog|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0023", "Timolol/Bimatoprost", "Timolol+Bimatoprost fixed combination", "glaucoma_fixed_combination", "beta_blocker+prostamide_agonist", "beta_blocker|prostaglandin_analog|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0024", "Timolol/Brimonidine", "Timolol+Brimonidine fixed combination", "glaucoma_fixed_combination", "beta_blocker+alpha2_agonist", "beta_blocker|alpha2_agonist|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0025", "Timolol/Dorzolamide", "Timolol+Dorzolamide fixed combination", "glaucoma_fixed_combination", "beta_blocker+CAI", "beta_blocker|cai|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0026", "Brimonidine/Brinzolamide", "Brimonidine+Brinzolamide fixed combination", "glaucoma_fixed_combination", "alpha2_agonist+CAI", "alpha2_agonist|cai|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0027", "Brimonidine/Dorzolamide", "Brimonidine+Dorzolamide fixed combination", "glaucoma_fixed_combination", "alpha2_agonist+CAI", "alpha2_agonist|cai|systemic_absorption_medium", "PubMed"],
        ["topical_ophthalmic_0028", "Netarsudil/Latanoprost", "Netarsudil+Latanoprost fixed combination", "glaucoma_fixed_combination", "ROCK_inhibitor+FP_agonist", "rock_inhibitor|prostaglandin_analog|systemic_absorption_low", "PubMed"],
        # Fluoroquinolones
        ["topical_ophthalmic_0029", "Ofloxacin", "ofloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB01165, PubMed"],
        ["topical_ophthalmic_0030", "Levofloxacin", "levofloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB01137, PubMed"],
        ["topical_ophthalmic_0031", "Moxifloxacin", "moxifloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB00218, PubMed"],
        ["topical_ophthalmic_0032", "Gatifloxacin", "gatifloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB01044, PubMed"],
        ["topical_ophthalmic_0033", "Ciprofloxacin", "ciprofloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB00537, PubMed"],
        ["topical_ophthalmic_0034", "Besifloxacin", "besifloxacin ophthalmic", "antibiotic_fluoroquinolone", "DNA_gyrase_inhibitor_topoisomerase_IV_inhibitor", "antibiotic|fluoroquinolone|systemic_absorption_low", "DrugBank DB06771, PubMed"],
        # Aminoglycosides
        ["topical_ophthalmic_0035", "Tobramycin", "tobramycin ophthalmic", "antibiotic_aminoglycoside", "30S_ribosomal_inhibitor", "antibiotic|aminoglycoside|systemic_absorption_low", "DrugBank DB00684, PubMed"],
        ["topical_ophthalmic_0036", "Gentamicin", "gentamicin sulfate ophthalmic", "antibiotic_aminoglycoside", "30S_ribosomal_inhibitor", "antibiotic|aminoglycoside|systemic_absorption_low", "DrugBank DB00798, PubMed"],
        ["topical_ophthalmic_0037", "Neomycin", "neomycin sulfate ophthalmic", "antibiotic_aminoglycoside", "30S_ribosomal_inhibitor", "antibiotic|aminoglycoside|systemic_absorption_low", "DrugBank DB00994, PubMed"],
        # Macrolides
        ["topical_ophthalmic_0038", "Erythromycin", "erythromycin ophthalmic", "antibiotic_macrolide", "50S_ribosomal_inhibitor", "antibiotic|macrolide|systemic_absorption_low", "DrugBank DB00199, PubMed"],
        ["topical_ophthalmic_0039", "Azithromycin", "azithromycin ophthalmic", "antibiotic_macrolide", "50S_ribosomal_inhibitor", "antibiotic|macrolide|systemic_absorption_low", "DrugBank DB00207, PubMed"],
        # Other Antibiotics
        ["topical_ophthalmic_0040", "Chloramphenicol", "chloramphenicol ophthalmic", "antibiotic_other", "50S_ribosomal_inhibitor", "antibiotic|systemic_absorption_low|bone_marrow_suppression_risk", "DrugBank DB00446, PubMed"],
        ["topical_ophthalmic_0041", "Fusidic acid", "fusidic acid ophthalmic", "antibiotic_other", "protein_synthesis_inhibitor", "antibiotic|systemic_absorption_low", "DrugBank DB02703, PubMed"],
        ["topical_ophthalmic_0042", "Bacitracin", "bacitracin ophthalmic", "antibiotic_polypeptide", "cell_wall_synthesis_inhibitor", "antibiotic|systemic_absorption_very_low", "DrugBank DB00626, PubMed"],
        ["topical_ophthalmic_0043", "Polymyxin B", "polymyxin B sulfate ophthalmic", "antibiotic_polypeptide", "cell_membrane_disruptor", "antibiotic|systemic_absorption_very_low", "DrugBank DB00781, PubMed"],
        ["topical_ophthalmic_0044", "Sulfacetamide", "sulfacetamide sodium ophthalmic", "antibiotic_sulfonamide", "dihydropteroate_synthase_inhibitor", "antibiotic|sulfonamide|systemic_absorption_low", "DrugBank DB00634, PubMed"],
        # Antivirals
        ["topical_ophthalmic_0045", "Acyclovir", "acyclovir ophthalmic", "antiviral", "viral_DNA_polymerase_inhibitor", "antiviral|systemic_absorption_low", "DrugBank DB00787, PubMed"],
        ["topical_ophthalmic_0046", "Ganciclovir", "ganciclovir ophthalmic gel", "antiviral", "viral_DNA_polymerase_inhibitor", "antiviral|systemic_absorption_low", "DrugBank DB01004, PubMed"],
        ["topical_ophthalmic_0047", "Trifluridine", "trifluridine ophthalmic", "antiviral", "viral_DNA_polymerase_inhibitor", "antiviral|systemic_absorption_low", "DrugBank DB00432, PubMed"],
        # Antifungals
        ["topical_ophthalmic_0048", "Natamycin", "natamycin ophthalmic", "antifungal", "polyene_macrolide_fungicide", "antifungal|polyene|systemic_absorption_very_low", "DrugBank DB00826, PubMed"],
        ["topical_ophthalmic_0049", "Voriconazole", "voriconazole ophthalmic", "antifungal", "cyp51_inhibitor", "antifungal|azole|systemic_absorption_low", "DrugBank DB00582, PubMed"],
        ["topical_ophthalmic_0050", "Fluconazole", "fluconazole ophthalmic", "antifungal", "cyp51_inhibitor", "antifungal|azole|systemic_absorption_low", "DrugBank DB00196, PubMed"],
        # Corticosteroids
        ["topical_ophthalmic_0051", "Prednisolone", "prednisolone acetate ophthalmic", "corticosteroid", "glucocorticoid_receptor_agonist", "corticosteroid|systemic_absorption_medium|iop_elevation_risk", "DrugBank DB00860, PubMed"],
        ["topical_ophthalmic_0052", "Dexamethasone", "dexamethasone ophthalmic", "corticosteroid", "glucocorticoid_receptor_agonist", "corticosteroid|systemic_absorption_medium|iop_elevation_risk", "DrugBank DB01234, PubMed"],
        ["topical_ophthalmic_0053", "Fluorometholone", "fluorometholone ophthalmic", "corticosteroid", "glucocorticoid_receptor_agonist", "corticosteroid|systemic_absorption_medium|iop_elevation_risk", "DrugBank DB00324, PubMed"],
        ["topical_ophthalmic_0054", "Loteprednol", "loteprednol etabonate ophthalmic", "corticosteroid", "glucocorticoid_receptor_agonist", "corticosteroid|site_activated|systemic_absorption_low|iop_elevation_lower_risk", "DrugBank DB01173, PubMed"],
        ["topical_ophthalmic_0055", "Rimexolone", "rimexolone ophthalmic", "corticosteroid", "glucocorticoid_receptor_agonist", "corticosteroid|systemic_absorption_medium|iop_elevation_risk", "DrugBank DB00886, PubMed"],
        # NSAIDs
        ["topical_ophthalmic_0056", "Ketorolac", "ketorolac tromethamine ophthalmic", "nsaid_ophthalmic", "cox1_cox2_inhibitor", "nsaid|cox_inhibitor|systemic_absorption_low", "DrugBank DB00465, PubMed"],
        ["topical_ophthalmic_0057", "Flurbiprofen", "flurbiprofen sodium ophthalmic", "nsaid_ophthalmic", "cox_inhibitor", "nsaid|cox_inhibitor|systemic_absorption_low", "DrugBank DB00712, PubMed"],
        ["topical_ophthalmic_0058", "Diclofenac", "diclofenac sodium ophthalmic", "nsaid_ophthalmic", "cox1_cox2_inhibitor", "nsaid|cox_inhibitor|systemic_absorption_low", "DrugBank DB00586, PubMed"],
        ["topical_ophthalmic_0059", "Bromfenac", "bromfenac sodium ophthalmic", "nsaid_ophthalmic", "cox_inhibitor", "nsaid|cox_inhibitor|systemic_absorption_low", "DrugBank DB00963, PubMed"],
        ["topical_ophthalmic_0060", "Nepafenac", "nepafenac ophthalmic", "nsaid_ophthalmic", "cox_inhibitor_prodrug", "nsaid|cox_inhibitor|prodrug|systemic_absorption_low", "DrugBank DB01283, PubMed"],
        # Immunosuppressants
        ["topical_ophthalmic_0061", "Cyclosporine", "cyclosporine A ophthalmic", "immunosuppressant", "calcineurin_inhibitor", "immunosuppressant|calcineurin_inhibitor|systemic_absorption_very_low", "DrugBank DB00091, PubMed"],
        ["topical_ophthalmic_0062", "Tacrolimus", "tacrolimus ophthalmic", "immunosuppressant", "calcineurin_inhibitor", "immunosuppressant|calcineurin_inhibitor|systemic_absorption_low", "DrugBank DB00800, PubMed"],
        # Antihistamines
        ["topical_ophthalmic_0063", "Olopatadine", "olopatadine hydrochloride ophthalmic", "antihistamine_dual_action", "h1_receptor_antagonist_mast_cell_stabilizer", "antihistamine|mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00768, PubMed"],
        ["topical_ophthalmic_0064", "Ketotifen", "ketotifen fumarate ophthalmic", "antihistamine_mast_cell_stabilizer", "h1_receptor_antagonist_mast_cell_stabilizer", "antihistamine|mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00920, PubMed"],
        ["topical_ophthalmic_0065", "Epinastine", "epinastine hydrochloride ophthalmic", "antihistamine_dual_action", "h1_receptor_antagonist_mast_cell_stabilizer", "antihistamine|mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00751, PubMed"],
        ["topical_ophthalmic_0066", "Azelastine", "azelastine hydrochloride ophthalmic", "antihistamine", "h1_receptor_antagonist", "antihistamine|systemic_absorption_low", "DrugBank DB00972, PubMed"],
        ["topical_ophthalmic_0067", "Emedastine", "emedastine difumarate ophthalmic", "antihistamine", "h1_receptor_antagonist", "antihistamine|systemic_absorption_low", "DrugBank DB01093, PubMed"],
        ["topical_ophthalmic_0068", "Bepotastine", "bepotastine besilate ophthalmic", "antihistamine", "h1_receptor_antagonist", "antihistamine|systemic_absorption_low", "DrugBank DB04935, PubMed"],
        ["topical_ophthalmic_0069", "Alcaftadine", "alcaftadine ophthalmic", "antihistamine", "h1_receptor_antagonist", "antihistamine|systemic_absorption_low", "DrugBank DB08883, PubMed"],
        # Mast Cell Stabilizers
        ["topical_ophthalmic_0070", "Cromolyn sodium", "cromoglycate ophthalmic", "mast_cell_stabilizer", "mast_cell_stabilizer", "mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00186, PubMed"],
        ["topical_ophthalmic_0071", "Nedocromil", "nedocromil sodium ophthalmic", "mast_cell_stabilizer", "mast_cell_stabilizer", "mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00716, PubMed"],
        ["topical_ophthalmic_0072", "Lodoxamide", "lodoxamide tromethamine ophthalmic", "mast_cell_stabilizer", "mast_cell_stabilizer", "mast_cell_stabilizer|systemic_absorption_low", "DrugBank DB00484, PubMed"],
        # Mydriatics / Cycloplegics
        ["topical_ophthalmic_0073", "Atropine", "atropine sulfate ophthalmic", "mydriatic_cycloplegic", "muscarinic_receptor_antagonist", "anticholinergic|mydriatic|systemic_absorption_medium", "DrugBank DB00572, PubMed"],
        ["topical_ophthalmic_0074", "Cyclopentolate", "cyclopentolate hydrochloride ophthalmic", "mydriatic_cycloplegic", "muscarinic_receptor_antagonist", "anticholinergic|mydriatic|systemic_absorption_medium", "DrugBank DB00979, PubMed"],
        ["topical_ophthalmic_0075", "Homatropine", "homatropine hydrobromide ophthalmic", "mydriatic_cycloplegic", "muscarinic_receptor_antagonist", "anticholinergic|mydriatic|systemic_absorption_medium", "DrugBank DB00725, PubMed"],
        ["topical_ophthalmic_0076", "Scopolamine", "scopolamine hydrobromide ophthalmic", "mydriatic_cycloplegic", "muscarinic_receptor_antagonist", "anticholinergic|mydriatic|systemic_absorption_high", "DrugBank DB00747, PubMed"],
        ["topical_ophthalmic_0077", "Tropicamide", "tropicamide ophthalmic", "mydriatic_cycloplegic", "muscarinic_receptor_antagonist", "anticholinergic|mydriatic|systemic_absorption_low", "DrugBank DB00809, PubMed"],
        ["topical_ophthalmic_0078", "Phenylephrine", "phenylephrine hydrochloride ophthalmic", "mydriatic", "alpha1_adrenergic_agonist", "sympathomimetic|mydriatic|systemic_absorption_medium|hypertension_risk", "DrugBank DB00388, PubMed"],
        # Anesthetics
        ["topical_ophthalmic_0079", "Proparacaine", "proparacaine hydrochloride ophthalmic", "anesthetic_topical", "sodium_channel_blocker", "anesthetic|systemic_absorption_low", "DrugBank DB01227, PubMed"],
        ["topical_ophthalmic_0080", "Tetracaine", "tetracaine hydrochloride ophthalmic", "anesthetic_topical", "sodium_channel_blocker", "anesthetic|systemic_absorption_low", "DrugBank DB00445, PubMed"],
        ["topical_ophthalmic_0081", "Lidocaine", "lidocaine ophthalmic gel", "anesthetic_topical", "sodium_channel_blocker", "anesthetic|systemic_absorption_low|antiarrhythmic", "DrugBank DB00281, PubMed"],
        ["topical_ophthalmic_0082", "Benoxinate", "benoxinate hydrochloride", "anesthetic_topical", "sodium_channel_blocker", "anesthetic|systemic_absorption_low", "DrugBank DB00807, PubMed"],
        # Diagnostic Dyes
        ["topical_ophthalmic_0083", "Fluorescein", "fluorescein sodium ophthalmic", "diagnostic_dye", "diagnostic_contrast", "diagnostic|dye|systemic_absorption_low", "DrugBank DB00693, PubMed"],
        ["topical_ophthalmic_0084", "Indocyanine green", "ICG ophthalmic", "diagnostic_dye", "diagnostic_contrast", "diagnostic|dye|systemic_absorption_very_low", "DrugBank DB00354, PubMed"],
        ["topical_ophthalmic_0085", "Rose bengal", "rose bengal ophthalmic", "diagnostic_dye", "diagnostic_contrast", "diagnostic|dye|systemic_absorption_very_low", "DrugBank DB00762, PubMed"],
        # Anti-VEGF
        ["topical_ophthalmic_0086", "Ranibizumab", "ranibizumab intravitreal", "anti_vegf_intravitreal", "vegf_a_inhibitor", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "DrugBank DB01276, PubMed"],
        ["topical_ophthalmic_0087", "Aflibercept", "aflibercept intravitreal", "anti_vegf_intravitreal", "vegf_plgf_inhibitor", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "DrugBank DB01661, PubMed"],
        ["topical_ophthalmic_0088", "Bevacizumab", "bevacizumab intravitreal", "anti_vegf_intravitreal", "vegf_a_inhibitor", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "DrugBank DB00112, PubMed"],
        ["topical_ophthalmic_0089", "Brolucizumab", "brolucizumab intravitreal", "anti_vegf_intravitreal", "vegf_a_inhibitor", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "DrugBank DB16546, PubMed"],
        ["topical_ophthalmic_0090", "Faricimab", "faricimab intravitreal", "anti_vegf_intravitreal", "vegf_a_ang2_inhibitor", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "DrugBank DB16647, PubMed"],
        # Decongestants
        ["topical_ophthalmic_0091", "Naphazoline", "naphazoline ophthalmic", "decongestant", "alpha_adrenergic_agonist", "sympathomimetic|vasoconstrictor|systemic_absorption_medium", "DrugBank DB00882, PubMed"],
        ["topical_ophthalmic_0092", "Tetrahydrozoline", "tetrahydrozoline ophthalmic", "decongestant", "alpha_adrenergic_agonist", "sympathomimetic|vasoconstrictor|systemic_absorption_medium", "DrugBank DB00714, PubMed"],
        # Other
        ["topical_ophthalmic_0093", "Dipivefrin", "dipivefrin hydrochloride ophthalmic", "glaucoma_other", "prodrug_of_epinephrine_adrenergic_agonist", "sympathomimetic|prodrug|systemic_absorption_medium", "DrugBank DB00449, PubMed"],
        # === Additions: Dry Eye ===
        ["topical_ophthalmic_0094", "Lifitegrast", "lifitegrast ophthalmic; Xiidra", "dry_eye_anti_inflammatory", "lfa1_icam1_inhibitor", "immunosuppressant|anti_inflammatory|systemic_absorption_very_low", "DrugBank DB11674, PubMed"],
        ["topical_ophthalmic_0095", "Diquafosol", "diquafosol sodium ophthalmic", "dry_eye_mucin_secretagogue", "p2y2_receptor_agonist", "dry_eye|mucin_stimulant|systemic_absorption_low", "DrugBank DB06217, PubMed"],
        ["topical_ophthalmic_0096", "Rebamipide", "rebamipide ophthalmic", "dry_eye_mucin_secretagogue", "mucin_production_stimulator", "dry_eye|mucin_stimulant|systemic_absorption_low", "DrugBank DB11934, PubMed"],
        ["topical_ophthalmic_0097", "Hydroxypropyl cellulose", "hydroxypropyl cellulose ophthalmic insert; Lacrisert", "dry_eye_lubricant_insert", "ocular_lubricant_insert", "dry_eye|artificial_tear_insert|systemic_absorption_none", "DrugBank DB09350, PubMed"],
        ["topical_ophthalmic_0098", "Sodium hyaluronate", "sodium hyaluronate ophthalmic; hyaluronic acid", "dry_eye_lubricant", "viscosupplementation", "dry_eye|artificial_tear|systemic_absorption_none", "DrugBank DB08818, PubMed"],
        # === Additions: Antibiotic+Corticosteroid Combinations ===
        ["topical_ophthalmic_0099", "Tobramycin/Dexamethasone", "TobraDex; tobramycin+dexamethasone ophthalmic", "antibiotic_corticosteroid_combination", "aminoglycoside+glucocorticoid", "antibiotic|aminoglycoside|corticosteroid|systemic_absorption_low", "DrugBank DB00684+DB01234, PubMed"],
        ["topical_ophthalmic_0100", "Neomycin/Polymyxin B/Dexamethasone", "Maxitrol; neomycin+polymyxinB+dexamethasone", "antibiotic_corticosteroid_combination", "aminoglycoside+polypeptide+glucocorticoid", "antibiotic|aminoglycoside|polypeptide|corticosteroid|systemic_absorption_low", "DrugBank DB00994+DB00781+DB01234, PubMed"],
        ["topical_ophthalmic_0101", "Bacitracin/Polymyxin B", "bacitracin+polymyxin B ophthalmic; Polysporin", "antibiotic_combination", "cell_wall_synthesis_inhibitor+cell_membrane_disruptor", "antibiotic|polypeptide|systemic_absorption_very_low", "DrugBank DB00626+DB00781, PubMed"],
        ["topical_ophthalmic_0102", "Sulfacetamide/Prednisolone", "sulfacetamide+prednisolone ophthalmic", "antibiotic_corticosteroid_combination", "dihydropteroate_synthase_inhibitor+glucocorticoid", "antibiotic|sulfonamide|corticosteroid|systemic_absorption_low", "DrugBank DB00634+DB00860, PubMed"],
        # === Additions: Antiseptics ===
        ["topical_ophthalmic_0103", "Povidone-iodine", "povidone-iodine ophthalmic; Betadine", "antiseptic", "iodine_oxidizing_agent_broad_spectrum", "antiseptic|bactericidal_fungicidal_virucidal|systemic_absorption_low", "DrugBank DB14021, PubMed"],
        ["topical_ophthalmic_0104", "Chlorhexidine", "chlorhexidine gluconate ophthalmic", "antiseptic", "cell_membrane_disruptor_broad_spectrum", "antiseptic|bactericidal|systemic_absorption_very_low", "DrugBank DB00878, PubMed"],
        # === Additions: Hyperosmotics ===
        ["topical_ophthalmic_0105", "Sodium chloride 5%", "sodium chloride ophthalmic hypertonic", "hyperosmotic", "osmotic_dehydrating_agent", "hyperosmotic|corneal_edema|systemic_absorption_low", "DrugBank DB14518, PubMed"],
        ["topical_ophthalmic_0106", "Glycerin ophthalmic", "glycerin ophthalmic; glycerol", "hyperosmotic", "osmotic_dehydrating_agent", "hyperosmotic|corneal_edema|systemic_absorption_low", "DrugBank DB02153, PubMed"],
        # === Additions: Antimetabolites (Surgery) ===
        ["topical_ophthalmic_0107", "Mitomycin C", "mitomycin c ophthalmic", "antimetabolite_ophthalmic", "dna_crosslinking_alkylating_agent", "antimetabolite|antifibrotic|systemic_absorption_low", "DrugBank DB00305, PubMed"],
        ["topical_ophthalmic_0108", "5-Fluorouracil", "5-fluorouracil ophthalmic", "antimetabolite_ophthalmic", "thymidylate_synthase_inhibitor", "antimetabolite|antifibrotic|systemic_absorption_low", "DrugBank DB00544, PubMed"],
        # === Additions: Intraocular Surgical Aids ===
        ["topical_ophthalmic_0109", "Acetylcholine intraocular", "acetylcholine chloride intraocular; Miochol", "miotic_intraocular", "cholinergic_agonist_intraocular", "cholinergic|miotic|intraocular|minimal_systemic_absorption", "DrugBank DB03145, PubMed"],
        ["topical_ophthalmic_0110", "Carboxymethylcellulose", "carboxymethylcellulose sodium; Viscoat", "viscoelastic_surgical_aid", "viscoelastic_protective_agent", "viscoelastic|surgical_aid|systemic_absorption_none", "DrugBank DB15897, PubMed"],
        ["topical_ophthalmic_0111", "Hydroxypropyl methylcellulose", "hypromellose ophthalmic; Ocucoat", "viscoelastic_surgical_aid", "viscoelastic_protective_agent", "viscoelastic|surgical_aid|systemic_absorption_none", "DrugBank DB09345, PubMed"],
        # === Additions: Cholinergic Agonist (Glaucoma Alternative) ===
        ["topical_ophthalmic_0112", "Accelidine", "accelidine ophthalmic", "glaucoma_miotic", "muscarinic_receptor_agonist", "miotic|cholinergic|systemic_absorption_medium", "PubMed"],
        # === Additions: Chinese Domestic Anti-VEGF ===
        ["topical_ophthalmic_0113", "Conbercept", "conbercept ophthalmic intravitreal; 康柏西普; Langmu", "anti_vegf_intravitreal", "vegf_plgf_inhibitor_fusion_protein", "anti_vegf|biologic|intravitreal|minimal_systemic_absorption", "PubMed, Chinese FDA"],
    ]


def build_entity_b() -> list[list[str]]:
    return [
        ["sys_med_0001", "Atenolol", "atenolol; tenormin", "beta_blocker_systemic", "beta1_selective_blocker", "CYP2D6", "", "medium", "DrugBank DB00335"],
        ["sys_med_0002", "Metoprolol", "metoprolol tartrate; metoprolol succinate", "beta_blocker_systemic", "beta1_selective_blocker|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB00264"],
        ["sys_med_0003", "Propranolol", "propranolol hydrochloride", "beta_blocker_systemic", "non_selective_beta_blocker|cyp1a2_substrate|cyp2d6_substrate", "CYP1A2, CYP2D6", "", "medium", "DrugBank DB00571"],
        ["sys_med_0004", "Bisoprolol", "bisoprolol fumarate", "beta_blocker_systemic", "beta1_selective_blocker", "", "", "medium", "DrugBank DB00612"],
        ["sys_med_0005", "Carvedilol", "carvedilol", "beta_blocker_systemic", "non_selective_beta_blocker_alpha1_blocker|cyp2d6_substrate|cyp2c9_substrate", "CYP2D6, CYP2C9", "", "medium", "DrugBank DB01136"],
        ["sys_med_0006", "Nebivolol", "nebivolol hydrochloride", "beta_blocker_systemic", "beta1_selective_blocker|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB04861"],
        ["sys_med_0007", "Sotalol", "sotalol hydrochloride", "beta_blocker_systemic", "non_selective_beta_blocker_class_iii_antiarrhythmic", "", "", "medium", "DrugBank DB00489"],
        ["sys_med_0008", "Labetalol", "labetalol hydrochloride", "beta_blocker_systemic", "non_selective_beta_blocker_alpha1_blocker", "", "", "medium", "DrugBank DB00598"],
        ["sys_med_0009", "Amlodipine", "amlodipine besylate", "ccb_dihydropyridine", "l_type_calcium_channel_blocker|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00381"],
        ["sys_med_0010", "Nifedipine", "nifedipine", "ccb_dihydropyridine", "l_type_calcium_channel_blocker|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01115"],
        ["sys_med_0011", "Felodipine", "felodipine", "ccb_dihydropyridine", "l_type_calcium_channel_blocker|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01023"],
        ["sys_med_0012", "Diltiazem", "diltiazem hydrochloride", "ccb_non_dihydropyridine", "l_type_calcium_channel_blocker|cyp3a4_inhibitor|p_gp_inhibitor", "CYP3A4", "P-glycoprotein", "medium", "DrugBank DB00343"],
        ["sys_med_0013", "Verapamil", "verapamil hydrochloride", "ccb_non_dihydropyridine", "l_type_calcium_channel_blocker|cyp3a4_inhibitor|p_gp_inhibitor", "CYP3A4", "P-glycoprotein", "medium", "DrugBank DB00661"],
        ["sys_med_0014", "Lisinopril", "lisinopril", "ace_inhibitor", "ace_inhibitor", "", "", "low", "DrugBank DB00722"],
        ["sys_med_0015", "Enalapril", "enalapril maleate", "ace_inhibitor", "ace_inhibitor|prodrug", "", "", "low", "DrugBank DB00584"],
        ["sys_med_0016", "Ramipril", "ramipril", "ace_inhibitor", "ace_inhibitor|prodrug", "", "", "low", "DrugBank DB00178"],
        ["sys_med_0017", "Captopril", "captopril", "ace_inhibitor", "ace_inhibitor", "", "", "low", "DrugBank DB01197"],
        ["sys_med_0018", "Losartan", "losartan potassium", "arb", "angiotensin_ii_receptor_antagonist|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB00678"],
        ["sys_med_0019", "Valsartan", "valsartan", "arb", "angiotensin_ii_receptor_antagonist", "", "", "low", "DrugBank DB00177"],
        ["sys_med_0020", "Irbesartan", "irbesartan", "arb", "angiotensin_ii_receptor_antagonist|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB01029"],
        ["sys_med_0021", "Candesartan", "candesartan cilexetil", "arb", "angiotensin_ii_receptor_antagonist|prodrug", "", "", "low", "DrugBank DB00796"],
        ["sys_med_0022", "Hydrochlorothiazide", "HCTZ; HCT", "thiazide_diuretic", "ncc_inhibitor", "", "", "medium", "DrugBank DB00999"],
        ["sys_med_0023", "Furosemide", "furosemide", "loop_diuretic", "nkcc2_inhibitor", "", "", "medium", "DrugBank DB00695"],
        ["sys_med_0024", "Spironolactone", "spironolactone", "potassium_sparing_diuretic", "mineralocorticoid_receptor_antagonist|cyp3a4_substrate", "CYP3A4", "", "medium", "DrugBank DB00421"],
        ["sys_med_0025", "Bumetanide", "bumetanide", "loop_diuretic", "nkcc2_inhibitor", "", "", "medium", "DrugBank DB00887"],
        ["sys_med_0026", "Eplerenone", "eplerenone", "potassium_sparing_diuretic", "mineralocorticoid_receptor_antagonist|cyp3a4_substrate", "CYP3A4", "", "medium", "DrugBank DB00700"],
        ["sys_med_0027", "Warfarin", "warfarin sodium", "anticoagulant_vitamin_k_antagonist", "vitamin_k_epoxide_reductase_inhibitor|cyp2c9_substrate|narrow_therapeutic_index", "CYP2C9", "", "high", "DrugBank DB00682"],
        ["sys_med_0028", "Apixaban", "apixaban", "anticoagulant_direct_xa_inhibitor", "factor_xa_inhibitor|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB06605"],
        ["sys_med_0029", "Rivaroxaban", "rivaroxaban", "anticoagulant_direct_xa_inhibitor", "factor_xa_inhibitor|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB06228"],
        ["sys_med_0030", "Dabigatran", "dabigatran etexilate", "anticoagulant_direct_thrombin_inhibitor", "thrombin_inhibitor|p_gp_substrate", "", "P-glycoprotein", "low", "DrugBank DB06695"],
        ["sys_med_0031", "Aspirin", "acetylsalicylic acid; ASA", "antiplatelet", "cox1_inhibitor_irreversible", "", "", "low", "DrugBank DB00945"],
        ["sys_med_0032", "Clopidogrel", "clopidogrel bisulfate", "antiplatelet", "p2y12_inhibitor_prodrug|cyp2c19_substrate", "CYP2C19", "", "low", "DrugBank DB00758"],
        ["sys_med_0033", "Ticagrelor", "ticagrelor", "antiplatelet", "p2y12_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB08816"],
        ["sys_med_0034", "Metformin", "metformin hydrochloride", "antidiabetic_biguanide", "ampk_activator", "", "", "low", "DrugBank DB00331"],
        ["sys_med_0035", "Gliclazide", "gliclazide", "antidiabetic_sulfonylurea", "atp_sensitive_k_channel_blocker|cyp2c9_substrate", "CYP2C9", "", "medium", "DrugBank DB01120"],
        ["sys_med_0036", "Glimepiride", "glimepiride", "antidiabetic_sulfonylurea", "atp_sensitive_k_channel_blocker|cyp2c9_substrate", "CYP2C9", "", "medium", "DrugBank DB00222"],
        ["sys_med_0037", "Sitagliptin", "sitagliptin phosphate", "antidiabetic_dpp4_inhibitor", "dpp4_inhibitor", "", "", "low", "DrugBank DB01261"],
        ["sys_med_0038", "Empagliflozin", "empagliflozin", "antidiabetic_sglt2_inhibitor", "sglt2_inhibitor", "", "", "low", "DrugBank DB09038"],
        ["sys_med_0039", "Dapagliflozin", "dapagliflozin propanediol", "antidiabetic_sglt2_inhibitor", "sglt2_inhibitor", "", "", "low", "DrugBank DB06292"],
        ["sys_med_0040", "Semaglutide", "semaglutide", "antidiabetic_glp1_ra", "glp1_receptor_agonist", "", "", "low", "DrugBank DB13928"],
        ["sys_med_0041", "Atorvastatin", "atorvastatin calcium", "statin", "hmg_coa_reductase_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01076"],
        ["sys_med_0042", "Rosuvastatin", "rosuvastatin calcium", "statin", "hmg_coa_reductase_inhibitor", "", "", "low", "DrugBank DB01098"],
        ["sys_med_0043", "Simvastatin", "simvastatin", "statin", "hmg_coa_reductase_inhibitor_prodrug|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00641"],
        ["sys_med_0044", "Amiodarone", "amiodarone hydrochloride", "antiarrhythmic_class_iii", "k_channel_blocker|cyp3a4_inhibitor|cyp2c9_inhibitor|cyp2d6_inhibitor", "CYP3A4, CYP2C9, CYP2D6", "", "high", "DrugBank DB01118"],
        ["sys_med_0045", "Digoxin", "digoxin", "cardiac_glycoside", "na_k_atpase_inhibitor|p_gp_substrate|narrow_therapeutic_index", "", "P-glycoprotein", "high", "DrugBank DB00390"],
        ["sys_med_0046", "Fluoxetine", "fluoxetine hydrochloride", "antidepressant_ssri", "sert_inhibitor|cyp2d6_inhibitor|cyp2c9_inhibitor", "CYP2D6, CYP2C9", "", "low", "DrugBank DB00472"],
        ["sys_med_0047", "Sertraline", "sertraline hydrochloride", "antidepressant_ssri", "sert_inhibitor", "", "", "low", "DrugBank DB01104"],
        ["sys_med_0048", "Citalopram", "citalopram hydrobromide", "antidepressant_ssri", "sert_inhibitor|cyp2c19_substrate|cyp3a4_substrate", "CYP2C19, CYP3A4", "", "low", "DrugBank DB00215"],
        ["sys_med_0049", "Carbamazepine", "carbamazepine", "antiepileptic", "na_channel_blocker|cyp3a4_inducer|cyp2c9_inducer|cyp1a2_inducer", "CYP3A4, CYP2C9, CYP1A2", "", "medium", "DrugBank DB00564"],
        ["sys_med_0050", "Valproic acid", "valproate; sodium valproate", "antiepileptic", "gaba_ergic|cyp2c9_inhibitor|cyp2c19_inhibitor", "CYP2C9, CYP2C19", "", "medium", "DrugBank DB00313"],
        ["sys_med_0051", "Phenytoin", "phenytoin sodium", "antiepileptic", "na_channel_blocker|cyp2c9_substrate|cyp3a4_inducer|cyp2c9_inducer", "CYP2C9, CYP3A4", "", "high", "DrugBank DB00252"],
        ["sys_med_0052", "Ibuprofen", "ibuprofen", "nsaid_systemic", "cox1_cox2_inhibitor", "", "", "low", "DrugBank DB01050"],
        ["sys_med_0053", "Naproxen", "naproxen sodium", "nsaid_systemic", "cox1_cox2_inhibitor|cyp1a2_substrate|cyp2c9_substrate", "CYP1A2, CYP2C9", "", "low", "DrugBank DB00788"],
        ["sys_med_0054", "Celecoxib", "celecoxib", "nsaid_systemic", "cox2_inhibitor|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB00482"],
        ["sys_med_0055", "Prednisone", "prednisone systemic", "corticosteroid_systemic", "glucocorticoid_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00635"],
        ["sys_med_0056", "Methylprednisolone", "methylprednisolone systemic", "corticosteroid_systemic", "glucocorticoid_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00959"],
        ["sys_med_0057", "Dexamethasone systemic", "dexamethasone systemic", "corticosteroid_systemic", "glucocorticoid_receptor_agonist|cyp3a4_substrate|cyp3a4_inducer", "CYP3A4", "", "low", "DrugBank DB01234"],
        ["sys_med_0058", "Methotrexate", "methotrexate", "immunosuppressant_systemic", "dhfr_inhibitor|narrow_therapeutic_index", "", "", "high", "DrugBank DB00563"],
        ["sys_med_0059", "Cyclosporine systemic", "cyclosporine A systemic", "immunosuppressant_systemic", "calcineurin_inhibitor|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "medium", "DrugBank DB00091"],
        ["sys_med_0060", "Tacrolimus systemic", "tacrolimus systemic", "immunosuppressant_systemic", "calcineurin_inhibitor|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "medium", "DrugBank DB00800"],
        ["sys_med_0061", "Clarithromycin", "clarithromycin", "antibiotic_macrolide_systemic", "50S_inhibitor|cyp3a4_inhibitor|p_gp_inhibitor", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB01211"],
        ["sys_med_0062", "Rifampicin", "rifampin; rifampicin", "antibiotic_ansamycin", "rna_polymerase_inhibitor|cyp3a4_inducer|p_gp_inducer", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB01045"],
        ["sys_med_0063", "Fluconazole systemic", "fluconazole systemic", "antifungal_azole_systemic", "cyp51_inhibitor|cyp2c9_inhibitor|cyp2c19_inhibitor", "CYP2C9, CYP2C19", "", "low", "DrugBank DB00196"],
        ["sys_med_0064", "Itraconazole", "itraconazole", "antifungal_azole_systemic", "cyp51_inhibitor|cyp3a4_inhibitor|p_gp_inhibitor", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB01167"],
        ["sys_med_0065", "Omeprazole", "omeprazole", "proton_pump_inhibitor", "h_k_atpase_inhibitor|cyp2c19_inhibitor|cyp3a4_substrate", "CYP2C19, CYP3A4", "", "low", "DrugBank DB00338"],
        ["sys_med_0066", "Levothyroxine", "levothyroxine sodium; T4", "thyroid_hormone", "thyroid_hormone_receptor_agonist", "", "", "medium", "DrugBank DB00451"],
        ["sys_med_0067", "Salbutamol", "albuterol; salbutamol", "respiratory_beta2_agonist", "beta2_adrenergic_agonist", "", "", "low", "DrugBank DB01001"],
        ["sys_med_0068", "Fluticasone", "fluticasone propionate", "respiratory_corticosteroid", "glucocorticoid_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00588"],
        ["sys_med_0069", "Diphenhydramine", "diphenhydramine hydrochloride", "antihistamine_systemic", "h1_receptor_antagonist|cyp2d6_substrate", "CYP2D6", "", "low", "DrugBank DB01075"],
        ["sys_med_0070", "Fentanyl", "fentanyl", "opioid", "mu_opioid_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "medium", "DrugBank DB00813"],
        ["sys_med_0071", "Morphine", "morphine sulfate", "opioid", "mu_opioid_receptor_agonist|ugt2b7_substrate", "", "", "medium", "DrugBank DB00295"],
        ["sys_med_0072", "Oxycodone", "oxycodone hydrochloride", "opioid", "mu_opioid_receptor_agonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "medium", "DrugBank DB00497"],
        ["sys_med_0073", "Colchicine", "colchicine", "anti_gout", "tubulin_inhibitor|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "high", "DrugBank DB01394"],
        ["sys_med_0074", "Allopurinol", "allopurinol", "anti_gout", "xanthine_oxidase_inhibitor", "", "", "low", "DrugBank DB00437"],
        ["sys_med_0075", "Lithium", "lithium carbonate", "mood_stabilizer", "inositol_monophosphatase_inhibitor|narrow_therapeutic_index", "", "", "high", "DrugBank DB01356"],
        ["sys_med_0076", "Metronidazole", "metronidazole", "antibiotic_nitroimidazole", "dna_damaging", "", "", "low", "DrugBank DB00916"],
        ["sys_med_0077", "Vancomycin", "vancomycin hydrochloride", "antibiotic_glycopeptide", "cell_wall_synthesis_inhibitor|narrow_therapeutic_index", "", "", "high", "DrugBank DB00512"],
        ["sys_med_0078", "Doxycycline", "doxycycline hyclate", "antibiotic_tetracycline", "30S_inhibitor", "", "", "low", "DrugBank DB00254"],
        ["sys_med_0079", "Sildenafil", "sildenafil citrate", "pde5_inhibitor", "pde5_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00203"],
        ["sys_med_0080", "Acetaminophen", "paracetamol; APAP", "analgesic_antipyretic", "cox_inhibitor_central|cyp1a2_substrate|cyp2e1_substrate|cyp3a4_substrate", "CYP1A2, CYP2E1, CYP3A4", "", "medium", "DrugBank DB00316"],
        ["sys_med_0081", "Levetiracetam", "levetiracetam", "antiepileptic", "sv2a_modulator", "", "", "low", "DrugBank DB01202"],
        ["sys_med_0082", "Lamotrigine", "lamotrigine", "antiepileptic", "na_channel_blocker", "", "", "low", "DrugBank DB00555"],
        ["sys_med_0083", "Olanzapine", "olanzapine", "antipsychotic_atypical", "d2_5ht2a_antagonist|cyp1a2_substrate", "CYP1A2", "", "low", "DrugBank DB00334"],
        ["sys_med_0084", "Risperidone", "risperidone", "antipsychotic_atypical", "d2_5ht2a_antagonist|cyp2d6_substrate", "CYP2D6", "", "low", "DrugBank DB00734"],
        ["sys_med_0085", "Quetiapine", "quetiapine fumarate", "antipsychotic_atypical", "d2_5ht2a_antagonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01224"],
        ["sys_med_0086", "Aripiprazole", "aripiprazole", "antipsychotic_atypical", "d2_partial_agonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "low", "DrugBank DB01238"],
        ["sys_med_0087", "Loratadine", "loratadine", "antihistamine_systemic", "h1_receptor_antagonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00455"],
        ["sys_med_0088", "Cetirizine", "cetirizine hydrochloride", "antihistamine_systemic", "h1_receptor_antagonist", "", "", "low", "DrugBank DB00341"],
        ["sys_med_0089", "Midazolam", "midazolam hydrochloride", "benzodiazepine", "gaba_a_positive_allosteric_modulator|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00683"],
        ["sys_med_0090", "Diazepam", "diazepam", "benzodiazepine", "gaba_a_positive_allosteric_modulator|cyp2c19_substrate|cyp3a4_substrate", "CYP2C19, CYP3A4", "", "low", "DrugBank DB00829"],
        ["sys_med_0091", "Clonazepam", "clonazepam", "benzodiazepine", "gaba_a_positive_allosteric_modulator|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01068"],
        ["sys_med_0092", "Pregabalin", "pregabalin", "antiepileptic", "calcium_channel_alpha2delta_ligand", "", "", "low", "DrugBank DB00230"],
        ["sys_med_0093", "Amitriptyline", "amitriptyline hydrochloride", "antidepressant_tca", "sert_net_inhibitor|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB00321"],
        ["sys_med_0094", "Venlafaxine", "venlafaxine hydrochloride", "antidepressant_snri", "sert_net_inhibitor|cyp2d6_substrate", "CYP2D6", "", "low", "DrugBank DB00285"],
        ["sys_med_0095", "Duloxetine", "duloxetine hydrochloride", "antidepressant_snri", "sert_net_inhibitor|cyp1a2_substrate|cyp2d6_substrate", "CYP1A2, CYP2D6", "", "low", "DrugBank DB00476"],
        ["sys_med_0096", "Pioglitazone", "pioglitazone hydrochloride", "antidiabetic_tzd", "ppar_gamma_agonist|cyp2c8_substrate", "CYP2C8", "", "low", "DrugBank DB01132"],
        ["sys_med_0097", "Linagliptin", "linagliptin", "antidiabetic_dpp4_inhibitor", "dpp4_inhibitor", "", "", "low", "DrugBank DB09044"],
        ["sys_med_0098", "Canagliflozin", "canagliflozin", "antidiabetic_sglt2_inhibitor", "sglt2_inhibitor", "", "", "low", "DrugBank DB08907"],
        ["sys_med_0099", "Liraglutide", "liraglutide", "antidiabetic_glp1_ra", "glp1_receptor_agonist", "", "", "low", "DrugBank DB01290"],
        ["sys_med_0100", "Pravastatin", "pravastatin sodium", "statin", "hmg_coa_reductase_inhibitor", "", "", "low", "DrugBank DB00175"],
        ["sys_med_0101", "Pitavastatin", "pitavastatin calcium", "statin", "hmg_coa_reductase_inhibitor|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB08876"],
        ["sys_med_0102", "Doxazosin", "doxazosin mesylate", "alpha_blocker", "alpha1_adrenergic_antagonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00590"],
        ["sys_med_0103", "Tamsulosin", "tamsulosin hydrochloride", "alpha_blocker", "alpha1a_adrenergic_antagonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "low", "DrugBank DB00706"],
        ["sys_med_0104", "Dronedarone", "dronedarone", "antiarrhythmic_class_iii", "multichannel_blocker|cyp3a4_inhibitor|cyp2d6_inhibitor", "CYP3A4, CYP2D6", "", "medium", "DrugBank DB11618"],
        ["sys_med_0105", "Lidocaine IV", "lidocaine intravenous", "antiarrhythmic_class_ib", "na_channel_blocker|cyp1a2_substrate", "CYP1A2", "", "medium", "DrugBank DB00281"],
        ["sys_med_0106", "Flecainide", "flecainide acetate", "antiarrhythmic_class_ic", "na_channel_blocker|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB01195"],
        ["sys_med_0107", "Propafenone", "propafenone hydrochloride", "antiarrhythmic_class_ic", "na_channel_blocker_beta_blocker|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB01182"],
        ["sys_med_0108", "Tranexamic acid", "tranexamic acid", "hemostatic", "plasmin_inhibitor", "", "", "low", "DrugBank DB00302"],
        ["sys_med_0109", "Alendronic acid", "alendronate sodium", "bisphosphonate", "farnesyl_pyrophosphate_synthase_inhibitor", "", "", "low", "DrugBank DB00630"],
        ["sys_med_0110", "Baclofen", "baclofen", "muscle_relaxant", "gaba_b_receptor_agonist", "", "", "low", "DrugBank DB00181"],
        ["sys_med_0111", "Zolpidem", "zolpidem tartrate", "non_benzodiazepine_hypnotic", "gaba_a_positive_allosteric_modulator|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00425"],
        ["sys_med_0112", "Methylphenidate", "methylphenidate hydrochloride", "cns_stimulant", "dat_net_inhibitor", "", "", "low", "DrugBank DB00422"],
        ["sys_med_0113", "Ondansetron", "ondansetron hydrochloride", "antiemetic", "5ht3_receptor_antagonist|cyp1a2_substrate|cyp3a4_substrate|cyp2d6_substrate", "CYP1A2, CYP3A4, CYP2D6", "", "low", "DrugBank DB00904"],
        ["sys_med_0114", "Acyclovir systemic", "acyclovir systemic", "antiviral_systemic", "viral_dna_polymerase_inhibitor", "", "", "low", "DrugBank DB00787"],
        ["sys_med_0115", "Insulin glargine", "insulin glargine; Lantus", "antidiabetic_insulin", "insulin_receptor_agonist", "", "", "medium", "DrugBank DB00047"],
        ["sys_med_0116", "Edoxaban", "edoxaban tosylate", "anticoagulant_direct_xa_inhibitor", "factor_xa_inhibitor|p_gp_substrate", "", "P-glycoprotein", "low", "DrugBank DB09075"],
        ["sys_med_0117", "Prasugrel", "prasugrel hydrochloride", "antiplatelet", "p2y12_inhibitor_prodrug", "", "", "low", "DrugBank DB06209"],
        ["sys_med_0118", "Nitroglycerin", "glyceryl trinitrate", "antianginal", "no_donor", "", "", "low", "DrugBank DB00727"],
        ["sys_med_0119", "Desmopressin", "desmopressin acetate", "antidiuretic", "vasopressin_v2_receptor_agonist", "", "", "low", "DrugBank DB00035"],
        ["sys_med_0120", "Hydroxychloroquine", "hydroxychloroquine sulfate", "immunosuppressant_systemic", "tlr_inhibitor", "", "", "low", "DrugBank DB01611"],
        ["sys_med_0121", "Mycophenolate", "mycophenolate mofetil", "immunosuppressant_systemic", "imdh_inhibitor", "", "", "low", "DrugBank DB01024"],
        ["sys_med_0122", "Azathioprine", "azathioprine", "immunosuppressant_systemic", "purine_analog", "", "", "low", "DrugBank DB00993"],
        ["sys_med_0123", "Sulfasalazine", "sulfasalazine", "dmard", "antiinflammatory|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00764"],
        ["sys_med_0124", "Leflunomide", "leflunomide", "dmard", "dhodh_inhibitor", "", "", "low", "DrugBank DB01097"],
        ["sys_med_0125", "Tadalafil", "tadalafil", "pde5_inhibitor", "pde5_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00820"],
        ["sys_med_0126", "Finasteride", "finasteride", "5ari", "5alpha_reductase_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01216"],
        ["sys_med_0127", "Loperamide", "loperamide hydrochloride", "antidiarrheal", "mu_opioid_receptor_agonist|cyp3a4_substrate|p_gp_substrate", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB00836"],
        ["sys_med_0128", "Metoclopramide", "metoclopramide hydrochloride", "antiemetic", "d2_antagonist_5ht4_agonist", "", "", "low", "DrugBank DB01233"],
        ["sys_med_0129", "Buspirone", "buspirone hydrochloride", "anxiolytic", "5ht1a_partial_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00490"],
        ["sys_med_0130", "Azithromycin systemic", "azithromycin systemic", "antibiotic_macrolide_systemic", "50S_inhibitor", "", "", "low", "DrugBank DB00207"],
        ["sys_med_0131", "Ciprofloxacin systemic", "ciprofloxacin systemic", "antibiotic_fluoroquinolone_systemic", "dna_gyrase_inhibitor|cyp1a2_inhibitor", "CYP1A2", "", "low", "DrugBank DB00537"],
        ["sys_med_0132", "Levofloxacin systemic", "levofloxacin systemic", "antibiotic_fluoroquinolone_systemic", "dna_gyrase_inhibitor", "", "", "low", "DrugBank DB01137"],
        ["sys_med_0133", "Diclofenac systemic", "diclofenac sodium systemic", "nsaid_systemic", "cox1_cox2_inhibitor|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB00586"],
        ["sys_med_0134", "Indomethacin systemic", "indomethacin systemic", "nsaid_systemic", "cox1_cox2_inhibitor", "", "", "medium", "DrugBank DB00328"],
        ["sys_med_0135", "Tiotropium", "tiotropium bromide", "respiratory_anticholinergic", "muscarinic_receptor_antagonist", "", "", "low", "DrugBank DB01409"],
        ["sys_med_0136", "Salmeterol", "salmeterol xinafoate", "respiratory_beta2_agonist", "beta2_adrenergic_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00938"],
        ["sys_med_0137", "Budesonide", "budesonide", "respiratory_corticosteroid", "glucocorticoid_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01222"],
        ["sys_med_0138", "Haloperidol", "haloperidol", "antipsychotic_typical", "d2_antagonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "medium", "DrugBank DB00502"],
        ["sys_med_0139", "Clozapine", "clozapine", "antipsychotic_atypical", "d2_5ht2a_antagonist|cyp1a2_substrate", "CYP1A2", "", "medium", "DrugBank DB00363"],
        ["sys_med_0140", "Nortriptyline", "nortriptyline hydrochloride", "antidepressant_tca", "net_inhibitor|cyp2d6_substrate", "CYP2D6", "", "medium", "DrugBank DB00540"],
        ["sys_med_0141", "Paroxetine", "paroxetine hydrochloride", "antidepressant_ssri", "sert_inhibitor|cyp2d6_inhibitor", "CYP2D6", "", "low", "DrugBank DB00715"],
        ["sys_med_0142", "Escitalopram", "escitalopram oxalate", "antidepressant_ssri", "sert_inhibitor", "", "", "low", "DrugBank DB01175"],
        ["sys_med_0143", "Fluvoxamine", "fluvoxamine maleate", "antidepressant_ssri", "sert_inhibitor|cyp1a2_inhibitor|cyp2c19_inhibitor|cyp3a4_inhibitor", "CYP1A2, CYP2C19, CYP3A4", "", "low", "DrugBank DB00176"],
        ["sys_med_0144", "Gabapentin", "gabapentin", "antiepileptic", "calcium_channel_alpha2delta_ligand", "", "", "low", "DrugBank DB00396"],
        ["sys_med_0145", "Topiramate", "topiramate", "antiepileptic", "na_channel_blocker_gaba_ergic", "", "", "low", "DrugBank DB00273"],
        ["sys_med_0146", "Pantoprazole", "pantoprazole sodium", "proton_pump_inhibitor", "h_k_atpase_inhibitor|cyp2c19_substrate", "CYP2C19", "", "low", "DrugBank DB00213"],
        ["sys_med_0147", "Esomeprazole", "esomeprazole magnesium", "proton_pump_inhibitor", "h_k_atpase_inhibitor|cyp2c19_inhibitor", "CYP2C19", "", "low", "DrugBank DB00736"],
        ["sys_med_0148", "Lansoprazole", "lansoprazole", "proton_pump_inhibitor", "h_k_atpase_inhibitor|cyp2c19_substrate|cyp3a4_substrate", "CYP2C19, CYP3A4", "", "low", "DrugBank DB00448"],
        ["sys_med_0149", "Erythromycin systemic", "erythromycin systemic", "antibiotic_macrolide_systemic", "50S_inhibitor|cyp3a4_inhibitor", "CYP3A4", "", "medium", "DrugBank DB00199"],
        ["sys_med_0150", "Voriconazole systemic", "voriconazole systemic", "antifungal_azole_systemic", "cyp51_inhibitor|cyp2c9_inhibitor|cyp2c19_inhibitor|cyp3a4_inhibitor", "CYP2C9, CYP2C19, CYP3A4", "", "medium", "DrugBank DB00582"],
        ["sys_med_0151", "Ketoconazole", "ketoconazole", "antifungal_azole_systemic", "cyp51_inhibitor|cyp3a4_inhibitor|p_gp_inhibitor", "CYP3A4", "P-glycoprotein", "low", "DrugBank DB01026"],
        ["sys_med_0152", "Tamoxifen", "tamoxifen citrate", "antineoplastic_hormonal", "estrogen_receptor_modulator|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "low", "DrugBank DB00675"],
        ["sys_med_0153", "Imatinib", "imatinib mesylate", "antineoplastic_tyrosine_kinase_inhibitor", "bcr_abl_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00619"],
        ["sys_med_0154", "Methotrexate systemic", "methotrexate systemic", "antineoplastic_antimetabolite", "dhfr_inhibitor|narrow_therapeutic_index", "", "", "high", "DrugBank DB00563"],
        ["sys_med_0155", "Cyclophosphamide", "cyclophosphamide", "antineoplastic_alkylating", "dna_crosslinker|cyp2b6_substrate|cyp3a4_substrate", "CYP2B6, CYP3A4", "", "medium", "DrugBank DB00527"],
        ["sys_med_0156", "Capecitabine", "capecitabine", "antineoplastic_antimetabolite", "thymidylate_synthase_inhibitor_prodrug", "", "", "low", "DrugBank DB01101"],
        ["sys_med_0157", "Clindamycin", "clindamycin", "antibiotic_lincosamide", "50S_inhibitor", "", "", "low", "DrugBank DB01190"],
        ["sys_med_0158", "Linezolid", "linezolid", "antibiotic_oxazolidinone", "50S_inhibitor|maoi", "", "", "low", "DrugBank DB00601"],
        ["sys_med_0159", "Tramadol", "tramadol hydrochloride", "opioid", "mu_opioid_receptor_agonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "low", "DrugBank DB00193"],
        ["sys_med_0160", "Rosiglitazone", "rosiglitazone maleate", "antidiabetic_tzd", "ppar_gamma_agonist|cyp2c8_substrate", "CYP2C8", "", "low", "DrugBank DB00412"],
        ["sys_med_0161", "Vildagliptin", "vildagliptin", "antidiabetic_dpp4_inhibitor", "dpp4_inhibitor", "", "", "low", "DrugBank DB04876"],
        ["sys_med_0162", "Saxagliptin", "saxagliptin hydrochloride", "antidiabetic_dpp4_inhibitor", "dpp4_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB06335"],
        ["sys_med_0163", "Glibenclamide", "glyburide; glibenclamide", "antidiabetic_sulfonylurea", "k_atp_channel_blocker|cyp2c9_substrate|cyp3a4_substrate", "CYP2C9, CYP3A4", "", "medium", "DrugBank DB01016"],
        ["sys_med_0164", "Insulin aspart", "insulin aspart; NovoRapid", "antidiabetic_insulin", "insulin_receptor_agonist", "", "", "medium", "DrugBank DB01306"],
        ["sys_med_0165", "Dulaglutide", "dulaglutide", "antidiabetic_glp1_ra", "glp1_receptor_agonist", "", "", "low", "DrugBank DB09045"],
        ["sys_med_0166", "Clomipramine", "clomipramine hydrochloride", "antidepressant_tca", "sert_inhibitor|cyp2d6_substrate|cyp1a2_substrate", "CYP2D6, CYP1A2", "", "medium", "DrugBank DB01242"],
        ["sys_med_0167", "Desvenlafaxine", "desvenlafaxine succinate", "antidepressant_snri", "sert_net_inhibitor", "", "", "low", "DrugBank DB06700"],
        ["sys_med_0168", "Zoledronic acid", "zoledronate", "bisphosphonate", "farnesyl_pyrophosphate_synthase_inhibitor", "", "", "low", "DrugBank DB00399"],
        ["sys_med_0169", "Febuxostat", "febuxostat", "anti_gout", "xanthine_oxidase_inhibitor", "", "", "low", "DrugBank DB04854"],
        ["sys_med_0170", "Dipyridamole", "dipyridamole", "antiplatelet", "phosphodiesterase_inhibitor", "", "", "low", "DrugBank DB00937"],
        ["sys_med_0171", "Cilostazol", "cilostazol", "antiplatelet", "pde3_inhibitor|cyp3a4_substrate|cyp2c19_substrate", "CYP3A4, CYP2C19", "", "low", "DrugBank DB01166"],
        ["sys_med_0172", "Heparin", "unfractionated heparin", "anticoagulant_parenteral", "antithrombin_iii_activator", "", "", "medium", "DrugBank DB01309"],
        ["sys_med_0173", "Enoxaparin", "enoxaparin sodium", "anticoagulant_lmw_heparin", "antithrombin_iii_activator", "", "", "medium", "DrugBank DB01225"],
        ["sys_med_0174", "Fondaparinux", "fondaparinux sodium", "anticoagulant_parenteral", "factor_xa_inhibitor_indirect", "", "", "low", "DrugBank DB01223"],
        ["sys_med_0175", "Amoxicillin", "amoxicillin", "antibiotic_penicillin", "beta_lactam_cell_wall_inhibitor", "", "", "low", "DrugBank DB01060"],
        ["sys_med_0176", "Hydrocortisone", "hydrocortisone systemic", "corticosteroid_systemic", "glucocorticoid_receptor_agonist", "", "", "low", "DrugBank DB00741"],
        ["sys_med_0177", "Perindopril", "perindopril", "ace_inhibitor", "ace_inhibitor|prodrug", "", "", "low", "DrugBank DB00790"],
        ["sys_med_0178", "Telmisartan", "telmisartan", "arb", "angiotensin_ii_receptor_antagonist", "", "", "low", "DrugBank DB00966"],
        ["sys_med_0179", "Indapamide", "indapamide", "thiazide_like_diuretic", "ncc_inhibitor", "", "", "medium", "DrugBank DB00808"],
        ["sys_med_0180", "Ivabradine", "ivabradine hydrochloride", "antianginal", "if_channel_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB09042"],
        ["sys_med_0181", "Ranolazine", "ranolazine", "antianginal", "late_na_channel_inhibitor|cyp3a4_substrate|cyp2d6_substrate", "CYP3A4, CYP2D6", "", "low", "DrugBank DB01627"],
        ["sys_med_0182", "Isosorbide mononitrate", "isosorbide mononitrate", "antianginal", "no_donor", "", "", "low", "DrugBank DB01020"],
        ["sys_med_0183", "Fluvastatin", "fluvastatin sodium", "statin", "hmg_coa_reductase_inhibitor|cyp2c9_substrate", "CYP2C9", "", "low", "DrugBank DB01095"],
        ["sys_med_0184", "Propofol", "propofol", "anesthetic_iv", "gaba_a_positive_allosteric_modulator", "", "", "low", "DrugBank DB00818"],
        ["sys_med_0185", "Dexmedetomidine", "dexmedetomidine hydrochloride", "sedative", "alpha2_adrenergic_agonist", "", "", "low", "DrugBank DB00633"],
        ["sys_med_0186", "Epinephrine", "adrenaline", "vasopressor_anaphylaxis", "alpha_beta_adrenergic_agonist", "", "", "high", "DrugBank DB00668"],
        ["sys_med_0187", "Norepinephrine", "noradrenaline", "vasopressor", "alpha1_beta1_adrenergic_agonist", "", "", "high", "DrugBank DB00368"],
        ["sys_med_0188", "Vasopressin", "arginine vasopressin", "vasopressor", "v1_v2_receptor_agonist", "", "", "medium", "DrugBank DB00078"],
        ["sys_med_0189", "Oseltamivir", "oseltamivir phosphate", "antiviral_systemic", "neuraminidase_inhibitor", "", "", "low", "DrugBank DB00198"],
        ["sys_med_0190", "Remdesivir", "remdesivir", "antiviral_systemic", "rna_polymerase_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB14761"],
        ["sys_med_0191", "Tenofovir", "tenofovir disoproxil fumarate", "antiviral_hiv", "reverse_transcriptase_inhibitor", "", "", "low", "DrugBank DB00300"],
        ["sys_med_0192", "Ritonavir", "ritonavir", "antiviral_hiv_protease_inhibitor", "hiv_protease_inhibitor|cyp3a4_inhibitor", "CYP3A4", "", "low", "DrugBank DB00503"],
        ["sys_med_0193", "Letrozole", "letrozole", "antineoplastic_aromatase_inhibitor", "aromatase_inhibitor|cyp2a6_inhibitor", "CYP2A6", "", "low", "DrugBank DB01045"],
        ["sys_med_0194", "Aprepitant", "aprepitant", "antiemetic_nk1", "nk1_receptor_antagonist|cyp3a4_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00373"],
        ["sys_med_0195", "Terazosin", "terazosin hydrochloride", "alpha_blocker", "alpha1_adrenergic_antagonist", "", "", "low", "DrugBank DB01121"],
        ["sys_med_0196", "Dutasteride", "dutasteride", "5ari", "5alpha_reductase_inhibitor|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01126"],
        ["sys_med_0197", "Levodopa/Carbidopa", "co-careldopa", "antiparkinson", "dopamine_precursor_ddc_inhibitor", "", "", "low", "DrugBank DB01235"],
        ["sys_med_0198", "Pramipexole", "pramipexole dihydrochloride", "antiparkinson", "d2_d3_receptor_agonist", "", "", "low", "DrugBank DB00413"],
        ["sys_med_0199", "Octreotide", "octreotide acetate", "somatostatin_analog", "somatostatin_receptor_agonist", "", "", "low", "DrugBank DB00104"],
        ["sys_med_0200", "Methimazole", "methimazole; thiamazole", "antithyroid", "thyroid_peroxidase_inhibitor", "", "", "low", "DrugBank DB00763"],
        # === Additions: Common Missing Drugs ===
        # Respiratory
        ["sys_med_0201", "Montelukast", "montelukast sodium", "respiratory_leukotriene_modifier", "cyslt1_receptor_antagonist|cyp3a4_substrate|cyp2c9_substrate", "CYP3A4, CYP2C9", "", "low", "DrugBank DB00471"],
        ["sys_med_0202", "Theophylline", "theophylline", "respiratory_xanthine", "adenosine_receptor_antagonist_pde_inhibitor|cyp1a2_substrate|narrow_therapeutic_index", "CYP1A2", "", "high", "DrugBank DB00277"],
        # Antidiabetic - common Chinese agents
        ["sys_med_0203", "Acarbose", "acarbose", "antidiabetic_alpha_glucosidase_inhibitor", "alpha_glucosidase_inhibitor", "", "", "low", "DrugBank DB00284"],
        ["sys_med_0204", "Repaglinide", "repaglinide", "antidiabetic_glinide", "k_atp_channel_blocker|cyp2c8_substrate|cyp3a4_substrate", "CYP2C8, CYP3A4", "", "medium", "DrugBank DB00912"],
        ["sys_med_0205", "Nateglinide", "nateglinide", "antidiabetic_glinide", "k_atp_channel_blocker|cyp2c9_substrate|cyp3a4_substrate", "CYP2C9, CYP3A4", "", "medium", "DrugBank DB00731"],
        # Lipid-lowering
        ["sys_med_0206", "Ezetimibe", "ezetimibe", "lipid_lowering_cholesterol_absorption_inhibitor", "npc1l1_inhibitor", "", "", "low", "DrugBank DB00973"],
        ["sys_med_0207", "Fenofibrate", "fenofibrate", "lipid_lowering_fibrate", "ppar_alpha_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB01039"],
        ["sys_med_0208", "Gemfibrozil", "gemfibrozil", "lipid_lowering_fibrate", "ppar_alpha_agonist|cyp2c8_inhibitor", "CYP2C8", "", "low", "DrugBank DB01241"],
        # CNS - Alzheimer's / Parkinson's
        ["sys_med_0209", "Donepezil", "donepezil hydrochloride", "alzheimers_cholinesterase_inhibitor", "ache_inhibitor|cyp3a4_substrate|cyp2d6_substrate", "CYP3A4, CYP2D6", "", "low", "DrugBank DB00843"],
        ["sys_med_0210", "Rivastigmine", "rivastigmine tartrate", "alzheimers_cholinesterase_inhibitor", "ache_buche_inhibitor", "", "", "low", "DrugBank DB00989"],
        ["sys_med_0211", "Memantine", "memantine hydrochloride", "alzheimers_nmda_antagonist", "nmda_receptor_antagonist", "", "", "low", "DrugBank DB01043"],
        ["sys_med_0212", "Ropinirole", "ropinirole hydrochloride", "parkinsons_dopamine_agonist", "d2_d3_receptor_agonist|cyp1a2_substrate", "CYP1A2", "", "low", "DrugBank DB00268"],
        # Analgesics
        ["sys_med_0213", "Codeine", "codeine phosphate", "opioid", "mu_opioid_receptor_agonist|cyp2d6_substrate|cyp3a4_substrate", "CYP2D6, CYP3A4", "", "medium", "DrugBank DB00318"],
        ["sys_med_0214", "Tapentadol", "tapentadol hydrochloride", "opioid", "mu_opioid_receptor_agonist_nri", "", "", "low", "DrugBank DB06204"],
        # GI
        ["sys_med_0215", "Mesalamine", "mesalazine; 5-ASA", "anti_inflammatory_intestinal", "unknown_anti_inflammatory", "", "", "low", "DrugBank DB00244"],
        ["sys_med_0216", "Ursodeoxycholic acid", "ursodiol; UDCA", "gallstone_dissolution", "bile_acid_replacement", "", "", "low", "DrugBank DB01586"],
        ["sys_med_0217", "Lactulose", "lactulose", "laxative_osmotic", "osmotic_laxative", "", "", "low", "DrugBank DB04468"],
        # Commonly used antibiotics (China)
        ["sys_med_0218", "Cefalexin", "cephalexin", "antibiotic_cephalosporin_1g", "cell_wall_synthesis_inhibitor", "", "", "low", "DrugBank DB00567"],
        ["sys_med_0219", "Ceftriaxone", "ceftriaxone", "antibiotic_cephalosporin_3g", "cell_wall_synthesis_inhibitor", "", "", "low", "DrugBank DB01212"],
        ["sys_med_0220", "Cefixime", "cefixime", "antibiotic_cephalosporin_3g", "cell_wall_synthesis_inhibitor", "", "", "low", "DrugBank DB00671"],
        ["sys_med_0221", "Nitrofurantoin", "nitrofurantoin", "antibiotic_urinary", "bacterial_enzyme_inhibitor", "", "", "low", "DrugBank DB00698"],
        # Hormone therapy
        ["sys_med_0222", "Estradiol", "estradiol; E2", "hormone_estrogen", "estrogen_receptor_agonist", "", "", "low", "DrugBank DB00783"],
        ["sys_med_0223", "Testosterone", "testosterone", "hormone_androgen", "androgen_receptor_agonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00624"],
        ["sys_med_0224", "Raloxifene", "raloxifene hydrochloride", "serm", "estrogen_receptor_modulator|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00481"],
        # Antiemetics/Prokinetics
        ["sys_med_0225", "Domperidone", "domperidone", "antiemetic_prokinetic", "d2_receptor_antagonist|cyp3a4_substrate", "CYP3A4", "", "medium", "DrugBank DB01184"],
        ["sys_med_0226", "Levothyroxine", "levothyroxine; T4", "thyroid_hormone", "thyroid_hormone_receptor_agonist", "", "", "medium", "DrugBank DB00451"],
        # Additional anti-gout
        ["sys_med_0227", "Probenecid", "probenecid", "anti_gout_uricosuric", "urat1_inhibitor", "", "", "low", "DrugBank DB01032"],
        # Antiplatelet (GPIIb/IIIa)
        ["sys_med_0228", "Abciximab", "abciximab", "antiplatelet_gpiibiiia", "gpiibiiia_inhibitor", "", "", "medium", "DrugBank DB00091"],
        ["sys_med_0229", "Tirofiban", "tirofiban hydrochloride", "antiplatelet_gpiibiiia", "gpiibiiia_inhibitor", "", "", "medium", "DrugBank DB00777"],
        # Alpha blockers for BPH (additional)
        ["sys_med_0230", "Alfuzosin", "alfuzosin hydrochloride", "alpha_blocker_bph", "alpha1_adrenergic_antagonist|cyp3a4_substrate", "CYP3A4", "", "low", "DrugBank DB00846"],
    ]


def main() -> None:
    seed_dir = os.path.join(PROJECT_ROOT, "data", "seed")
    os.makedirs(seed_dir, exist_ok=True)

    # Entity A
    a_data = build_entity_a()
    a_path = os.path.join(seed_dir, "entities_a.csv")
    with open(a_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["topical_ophthalmic_medications_id", "primary_name", "aliases", "category", "active_mechanisms", "flags", "evidence_sources"])
        for row in a_data:
            w.writerow(row)
    print(f"Entity A: {len(a_data)} entries -> {a_path}")

    # Entity B
    b_data = build_entity_b()
    b_path = os.path.join(seed_dir, "entities_b.csv")
    with open(b_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entity_b_id", "generic_name", "aliases", "drug_class", "flags", "metabolic_pathways", "transporter_substrates", "narrow_therapeutic_index", "label_source"])
        for row in b_data:
            w.writerow(row)
    print(f"Entity B: {len(b_data)} entries -> {b_path}")

    # Sample interactions gold
    gold_path = os.path.join(seed_dir, "interactions_gold.jsonl")
    interactions = [
        {"a_id": "topical_ophthalmic_0001", "b_id": "sys_med_0002", "mechanism": "pharmacodynamic", "severity": "high", "description": "Timolol + Metoprolol: additive beta-blockade risk of bradycardia", "evidence": "DrugBank, PubMed"},
        {"a_id": "topical_ophthalmic_0006", "b_id": "sys_med_0031", "mechanism": "pharmacodynamic", "severity": "low", "description": "Latanoprost + Aspirin: minimal interaction but monitor for ocular bleeding", "evidence": "FDA label"},
        {"a_id": "topical_ophthalmic_0014", "b_id": "sys_med_0022", "mechanism": "pharmacokinetic", "severity": "moderate", "description": "Dorzolamide + Hydrochlorothiazide: additive metabolic acidosis risk", "evidence": "PubMed"},
        {"a_id": "topical_ophthalmic_0051", "b_id": "sys_med_0055", "mechanism": "pharmacodynamic", "severity": "moderate", "description": "Prednisolone topical + Prednisone systemic: additive corticosteroid effects", "evidence": "FDA label"},
        {"a_id": "topical_ophthalmic_0078", "b_id": "sys_med_0009", "mechanism": "pharmacodynamic", "severity": "moderate", "description": "Phenylephrine + Amlodipine: reduced antihypertensive effect", "evidence": "PubMed"},
        {"a_id": "topical_ophthalmic_0012", "b_id": "sys_med_0002", "mechanism": "pharmacodynamic", "severity": "moderate", "description": "Brimonidine + Metoprolol: additive hypotensive effect", "evidence": "PubMed"},
    ]
    with open(gold_path, "w", encoding="utf-8") as f:
        for item in interactions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Interactions gold: {len(interactions)} entries -> {gold_path}")
    print("Done!")


if __name__ == "__main__":
    main()
