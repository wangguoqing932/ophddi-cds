"""Bounded diagnostics for the exact LightRAG extraction LLM configuration."""
from __future__ import annotations
import argparse,asyncio,json,sys,time
from pathlib import Path
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1];load_dotenv(ROOT/'.env');sys.path.insert(0,str(ROOT/'src'))
from ophthalmic_ddi_cds_agent.llm_config import LLMSettings

from types import SimpleNamespace

class DummyKV:
 def __init__(self,model):self.global_config={'llm_model_name':model}

async def call(label:str,prompt:str,system:str|None,settings:LLMSettings):
 from lightrag.llm.openai import openai_complete
 started=time.monotonic()
 try:
  result=await openai_complete(prompt,system_prompt=system,timeout=180,model=settings.model,hashing_kv=object())
  return {'probe':label,'status':'ok','elapsed_seconds':round(time.monotonic()-started,2),'response_length':len(str(result))}
 except Exception as exc:
  return {'probe':label,'status':'error','elapsed_seconds':round(time.monotonic()-started,2),'error_type':type(exc).__name__,'message':str(exc)[:200]}
async def main_async():
 settings=LLMSettings.from_env();settings.apply()
 sample=json.loads(next(x for x in (ROOT/'data/seed/evidence_chunks.jsonl').read_text(encoding='utf-8').splitlines() if x))['text'][:800]
 extraction_system='Extract at most five entities and relationships. Return concise plain text.'
 probes=[
  await call('ordinary','Reply only with OK.',None,settings),
  await call('minimal_extraction','Timolol ophthalmic drops may cause bradycardia with systemic beta-blockers.',extraction_system,settings),
  await call('evidence_excerpt',sample,extraction_system,settings),
 ]
 print(json.dumps({'settings':settings.sanitized(),'probes':probes},ensure_ascii=False))
 raise SystemExit(0 if all(item['status']=='ok' for item in probes) else 1)
def main():asyncio.run(main_async())
if __name__=='__main__':main()
