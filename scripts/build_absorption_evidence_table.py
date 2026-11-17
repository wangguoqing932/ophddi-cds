# -*- coding: utf-8 -*-
"""Build data/curation/absorption_tier_evidence.csv from the registry plus curated evidence."""
import csv
from collections import Counter

T = ['systemic_absorption_high', 'systemic_absorption_medium', 'systemic_absorption_low',
     'systemic_absorption_very_low', 'minimal_systemic_absorption', 'systemic_absorption_none']


def tier(fs):
    for t in T:
        if t in fs:
            return t
    return 'NONE'


O = {
    'Timolol': ('0.25-0.5% ophthalmic solution', 'one drop twice daily',
                'Systemic bioavailability was about 78% relative to intravenous timolol in one crossover study; plasma concentrations after topical dosing are in the low ng/mL range.',
                'FDA timolol ophthalmic label; refs [5-7]', 'measured', ''),
    'Atropine': ('1% ophthalmic solution', '30-40 uL per dose',
                 'Systemic bioavailability of l-hyoscyamine 64 +/- 29%; Cmax 288 +/- 73 pg/mL (30 uL) and 860 +/- 402 pg/mL (40 uL).',
                 'Isopto Atropine label, section 12.3', 'measured', ''),
    'Dexamethasone': ('0.1% ophthalmic suspension', 'one drop four times daily',
                      'Peak plasma dexamethasone <1 ng/mL after multiple bilateral doses of 0.1%.',
                      'TobraDex label, section 12.3', 'measured',
                      're-tiered high to medium; peak plasma <1 ng/mL is below the high-exposure band; medium is a conservative ordinal placement'),
    'Dorzolamide': ('2% ophthalmic solution', 'one drop three times daily',
                    'Plasma dorzolamide and metabolite generally below the assay limit of quantitation (15 nM).',
                    'Dorzolamide label, section 12.3', 'measured',
                    'reassigned low -> very low after assay-limit review'),
    'Brinzolamide': ('1% ophthalmic suspension', 'one drop three times daily',
                     'Plasma brinzolamide and N-desethyl brinzolamide below the assay limit of quantification (10 ng/mL).',
                     'Azopt label, section 12.3', 'measured',
                     'reassigned low -> very low after assay-limit review'),
    'Accelidine': ('1.44% ophthalmic solution', 'two drops per eye once daily',
                   'Metabolite 3-quinuclidinol Cmax 2.1 ng/mL and AUC0-t 4.9 h.ng/mL; label states systemic levels are low.',
                   'VIZZ label, section 12.3', 'measured', 'tier retained; curation file corrected'),
    'Flurbiprofen': ('0.03% ophthalmic solution', 'one drop four times daily',
                     'Lowest-concentration ophthalmic NSAID in the registry; systemic exposure low.',
                     'FDA flurbiprofen ophthalmic label', 'label_statement',
                     'corrected high to low before this revision'),
    'Prednisolone': ('1% ophthalmic suspension', 'one drop four times daily',
                     'No quantitative PK in the label; systemic absorption is acknowledged but not measured.',
                     'Pred Forte label', 'label_statement',
                     'uncertain: medium is a conservative class assignment'),
    'Betaxolol': ('0.5% ophthalmic suspension', 'one drop twice daily',
                  'Beta1-selective; systemic exposure lower than timolol but measurable.',
                  'DrugBank DB00195; betaxolol label', 'class_inference', 'uncertain'),
    'Brimonidine': ('0.1-0.2% ophthalmic solution', 'one drop two to three times daily',
                    'Systemic absorption documented by pediatric CNS depression and apnea.',
                    'FDA brimonidine label; case reports', 'label_statement', ''),
    'Apraclonidine': ('0.5-1% ophthalmic solution', 'one drop up to three times daily',
                      'Systemic alpha-2 exposure documented by dry mouth and fatigue.',
                      'DrugBank DB00484; label', 'label_statement', 'uncertain'),
    'Cyclopentolate': ('0.5-2% ophthalmic solution', 'one drop',
                       'Anticholinergic systemic effects reported, especially in children.',
                       'DrugBank; label', 'class_inference', 'uncertain'),
    'Homatropine': ('2-5% ophthalmic solution', 'one drop',
                    'Anticholinergic systemic effects reported.',
                    'DrugBank; label', 'class_inference', 'uncertain'),
    'Phenylephrine': ('2.5-10% ophthalmic solution', 'one drop',
                      'Systemic alpha-1 exposure can raise blood pressure; label warns.',
                      'Label', 'label_statement', ''),
    'Naphazoline': ('0.05-0.1% ophthalmic solution', 'one to two drops',
                    'Imidazoline systemic absorption can cause CNS depression in children.',
                    'Label', 'class_inference', 'uncertain'),
    'Tetrahydrozoline': ('0.05% ophthalmic solution', 'one to two drops',
                         'Imidazoline systemic absorption can cause CNS depression in children.',
                         'Label', 'class_inference', 'uncertain'),
    'Pilocarpine': ('1-4% ophthalmic solution', 'one drop up to four times daily',
                    'Systemic cholinergic effects uncommon but reported.',
                    'DrugBank; label', 'class_inference', 'uncertain'),
    'Carbachol': ('1.5-3% ophthalmic solution', 'one drop up to three times daily',
                  'Systemic cholinergic effects uncommon.',
                  'DrugBank; label', 'class_inference', 'uncertain'),
    'Dipivefrin': ('0.1% ophthalmic solution', 'one drop twice daily',
                   'Prodrug of epinephrine; systemic adrenergic exposure possible.',
                   'DrugBank; label', 'class_inference', 'uncertain'),
    'Fluorometholone': ('0.1-0.25% ophthalmic suspension', 'one drop two to four times daily',
                        'No quantitative PK; corticosteroid systemic absorption acknowledged.',
                        'Label', 'class_inference', 'uncertain'),
    'Rimexolone': ('1% ophthalmic suspension', 'one drop up to four times daily',
                   'No quantitative PK; corticosteroid systemic absorption acknowledged.',
                   'Label', 'class_inference', 'uncertain'),
    'Scopolamine': ('0.25% ophthalmic solution', 'one drop',
                    'Anticholinergic systemic toxicity reported; class effect shared with atropine.',
                    'DrugBank; case reports', 'class_inference', 'uncertain'),
    'Carteolol': ('1-2% ophthalmic solution', 'one drop twice daily',
                  'Non-selective beta-blocker; nasolacrimal absorption expected to approach timolol.',
                  'DrugBank DB00521; label', 'class_inference', 'uncertain'),
    'Levobunolol': ('0.25-0.5% ophthalmic solution', 'one drop once to twice daily',
                    'Non-selective beta-blocker; systemic absorption documented.',
                    'DrugBank DB01210; label', 'class_inference', 'uncertain'),
    'Metipranolol': ('0.3% ophthalmic solution', 'one drop twice daily',
                     'Non-selective beta-blocker; systemic absorption expected.',
                     'DrugBank DB01214; label', 'class_inference', 'uncertain'),
    'Ecothiopate': ('0.03-0.25% ophthalmic solution', 'one drop',
                    'Cholinesterase inhibitor; systemic cholinergic toxicity reported.',
                    'DrugBank; label', 'class_inference', 'uncertain'),
    'Sulfacetamide/Prednisolone': ('10%/0.2% ophthalmic suspension', 'one drop up to four times daily',
                                   'Product tier = highest component tier (prednisolone, medium); sulfacetamide low.',
                                   'Component labels', 'class_inference',
                                   'combination product; per-component assignment'),
    'Tobramycin/Dexamethasone': ('0.3%/0.1% ophthalmic suspension', 'one drop four times daily',
                                 'Dexamethasone component measured <1 ng/mL; tobramycin systemic absorption not quantified.',
                                 'TobraDex label, section 12.3', 'measured',
                                 're-tiered high to medium; per-component assignment'),
    'Neomycin/Polymyxin B/Dexamethasone': ('0.35%/0.1%/0.1% ophthalmic suspension',
                                           'one drop up to four times daily',
                                           'Dexamethasone component measured <1 ng/mL; aminoglycoside/polypeptide components low.',
                                           'Maxitrol label; TobraDex label', 'measured',
                                           're-tiered high to medium; per-component assignment'),
    'Timolol/Latanoprost': ('0.5%/0.005% ophthalmic solution', 'one drop once daily',
                            'Product tier = highest component tier (timolol, high); latanoprost low.',
                            'Component labels; refs [5-7]', 'measured', 'per-component assignment'),
    'Timolol/Travoprost': ('0.5%/0.004% ophthalmic solution', 'one drop once daily',
                           'Product tier = highest component tier (timolol, high); travoprost low.',
                           'Component labels; refs [5-7]', 'measured', 'per-component assignment'),
    'Timolol/Bimatoprost': ('0.5%/0.03% ophthalmic solution', 'one drop once daily',
                            'Product tier = highest component tier (timolol, high); bimatoprost low.',
                            'Component labels; refs [5-7]', 'measured', 'per-component assignment'),
    'Timolol/Brimonidine': ('0.5%/0.2% ophthalmic solution', 'one drop twice daily',
                            'Product tier = highest component tier (timolol, high); brimonidine medium.',
                            'Component labels; refs [5-7]', 'measured', 'per-component assignment'),
    'Timolol/Dorzolamide': ('0.5%/2% ophthalmic solution', 'one drop twice daily',
                            'Product tier = highest component tier (timolol, high); dorzolamide very low.',
                            'Component labels; refs [5-7]', 'measured', 'per-component assignment'),
    'Ranibizumab': ('0.5 mg/0.05 mL intravitreal injection (Fab, 48 kDa)', 'monthly or treat-and-extend',
                    'Serum ranibizumab concentrations are in the low ng/mL range and below systemic therapeutic exposure.',
                    'FDA ranibizumab label', 'label_statement', 'intravitreal; individual agent'),
    'Aflibercept': ('2 mg/0.05 mL intravitreal injection (fusion protein, 115 kDa)', 'every 4-8 weeks',
                    'Free serum aflibercept is generally below the assay limit; systemic exposure minimal.',
                    'FDA aflibercept label', 'label_statement', 'intravitreal; individual agent'),
    'Bevacizumab': ('1.25 mg/0.05 mL intravitreal injection (IgG1, 149 kDa)', 'every 4-6 weeks',
                    'Serum bevacizumab is detectable but far below systemic anticancer doses; exposure minimal.',
                    'FDA bevacizumab label; IVT literature', 'label_statement', 'intravitreal; individual agent'),
    'Brolucizumab': ('6 mg/0.05 mL intravitreal injection (scFv, 26 kDa)', 'every 8-12 weeks',
                     'Serum brolucizumab is low and transient despite the smaller format.',
                     'FDA brolucizumab label', 'label_statement', 'intravitreal; individual agent'),
    'Faricimab': ('6 mg/0.05 mL intravitreal injection (bispecific IgG1, 150 kDa)', 'every 8-16 weeks',
                  'Serum faricimab is low; systemic exposure minimal.',
                  'FDA faricimab label', 'label_statement', 'intravitreal; individual agent'),
    'Conbercept': ('0.5 mg/0.05 mL intravitreal injection (fusion protein, 143 kDa)',
                   'monthly or treat-and-extend',
                   'Serum conbercept is low; systemic exposure minimal.',
                   'Conbercept label/literature', 'class_inference', 'intravitreal; individual agent'),
    'Acetylcholine intraocular': ('1% intracameral injection', 'single intraoperative dose',
                                  'Confined to the anterior chamber; systemic exposure minimal.',
                                  'DrugBank; surgical literature', 'class_inference',
                                  'intraocular; individual agent'),
    'Carboxymethylcellulose': ('viscoelastic / tear substitute', 'intraoperative or topical',
                               'No systemic absorption expected.', 'Product label', 'class_inference', 'none'),
    'Hydroxypropyl cellulose': ('tear substitute', 'topical', 'No systemic absorption expected.',
                                'Product label', 'class_inference', 'none'),
    'Hydroxypropyl methylcellulose': ('viscoelastic / tear substitute', 'intraoperative or topical',
                                      'No systemic absorption expected.', 'Product label', 'class_inference',
                                      'none'),
    'Sodium hyaluronate': ('viscoelastic / tear substitute', 'intraoperative or topical',
                           'No systemic absorption expected.', 'Product label', 'class_inference', 'none'),
    'Cyclosporine': ('0.05-0.1% ophthalmic emulsion', 'one drop twice daily',
                     'Systemic exposure below quantification in most patients.',
                     'Restasis label', 'label_statement', ''),
}


def main():
    rows = list(csv.DictReader(open('data/seed/entities_a.csv', encoding='utf-8-sig')))
    out = []
    for r in rows:
        name = r['primary_name']
        t = tier(r['flags'].split('|'))
        o = O.get(name)
        if o:
            form, dose, exp, src, cert, note = o
        else:
            form = 'ophthalmic product (strength not itemised in registry)'
            dose = 'as labelled'
            exp = ('No agent-specific systemic-exposure measurement identified; tier assigned from '
                   'class pharmacology and label warnings.')
            src = r.get('evidence_sources', '')
            cert = 'class_inference'
            note = ''
        out.append({
            'ophthalmic_id': r['topical_ophthalmic_medications_id'],
            'primary_name': name,
            'route': r['ophthalmic_administration'],
            'formulation_concentration': form,
            'dosing': dose,
            'absorption_tier': t,
            'exposure_evidence': exp,
            'source': src,
            'certainty': cert,
            'resolution_note': note,
        })
    with open('data/curation/absorption_tier_evidence.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print('rows', len(out))
    print(Counter(o['certainty'] for o in out))
    print(Counter(o['absorption_tier'] for o in out))


if __name__ == '__main__':
    main()
