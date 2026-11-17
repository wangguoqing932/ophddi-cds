#!/usr/bin/env python3
"""build_drug_classes.py — Generate configs/drug_classes.yaml (A/B pharmacologic class maps).

Class mapping is INDEPENDENT of the flag system (entities CSVs stay untouched):
- manual map (pharmacologic knowledge, highest priority)
- flag-inferred fallback (only broad mechanism flags)
- 'other' for genuinely unclassifiable drugs
"""
import csv, json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

MANUAL = {
    # ── antidiabetic ──
    'Gliclazide': 'antidiabetic', 'Glimepiride': 'antidiabetic', 'Sitagliptin': 'antidiabetic',
    'Empagliflozin': 'antidiabetic', 'Dapagliflozin': 'antidiabetic', 'Semaglutide': 'antidiabetic',
    'Pioglitazone': 'antidiabetic', 'Linagliptin': 'antidiabetic', 'Canagliflozin': 'antidiabetic',
    'Liraglutide': 'antidiabetic', 'Insulin glargine': 'antidiabetic', 'Rosiglitazone': 'antidiabetic',
    'Vildagliptin': 'antidiabetic', 'Insulin aspart': 'antidiabetic', 'Acarbose': 'antidiabetic',
    'Metformin': 'antidiabetic', 'Dulaglutide': 'antidiabetic', 'Glipizide': 'antidiabetic',
    'Glyburide': 'antidiabetic', 'Saxagliptin': 'antidiabetic', 'Exenatide': 'antidiabetic',
    'Miglitol': 'antidiabetic', 'Insulin lispro': 'antidiabetic', 'Insulin regular': 'antidiabetic',
    # ── statin ──
    'Rosuvastatin': 'statin', 'Pravastatin': 'statin', 'Pitavastatin': 'statin', 'Fluvastatin': 'statin',
    'Simvastatin': 'statin', 'Atorvastatin': 'statin', 'Lovastatin': 'statin',
    # ── antidepressant ──
    'Fluoxetine': 'antidepressant_ssri', 'Sertraline': 'antidepressant_ssri', 'Escitalopram': 'antidepressant_ssri',
    'Amitriptyline': 'antidepressant_tca', 'Duloxetine': 'antidepressant_ssri', 'Paroxetine': 'antidepressant_ssri',
    'Citalopram': 'antidepressant_ssri', 'Mirtazapine': 'antidepressant_other', 'Venlafaxine': 'antidepressant_ssri',
    'Bupropion': 'antidepressant_other', 'Trazodone': 'antidepressant_other', 'Nefazodone': 'antidepressant_other',
    # TCA 主类优先于抗胆碱 FLAG2CLASS 映射（否则 TCA 特异性机制 cell 全部落空）
    'Clomipramine': 'antidepressant_tca', 'Nortriptyline': 'antidepressant_tca',
    # ── antiepileptic ──
    'Carbamazepine': 'antiepileptic', 'Valproic acid': 'antiepileptic', 'Phenytoin': 'antiepileptic',
    'Levetiracetam': 'antiepileptic', 'Lamotrigine': 'antiepileptic', 'Gabapentin': 'antiepileptic',
    'Topiramate': 'antiepileptic', 'Pregabalin': 'antiepileptic', 'Oxcarbazepine': 'antiepileptic',
    'Ethosuximide': 'antiepileptic', 'Tiagabine': 'antiepileptic',
    # ── nsaid ──
    'Ibuprofen': 'nsaid', 'Naproxen': 'nsaid', 'Celecoxib': 'nsaid', 'Diclofenac systemic': 'nsaid',
    'Indomethacin systemic': 'nsaid',
    # ── immunosuppressant ──
    'Methotrexate': 'immunosuppressant', 'Methotrexate systemic': 'immunosuppressant',
    'Mycophenolate': 'immunosuppressant', 'Azathioprine': 'immunosuppressant',
    'Leflunomide': 'immunosuppressant', 'Sulfasalazine': 'immunosuppressant',
    'Cyclosporine': 'immunosuppressant', 'Tacrolimus': 'immunosuppressant',
    'Sirolimus': 'immunosuppressant', 'Everolimus': 'immunosuppressant',
    # ── antifungal / antimycobacterial ──
    'Fluconazole systemic': 'antifungal', 'Itraconazole': 'antifungal', 'Ketoconazole': 'antifungal',
    'Voriconazole': 'antifungal', 'Griseofulvin': 'antifungal', 'Terbinafine': 'antifungal',
    'Rifampicin': 'antimycobacterial', 'Isoniazid': 'antimycobacterial',
    'Ethambutol': 'antimycobacterial', 'Pyrazinamide': 'antimycobacterial',
    # ── thyroid / beta2 / urate ──
    'Levothyroxine': 'thyroid_hormone', 'Salbutamol': 'beta2_agonist', 'Formoterol': 'beta2_agonist',
    'Allopurinol': 'urate_lowering', 'Febuxostat': 'urate_lowering',
    # ── antibiotic ──
    'Metronidazole': 'antibiotic', 'Vancomycin': 'antibiotic', 'Doxycycline': 'antibiotic',
    'Azithromycin systemic': 'antibiotic', 'Clindamycin': 'antibiotic', 'Linezolid': 'antibiotic',
    'Amoxicillin': 'antibiotic', 'Cefalexin': 'antibiotic', 'Ceftriaxone': 'antibiotic',
    'Cefixime': 'antibiotic', 'Nitrofurantoin': 'antibiotic', 'Erythromycin': 'macrolide',
    'Clarithromycin': 'macrolide', 'Sulfamethoxazole': 'antibiotic', 'Trimethoprim': 'antibiotic',
    'Tetracycline': 'antibiotic', 'Minocycline': 'antibiotic', 'Gentamicin': 'antibiotic',
    'Tobramycin systemic': 'antibiotic', 'Amikacin': 'antibiotic', 'Teicoplanin': 'antibiotic',
    'Daptomycin': 'antibiotic', 'Roxithromycin': 'antibiotic',
    # ── fluoroquinolone ──
    'Ciprofloxacin systemic': 'fluoroquinolone', 'Levofloxacin systemic': 'fluoroquinolone',
    'Moxifloxacin systemic': 'fluoroquinolone', 'Ofloxacin systemic': 'fluoroquinolone',
    'Norfloxacin': 'fluoroquinolone',
    # ── antiviral ──
    'Acyclovir systemic': 'antiviral', 'Oseltamivir': 'antiviral', 'Remdesivir': 'antiviral',
    'Tenofovir': 'antiviral', 'Valganciclovir': 'antiviral', 'Ganciclovir systemic': 'antiviral',
    'Famciclovir': 'antiviral', 'Raltegravir': 'antiviral', 'Efavirenz': 'antiviral',
    'Nevirapine': 'antiviral',
    # ── antipsychotic / benzodiazepine ──
    'Risperidone': 'antipsychotic', 'Quetiapine': 'antipsychotic', 'Olanzapine': 'antipsychotic',
    'Haloperidol': 'antipsychotic', 'Aripiprazole': 'antipsychotic', 'Clozapine': 'antipsychotic',
    'Diazepam': 'benzodiazepine', 'Lorazepam': 'benzodiazepine', 'Alprazolam': 'benzodiazepine',
    'Oxazepam': 'benzodiazepine',
    # ── antiarrhythmic / cardiac ──
    'Lidocaine IV': 'antiarrhythmic', 'Flecainide': 'antiarrhythmic', 'Propafenone': 'antiarrhythmic',
    'Amiodarone': 'antiarrhythmic', 'Sotalol': 'antiarrhythmic', 'Dronedarone': 'antiarrhythmic',
    'Ivabradine': 'antiarrhythmic', 'Digoxin': 'cardiac_glycoside',
    # ── anticoagulant / antiplatelet ──
    'Warfarin': 'anticoagulant', 'Acenocoumarol': 'anticoagulant', 'Phenprocoumon': 'anticoagulant',
    'Rivaroxaban': 'anticoagulant', 'Apixaban': 'anticoagulant', 'Edoxaban': 'anticoagulant',
    'Dabigatran': 'anticoagulant', 'Enoxaparin': 'anticoagulant', 'Dalteparin': 'anticoagulant',
    'Heparin': 'anticoagulant', 'Fondaparinux': 'anticoagulant',
    'Clopidogrel': 'antiplatelet', 'Prasugrel': 'antiplatelet', 'Ticagrelor': 'antiplatelet',
    'Dipyridamole': 'antiplatelet', 'Cilostazol': 'antiplatelet', 'Aspirin': 'antiplatelet',
    # ── antihypertensive ──
    'Timolol systemic': 'beta_blocker', 'Propranolol': 'beta_blocker', 'Metoprolol': 'beta_blocker',
    'Atenolol': 'beta_blocker', 'Bisoprolol': 'beta_blocker', 'Carvedilol': 'beta_blocker',
    'Nebivolol': 'beta_blocker', 'Labetalol': 'beta_blocker',
    'Verapamil': 'ccb', 'Diltiazem': 'ccb', 'Nifedipine': 'ccb', 'Amlodipine': 'ccb',
    'Felodipine': 'ccb',
    'Enalapril': 'acei', 'Lisinopril': 'acei', 'Ramipril': 'acei', 'Perindopril': 'acei',
    'Captopril': 'acei',
    'Losartan': 'arb', 'Valsartan': 'arb', 'Irbesartan': 'arb', 'Candesartan': 'arb',
    'Telmisartan': 'arb',
    'Furosemide': 'diuretic', 'Hydrochlorothiazide': 'diuretic', 'Indapamide': 'diuretic',
    'Spironolactone': 'diuretic', 'Eplerenone': 'diuretic', 'Torsemide': 'diuretic',
    'Bumetanide': 'diuretic',
    'Terazosin': 'alpha1_blocker',
    # ── antihistamine / anticholinergic ──
    'Diphenhydramine': 'antihistamine', 'Cetirizine': 'antihistamine', 'Loratadine': 'antihistamine',
    'Fexofenadine': 'antihistamine', 'Oxybutynin': 'anticholinergic', 'Tolterodine': 'anticholinergic',
    # ── corticosteroid ──
    'Prednisone': 'corticosteroid', 'Methylprednisolone': 'corticosteroid',
    'Prednisolone systemic': 'corticosteroid', 'Hydrocortisone': 'corticosteroid',
    'Dexamethasone systemic': 'corticosteroid',
    # ── opioid ──
    'Oxycodone': 'opioid', 'Morphine': 'opioid', 'Tramadol': 'opioid', 'Fentanyl': 'opioid',
    'Methadone': 'opioid', 'Buprenorphine': 'opioid', 'Codeine': 'opioid', 'Hydrocodone': 'opioid',
    # ── other systemic ──
    'Tranexamic acid': 'antifibrinolytic', 'Alendronic acid': 'bisphosphonate',
    'Zoledronic acid': 'bisphosphonate', 'Baclofen': 'muscle_relaxant',
    'Tizanidine': 'muscle_relaxant', 'Cyclobenzaprine': 'muscle_relaxant',
    'Carisoprodol': 'muscle_relaxant',
    'Methylphenidate': 'cns_stimulant', 'Atomoxetine': 'cns_stimulant', 'Modafinil': 'cns_stimulant',
    'Nitroglycerin': 'nitrate', 'Isosorbide mononitrate': 'nitrate',
    'Desmopressin': 'vasopressin_analog', 'Vasopressin': 'vasopressin_analog',
    'Hydroxychloroquine': 'antimalarial', 'Chloroquine': 'antimalarial', 'Quinine': 'antimalarial',
    'Artemether': 'antimalarial',
    'Metoclopramide': 'antiemetic', 'Pantoprazole': 'ppi', 'Esomeprazole': 'ppi',
    'Capecitabine': 'antineoplastic', 'Letrozole': 'antineoplastic',
    'Propofol': 'anesthetic', 'Dexmedetomidine': 'anesthetic',
    'Epinephrine': 'sympathomimetic', 'Norepinephrine': 'sympathomimetic',
    'Octreotide': 'somatostatin_analog', 'Methimazole': 'antithyroid',
    'Theophylline': 'xanthine', 'Ezetimibe': 'lipid_lowering', 'Fenofibrate': 'lipid_lowering',
    'Gemfibrozil': 'lipid_lowering',
    'Rivastigmine': 'cholinergic', 'Memantine': 'nmda_antagonist',
    'Levodopa/Carbidopa': 'dopaminergic', 'Pramipexole': 'dopaminergic', 'Ropinirole': 'dopaminergic',
    'Mesalamine': 'gi_antiinflammatory', 'Ursodeoxycholic acid': 'gi_antiinflammatory',
    'Lactulose': 'gi_antiinflammatory',
    'Estradiol': 'estrogen', 'Probenecid': 'uricosuric', 'Lithium': 'lithium',
    'Acetazolamide': 'carbonic_anhydrase_inhibitor', 'Methazolamide': 'carbonic_anhydrase_inhibitor',
    'Sildenafil': 'pde5', 'Tadalafil': 'pde5', 'Vardenafil': 'pde5',
    'Zolpidem': 'sedative_hypnotic', 'Eszopiclone': 'sedative_hypnotic',
    'Acetaminophen': 'analgesic_antipyretic',
    # ── second-pass additions ──
    'Cyclosporine systemic': 'immunosuppressant', 'Tacrolimus systemic': 'immunosuppressant',
    'Omeprazole': 'ppi', 'Lansoprazole': 'ppi', 'Colchicine': 'other',
    'Doxazosin': 'alpha1_blocker', 'Tamsulosin': 'alpha1_blocker', 'Alfuzosin': 'alpha1_blocker',
    'Ondansetron': 'antiemetic', 'Domperidone': 'antiemetic', 'Aprepitant': 'antiemetic',
    'Finasteride': 'other', 'Dutasteride': 'other',
    'Buspirone': 'cns_depressant', 'Salmeterol': 'beta2_agonist', 'Fluvoxamine': 'antidepressant_ssri',
    'Erythromycin systemic': 'macrolide', 'Voriconazole systemic': 'antifungal',
    'Tamoxifen': 'antineoplastic', 'Imatinib': 'antineoplastic', 'Cyclophosphamide': 'antineoplastic',
    'Glibenclamide': 'antidiabetic', 'Desvenlafaxine': 'antidepressant_ssri',
    'Ranolazine': 'antiarrhythmic', 'Ritonavir': 'antiviral',
    'Montelukast': 'other', 'Repaglinide': 'antidiabetic', 'Nateglinide': 'antidiabetic',
    'Donepezil': 'cholinergic', 'Testosterone': 'other', 'Raloxifene': 'other',
}

FLAG2CLASS = [
    ('beta_blocker_systemic', 'beta_blocker'), ('l_type_calcium_channel_blocker', 'ccb'),
    ('ace_inhibitor', 'acei'), ('angiotensin_ii_receptor_antagonist', 'arb'),
    ('diuretic', 'diuretic'), ('anticoagulant', 'anticoagulant'), ('antiplatelet', 'antiplatelet'),
    ('anticholinergic_systemic', 'anticholinergic'), ('cns_depressant', 'cns_depressant'),
    ('corticosteroid_systemic', 'corticosteroid'), ('h1_receptor_antagonist', 'antihistamine'),
    ('ampk_activator', 'antidiabetic'), ('immunosuppressant', 'immunosuppressant'),
    ('mu_opioid_receptor_agonist', 'opioid'), ('nsaid', 'nsaid'),
]

# A-side classes (from mechanism flags; names verified against entities_a.csv)
A_MECH = [
    ('beta_blocker', 'beta_blocker'), ('alpha2_agonist', 'alpha2_agonist'),
    ('cai_topical', 'carbonic_anhydrase_inhibitor'),
    ('prostaglandin_analog', 'prostaglandin_analog'), ('anticholinergic', 'anticholinergic'),
    ('sympathomimetic', 'sympathomimetic'), ('nsaid', 'nsaid'), ('corticosteroid', 'corticosteroid'),
    ('fluoroquinolone', 'fluoroquinolone'), ('aminoglycoside', 'aminoglycoside'),
    ('macrolide', 'macrolide'), ('antibiotic', 'antibiotic'), ('antihistamine', 'antihistamine'),
    ('mast_cell_stabilizer', 'mast_cell_stabilizer'), ('mydriatic', 'mydriatic'),
    ('immunosuppressant', 'immunosuppressant'), ('antiviral', 'antiviral'),
    ('cholinergic', 'cholinergic'), ('antifungal', 'antifungal_azole'), ('anesthetic', 'local_anesthetic'),
    ('cholinergic_crisis_risk', 'cholinergic'),
]

# Sparse B-side classes with no known ophthalmic-DDI meaning -> merged into 'other'
B_SPARSE_TO_OTHER = {
    'somatostatin_analog', 'antithyroid', 'estrogen', 'uricosuric',
    'gi_antiinflammatory', 'bisphosphonate', 'antifibrinolytic', 'vasopressin_analog',
    'cns_stimulant', 'nmda_antagonist', 'dopaminergic', 'antiemetic', 'ppi',
    'antineoplastic', 'anesthetic', 'sedative_hypnotic', 'pde5', 'analgesic_antipyretic',
    'lipid_lowering', 'muscle_relaxant', 'antimalarial', 'cns_depressant_other',
}


def build_b(rows) -> dict:
    classes = {}
    for r in rows:
        name = r['generic_name']
        if name in MANUAL:
            classes[name] = MANUAL[name]
        else:
            fl = set(r['flags'].split('|'))
            classes[name] = next((c for f, c in FLAG2CLASS if f in fl), 'other')
    # merge sparse classes into 'other'
    for name in list(classes):
        if classes[name] in B_SPARSE_TO_OTHER:
            classes[name] = 'other'
    return classes


WEAK_CORTICOSTEROIDS = {'Fluorometholone', 'Loteprednol', 'Rimexolone'}

def build_a(rows) -> dict:
    classes = {}
    for r in rows:
        fl = set(r['flags'].split('|'))
        cls = next((c for f, c in A_MECH if f in fl), 'other')
        if cls == 'corticosteroid' and r['primary_name'] in WEAK_CORTICOSTEROIDS:
            cls = 'corticosteroid_weak'
        classes[r['primary_name']] = cls
    return classes


def main() -> None:
    b_rows = list(csv.DictReader((ROOT / 'data' / 'seed' / 'entities_b.csv').open(encoding='utf-8-sig')))
    a_rows = list(csv.DictReader((ROOT / 'data' / 'seed' / 'entities_a.csv').open(encoding='utf-8-sig')))
    b = build_b(b_rows)
    a = build_a(a_rows)
    dist = Counter(b.values())
    print('B classes:', len(dist), '| other:', dist.get('other', 0))
    print('  other drugs:', [n for n, c in b.items() if c == 'other'])
    print('A classes:', len(Counter(a.values())), '|', dict(Counter(a.values())))
    out = {'schema_version': 2, 'side_a_classes': sorted(set(a.values())),
           'side_b_classes': sorted(set(b.values())),
           'class_of': {'entity_a': a, 'entity_b': b}}
    (ROOT / 'configs').mkdir(exist_ok=True)
    (ROOT / 'configs' / 'drug_classes.yaml').write_text(
        yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print('saved configs/drug_classes.yaml')


if __name__ == '__main__':
    main()
