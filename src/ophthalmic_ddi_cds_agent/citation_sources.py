"""Cache-backed metadata providers used by the strict Phase 3 citation gate."""
from __future__ import annotations
import hashlib,json
from datetime import UTC,datetime
from pathlib import Path
from urllib.parse import quote
import requests

PARSER_VERSION='phase3-citation-sources-v1'
class CitationSources:
 def __init__(self,root:Path,mode:str='cache-only'):
  self.root=root;self.mode=mode;self.base=root/'data/raw/evidence/citations'
 def get(self,provider:str,key:str,url:str):
  path=self.base/provider/(hashlib.sha256((key+'|'+url).encode()).hexdigest()+'.json')
  if path.exists():
   raw=path.read_bytes();return json.loads(raw),{'provider':provider,'url':url,'cache_path':str(path.relative_to(self.root)),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':'cached'}
  if self.mode=='cache-only':raise FileNotFoundError(f'missing citation cache {provider}:{key}')
  response=requests.get(url,timeout=45,headers={'User-Agent':'ophthalmic-ddi-cds/0.1 (mailto:registry@example.invalid)'})
  response.raise_for_status();raw=response.content;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  return response.json(),{'provider':provider,'url':response.url,'cache_path':str(path.relative_to(self.root)),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':datetime.now(UTC).isoformat()}
 def crossref(self,doi):return self.get('crossref',doi,f'https://api.crossref.org/works/{quote(doi,safe="/")}')
 def openalex(self,doi):return self.get('openalex',doi,f'https://api.openalex.org/works/https://doi.org/{quote(doi,safe="/")}')
 def pubmed(self,pmid):
  url=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml'
  path=self.base/'pubmed_citation'/(hashlib.sha256((pmid+'|'+url).encode()).hexdigest()+'.xml')
  if path.exists():
   raw=path.read_bytes();return raw,{'provider':'pubmed_citation','url':url,'cache_path':str(path.relative_to(self.root)),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':'cached'}
  if self.mode=='cache-only':raise FileNotFoundError(f'missing citation cache pubmed:{pmid}')
  response=requests.get(url,timeout=45,headers={'User-Agent':'ophthalmic-ddi-cds/0.1 (mailto:registry@example.invalid)'})
  response.raise_for_status();raw=response.content;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  return raw,{'provider':'pubmed_citation','url':response.url,'cache_path':str(path.relative_to(self.root)),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':datetime.now(UTC).isoformat()}
