"""Durable project-owned checkpoints for resumable LightRAG builds."""
from __future__ import annotations
import json,os,time
from datetime import UTC,datetime
from pathlib import Path

def utc_now()->str:return datetime.now(UTC).isoformat()
def atomic_json(path:Path,data:dict)->None:
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
 for attempt in range(5):
  try:
   tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,path);return
  except PermissionError:
   time.sleep(0.2*(2**attempt))
 raise RuntimeError(f'cannot atomically write {path}')
def load(path:Path)->dict:return json.loads(path.read_text(encoding='utf-8'))
def summary(state:dict)->dict:
 docs=state['documents'];counts={name:0 for name in ('pending','running','completed','terminal_failed')}
 for item in docs:counts[item['status']]=counts.get(item['status'],0)+1
 return counts
