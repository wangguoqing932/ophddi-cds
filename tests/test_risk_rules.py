from pathlib import Path
import csv
import yaml

from ophthalmic_ddi_cds_agent.risk_rules import RuleEngine
from ophthalmic_ddi_cds_agent.schemas import EntityA, EntityB

ROOT = Path(__file__).resolve().parents[1]


def entity_a(name: str) -> EntityA:
    with (ROOT / 'data/seed/entities_a.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['primary_name'] == name:
                return EntityA(entity_a_id=row['topical_ophthalmic_medications_id'], primary_name=name, canonical_name=name, aliases=row['aliases'].split('|') if row['aliases'] else [], category=row['category'], active_mechanisms=row['active_mechanisms'].split('|') if row['active_mechanisms'] else [], flags=row['flags'].split('|') if row['flags'] else [], evidence_sources=row['evidence_sources'].split('|') if row['evidence_sources'] else [])
    raise AssertionError(name)


def entity_b(name: str) -> EntityB:
    with (ROOT / 'data/seed/entities_b.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['generic_name'] == name:
                return EntityB(entity_b_id=row['entity_b_id'], generic_name=name, canonical_name=name, aliases=[], drug_class=row['drug_class'], flags=row['flags'].split('|') if row['flags'] else [])
    raise AssertionError(name)


def test_all_rules_and_patient_factors_have_safe_policy() -> None:
    config = yaml.safe_load((ROOT / 'configs/rules.yaml').read_text(encoding='utf-8'))
    assert len(config['rules']) == 40
    assert len(config['patient_factor_rules']) == 3
    
    # Verify DDI rules
    for spec in config['rules']:
        policy = spec['evidence_policy']
        assert policy['output_class'] in {'clinical_ddi', 'precaution', 'theoretical_mechanism', 'insufficient_evidence'}
        if policy['output_class'] in {'theoretical_mechanism', 'insufficient_evidence'}:
            assert policy['action_behavior'] in {'informational_only', 'no_ddi_conclusion'}
            assert 'avoid' not in spec['recommendation'].casefold()
        assert len(spec.get('citations', [])) >= 1, f"Rule {spec['id']} has no citations"
        assert spec['severity'] in {'high', 'medium', 'low', 'unknown'}
        assert len(spec.get('entity_a_flags', [])) >= 1
        assert len(spec.get('entity_b_flags', [])) >= 1
    
    # Verify patient factor rules (different structure — no evidence_policy)
    for pf_id, pf in config['patient_factor_rules'].items():
        assert pf['severity'] in {'high', 'medium', 'low', 'unknown'}
        assert len(pf.get('citations', [])) >= 1
        has_a = len(pf.get('matching_entity_a_flags', [])) >= 1
        has_b = len(pf.get('matching_entity_b_flags', [])) >= 1
        assert has_a or has_b, f"Patient factor {pf_id} has no matching flags"


def test_scoped_beta_blockade_and_contextual_precaution() -> None:
    engine = RuleEngine(ROOT / 'configs/rules.yaml')
    # additive_beta_blockade is Tier 0A: clinical_ddi + scoped_clinical_review (v0.1)
    beta = next(item for item in engine.evaluate(entity_a('Timolol'), entity_b('Metoprolol')).signals if item.rule_id == 'additive_beta_blockade')
    assert beta.output_class == 'clinical_ddi'
    assert beta.action_behavior == 'scoped_clinical_review'
    # additive_alpha2_cns_depression is Tier 0B: precaution (v0.1)
    brimonidine = next(item for item in engine.evaluate(entity_a('Brimonidine'), entity_b('Fentanyl')).signals if item.rule_id == 'additive_alpha2_cns_depression')
    assert brimonidine.output_class == 'precaution'
    assert brimonidine.action_behavior == 'precautionary_review'
    # cai_diuretic_metabolic_acidosis triggers between Dorzolamide (cai_topical) and HCTZ (diuretic)
    dorzolamide_hctz = next(item for item in engine.evaluate(entity_a('Dorzolamide'), entity_b('Hydrochlorothiazide')).signals if item.rule_id == 'cai_diuretic_metabolic_acidosis')
    assert dorzolamide_hctz.output_class in {'theoretical_mechanism', 'precaution'}
    assert dorzolamide_hctz.risk_type == 'pharmacokinetic_metabolic'
    # systemic_absorption_high_risk triggers between Timolol (sys_abs_high) and Metoprolol (beta_blocker_systemic)
    timolol_metoprolol = engine.evaluate(entity_a('Timolol'), entity_b('Metoprolol'))
    high_abs = next((s for s in timolol_metoprolol.signals if s.rule_id == 'systemic_absorption_high_risk'), None)
    assert high_abs is not None, "systemic_absorption_high_risk should trigger for Timolol+Metoprolol"
    assert high_abs.output_class == 'theoretical_mechanism'
    # patient factor: elderly only triggers when passed in patient_factors param AND entity_b has NTI flag
    timolol_warfarin_elderly = engine.evaluate(entity_a('Timolol'), entity_b('Warfarin'), patient_factors=['elderly'])
    elderly_signal = next((s for s in timolol_warfarin_elderly.signals if s.rule_id == 'patient_factor:elderly'), None)
    assert elderly_signal is not None, "Elderly patient factor should trigger when passed + Warfarin has NTI flag"
    assert elderly_signal.output_class == 'precaution'
