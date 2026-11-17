"""Execute Phase 3 hard citation gate and persist its outcome."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
result=subprocess.run([sys.executable,str(root/'scripts/verify_rule_citations.py'),'--project-root',str(root)])
report=json.loads((root/'outputs/citation_verification_report.json').read_text(encoding='utf-8'));progress=json.loads((root/'.executor/progress.json').read_text(encoding='utf-8'));state=json.loads((root/'.medical-agent/state.json').read_text(encoding='utf-8'))
phase={'status':'completed' if result.returncode==0 else 'blocked','citation_report':'outputs/citation_verification_report.json','rules_yaml_sha256':report['rules_yaml_sha256'],'rule_count':14,'patient_factor_count':3,'verification_status':report['overall']};progress['phase3']=phase
if result.returncode==0:
 state['completed']=list(dict.fromkeys([*state['completed'],'executor.phase3']));state['in_progress']='executor.phase4';state['blocked']=[x for x in state.get('blocked',[]) if x.get('phase')!='executor.phase3']
else:
 state['completed']=[x for x in state['completed'] if x!='executor.phase3'];state['in_progress']='executor.phase3';state['blocked']=[{'phase':'executor.phase3','reason':'strict citation verification failed; see outputs/citation_verification_report.json'}]
(root/'.executor/progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(root/'.medical-agent/state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');raise SystemExit(result.returncode)
