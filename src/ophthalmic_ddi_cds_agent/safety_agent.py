"""Rule-first safety agent with evidence-linked reports."""
from __future__ import annotations
from pathlib import Path
from .evidence_store import EvidenceStore
from .normalize import normalize_medication
from .kg_layer import PreciseKG
from .risk_rules import RuleEngine
from .schemas import RiskAssessment, RiskLevel, SafetyReport, RISK_ORDER
class SafetyAgentConfig:
 def __init__(self, project_root: Path): self.project_root=project_root
class SafetyAgent:
 def __init__(self, config: SafetyAgentConfig):
  import csv
  from .schemas import EntityA,EntityB
  root=config.project_root
  with (root/'data/seed/entities_a.csv').open(encoding='utf-8',newline='') as f:self.a=[EntityA(entity_a_id=r.pop('topical_ophthalmic_medications_id'),aliases=r['aliases'].split('|') if r['aliases'] else [],active_mechanisms=r['active_mechanisms'].split('|') if r['active_mechanisms'] else [],flags=r['flags'].split('|') if r['flags'] else [],components=r['components'].split('|') if r['components'] else [],evidence_sources=r['evidence_sources'].split('|') if r['evidence_sources'] else [],**{k:v for k,v in r.items() if k not in {'aliases','active_mechanisms','flags','components','evidence_sources'}}) for r in csv.DictReader(f)]
  with (root/'data/seed/entities_b.csv').open(encoding='utf-8',newline='') as f:self.b=[EntityB(aliases=r['aliases'].split('|') if r['aliases'] else [],flags=r['flags'].split('|') if r['flags'] else [],metabolic_pathways=r['metabolic_pathways'].split('|') if r['metabolic_pathways'] else [],transporter_substrates=r['transporter_substrates'].split('|') if r['transporter_substrates'] else [],**{k:v for k,v in r.items() if k not in {'aliases','flags','metabolic_pathways','transporter_substrates'}}) for r in csv.DictReader(f)]
  self.engine=RuleEngine(root/'configs/rules.yaml');self.evidence=EvidenceStore(root/'data/seed/evidence_chunks.jsonl');self.kg=PreciseKG()
 def assess(self, entity_a:str, entity_b:str, patient_factors:list[str]|None=None)->SafetyReport:
  ar=normalize_medication(entity_a,self.a,route='ophthalmic');br=normalize_medication(entity_b,self.b,route='systemic')
  if not ar.canonical_name or not br.canonical_name: raise ValueError('Unknown or ambiguous medication')
  a=next(x for x in self.a if x.canonical_name==ar.canonical_name);b=next(x for x in self.b if x.canonical_name==br.canonical_name)
  assessment=self.engine.evaluate(a,b,patient_factors or [])
  v2_level,_,_=self.kg.deterministic_level_v2(entity_a,entity_b)
  if v2_level and RISK_ORDER[RiskLevel(v2_level)]>RISK_ORDER[assessment.risk_level]:
   assessment=RiskAssessment(risk_level=RiskLevel(v2_level),risk_types=assessment.risk_types,signals=assessment.signals,confidence='cascade_v2',confidence_score=1.0)
  evidence=[]
  for signal in assessment.signals:
   if signal.rule_id.startswith('patient_factor:'):continue
   hits=self.evidence.search(entity_a=a.entity_a_id,entity_b=b.entity_b_id,rule_id=signal.rule_id) or self.evidence.search(rule_id=signal.rule_id)
   selected=hits[:3]; signal.evidence_ids=[item.evidence_id for item in selected]
   signal.citations=list(signal.verified_citation_ids)
   evidence.extend(selected)
  dedup={x.evidence_id:x for x in evidence}
  report_text='Rule-based screening result. Clinical review required.'
  return SafetyReport(case_id='interactive',entity_a=a.primary_name,entity_b=b.generic_name,patient_factors=patient_factors or [],risk_assessment=assessment,evidence=list(dedup.values()),report_text=report_text,metadata={'rules_yaml_sha256':self.engine.sha256,'citation_report_mode':'strict-policy-cache-replay'})
