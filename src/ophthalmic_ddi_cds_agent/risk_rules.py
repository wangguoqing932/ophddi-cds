"""Deterministic rule evaluation for ophthalmic-systemic interaction screening."""
from __future__ import annotations
import hashlib
from pathlib import Path
import yaml
from .schemas import RiskAssessment, RiskLevel, RiskSignal, RISK_ORDER

class RuleEngine:
    def __init__(self, rules_path: Path) -> None:
        self.rules_path=rules_path
        self.config=yaml.safe_load(rules_path.read_text(encoding='utf-8'))
        self.sha256=hashlib.sha256(rules_path.read_bytes()).hexdigest()
        self.levels={key:RiskLevel(key) for key in self.config['risk_levels']}
    def _signal(self, rule_id: str, spec: dict, risk_type: str, matched_terms: dict[str, list[str]]) -> RiskSignal:
        policy = spec['evidence_policy']
        return RiskSignal(
            rule_id=rule_id,
            risk_level=RiskLevel(spec['severity']),
            risk_type=risk_type,
            rationale=spec['rationale'],
            recommendation=spec['recommendation'],
            matched_terms=matched_terms,
            rules_yaml_sha256=self.sha256,
            output_class=policy['output_class'],
            support_tier=policy['support_tier'],
            action_behavior=policy['action_behavior'],
            claim_scope=policy['claim_scope'],
            verified_citation_ids=policy.get('verified_citation_ids', []),
        )
    def evaluate(self, entity_a: object, entity_b: object, patient_factors: list[str]=[]) -> RiskAssessment:
        a_flags=set(entity_a.flags); b_flags=set(entity_b.flags); signals=[]
        for rule in self.config['rules']:
            a_f=set(rule.get('entity_a_flags',[])); b_f=set(rule.get('entity_b_flags',[]))
            if rule.get('match') == 'all':
                a_ok = a_f <= a_flags if a_f else True
                b_ok = b_f <= b_flags if b_f else True
            else:
                a_ok = bool(a_f & a_flags)
                b_ok = bool(b_f & b_flags)
            if a_ok and b_ok:
                signals.append(self._signal(rule['id'], rule, rule['risk_type'], {'entity_a_flags':sorted(set(rule['entity_a_flags'])&a_flags),'entity_b_flags':sorted(set(rule['entity_b_flags'])&b_flags)}))
        for factor in patient_factors:
            spec=self.config.get('patient_factor_rules',{}).get(factor)
            if not spec: continue
            required_a=set(spec.get('matching_entity_a_flags',[])); required_b=set(spec.get('matching_entity_b_flags',[]))
            if required_a <= a_flags and required_b <= b_flags:
                signals.append(self._signal(f'patient_factor:{factor}', spec, 'patient_factor', {'patient_factor':[factor]}))
        signals.sort(key=lambda item:(-RISK_ORDER[item.risk_level],item.rule_id))
        if signals:
            level=signals[0].risk_level
            return RiskAssessment(risk_level=level,risk_types=sorted({item.risk_type for item in signals}),signals=signals,confidence='rule_based',confidence_score=1.0)
        # G19 hard constraint: low/very-low absorption + no rules matched -> deterministic low
        if 'systemic_absorption_low' in a_flags or 'systemic_absorption_very_low' in a_flags:
            signals.append(RiskSignal(
                rule_id='g19_hard_constraint',
                risk_level=RiskLevel.LOW,
                risk_type='hard_constraint',
                rationale=('Ophthalmic drug has LOW systemic absorption and NO interaction rules matched. '
                           'Risk assessment MUST be "low". Do NOT extrapolate from systemic-route data.'),
                recommendation='No interaction-specific monitoring required.',
                matched_terms={'entity_a_flags': sorted(a_flags)},
                rules_yaml_sha256=self.sha256,
                output_class='insufficient_evidence',
                support_tier='none',
                action_behavior='no_ddi_conclusion',
            ))
            return RiskAssessment(risk_level=RiskLevel.LOW, risk_types=['hard_constraint'], signals=signals,
                                  confidence='hard_constraint', confidence_score=1.0)
        return RiskAssessment(risk_level=RiskLevel.UNKNOWN, risk_types=[], signals=[],
                              confidence='low', confidence_score=0.0)
