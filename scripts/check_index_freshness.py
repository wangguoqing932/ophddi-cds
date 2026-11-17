"""Fail-closed Phase 4 freshness check."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[1]);args=p.parse_args();root=args.project_root.resolve()
 progress=json.loads((root/'.executor/progress.json').read_text(encoding='utf-8')); phases=progress.get('phases',{}); phase3=phases.get('phase3',{});phase4=phases.get('phase4',{})
 rules=digest(root/'configs/rules.yaml'); evidence=digest(root/'data/seed/evidence_chunks.jsonl'); sources=digest(root/'data/manifest/evidence_sources.jsonl');errors=[]
 report_path=root/phase3.get('citation_report','outputs/citation_verification_report.json')
 report=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
 if phase3.get('status')!='completed' or not phase3.get('citations_verified'):errors.append('phase3 not verified')
 if report.get('overall')!='pass':errors.append('citation report not pass')
 if not (rules==phase3.get('rules_yaml_sha256')==report.get('rules_yaml_sha256')==phase4.get('index_built_against_rules_sha256')):errors.append('rules SHA mismatch')
 if phase4.get('evidence_chunks_sha256')!=evidence:errors.append('evidence chunks SHA mismatch')
 if phase4.get('evidence_sources_sha256')!=sources:errors.append('evidence sources SHA mismatch')
 index=root/phase4.get('index_root','data/processed/lightrag_index');manifest=index/'index_manifest.json'
 if not manifest.exists():errors.append('index manifest missing')
 else:
  manifest_data=json.loads(manifest.read_text(encoding='utf-8'))
  if manifest_data.get('input_fingerprint')!=phase4.get('input_fingerprint'):errors.append('index manifest fingerprint mismatch')
  state_path=index/'build_state.json'
  if not state_path.exists():errors.append('build state missing')
  else:
   state=json.loads(state_path.read_text(encoding='utf-8'))
   if state.get('status')!='promoted':errors.append('build state not promoted')
   if state.get('input_fingerprint')!=manifest_data.get('input_fingerprint'):errors.append('build state fingerprint mismatch')
 if phase4.get('status')!='completed' or phase4.get('documents_failed') or phase4.get('smoke_tests',{}).get('status')!='pass':errors.append('index build incomplete')
 print(json.dumps({'fresh':not errors,'errors':errors},ensure_ascii=False));raise SystemExit(0 if not errors else 1)
if __name__=='__main__':main()
