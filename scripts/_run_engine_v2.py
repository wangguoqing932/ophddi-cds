"""Run rule engine v2 against dev-ddinter + int-pubmed datasets."""
import sys, json, csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))

from ophthalmic_ddi_cds_agent.risk_rules import RuleEngine
from ophthalmic_ddi_cds_agent.schemas import EntityA, EntityB

def load_entities_a(csv_path):
    entities = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            eid = row['topical_ophthalmic_medications_id']
            flags = [f.strip() for f in row['flags'].split('|') if f.strip()]
            mechanisms = [m.strip() for m in row['active_mechanisms'].split('|') if m.strip()] if row.get('active_mechanisms') else []
            entities[eid] = EntityA(
                entity_a_id=eid, primary_name=row.get('primary_name',''),
                category=row.get('category',''), flags=flags,
                active_mechanisms=mechanisms, evidence_sources=[])
    return entities

def load_entities_b(csv_path):
    entities = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            eid = row['entity_b_id']
            flags = [f.strip() for f in row['flags'].split('|') if f.strip()]
            pathways = [p.strip() for p in row['metabolic_pathways'].split('|') if p.strip()] if row.get('metabolic_pathways') else []
            entities[eid] = EntityB(
                entity_b_id=eid, generic_name=row.get('generic_name',''),
                drug_class=row.get('drug_class',''), flags=flags,
                metabolic_pathways=pathways, transporter_substrates=[])
    return entities

def load_rows(csv_path, id_col):
    rows = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            rows[row[id_col]] = row
    return rows

# Load
entities_a = load_entities_a(PROJECT / 'data' / 'seed' / 'entities_a.csv')
entities_b = load_entities_b(PROJECT / 'data' / 'seed' / 'entities_b.csv')
rows_a = load_rows(PROJECT / 'data' / 'seed' / 'entities_a.csv', 'topical_ophthalmic_medications_id')
rows_b = load_rows(PROJECT / 'data' / 'seed' / 'entities_b.csv', 'entity_b_id')

engine = RuleEngine(PROJECT / 'configs' / 'rules.yaml')
print(f'Engine: {len(engine.config["rules"])} rules, SHA={engine.sha256[:12]}')

for ds_name in ['dev-ddinter', 'int-pubmed']:
    cases_path = PROJECT / 'data' / 'datasets' / ds_name / 'cases.jsonl'
    short = 'dev' if 'dev' in ds_name else 'int'
    out_path = PROJECT / 'phase5_audit' / f'phase5_v2_{short}_results.csv'

    cases = []
    with open(cases_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip(): cases.append(json.loads(line.strip()))

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['case_id','dataset_id','entity_a_id','entity_b_id',
                         'ophthalmic_drug','ophthalmic_class','ophthalmic_flags',
                         'systemic_drug','systemic_class','systemic_flags',
                         'ddinter_level','system_level','rule_triggered','matched_rules'])

        for c in cases:
            a = entities_a.get(c['entity_a_id'])
            b = entities_b.get(c['entity_b_id'])
            if not a or not b: continue

            assessment = engine.evaluate(a, b, c.get('patient_factors', []))
            triggered = len(assessment.signals) > 0
            matched = '|'.join([s.rule_id for s in assessment.signals])
            system_level = assessment.risk_level.value

            ra = rows_a.get(c['entity_a_id'], {})
            rb = rows_b.get(c['entity_b_id'], {})

            writer.writerow([
                c['case_id'], c['dataset_id'], c['entity_a_id'], c['entity_b_id'],
                ra.get('primary_name', ''),
                ra.get('category', ''),
                ra.get('flags', ''),
                rb.get('generic_name', ''),
                rb.get('drug_class', ''),
                rb.get('flags', ''),
                c['gold_risk_level'], system_level,
                str(triggered), matched
            ])

    print(f'{ds_name}: {len(cases)} cases -> {out_path.name}')

print('Done.')
