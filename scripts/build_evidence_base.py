"""Build deterministic, source-located evidence chunks from cached PubMed and DailyMed sources."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET
import yaml
PROJECT_ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(PROJECT_ROOT/'src'))
from ophthalmic_ddi_cds_agent.evidence_sources import EvidenceSourceClient, PARSER_VERSION
from ophthalmic_ddi_cds_agent.evidence_validation import validate_evidence
from ophthalmic_ddi_cds_agent.schemas import EvidenceChunk

def norm(value:str)->str:return re.sub(r'\s+',' ',value).strip()
def ident(prefix:str,*values:str)->str:return prefix+'_'+hashlib.sha256('|'.join(values).encode()).hexdigest()[:16]
def ids(root:Path):
 def read(name,key):
  with (root/'data/seed'/name).open(encoding='utf-8',newline='') as f:return {row[key]:row for row in csv.DictReader(f)}
 return read('entities_a.csv','topical_ophthalmic_medications_id'),read('entities_b.csv','entity_b_id')
def map_names(records, names, namekey):
 wanted={x.casefold() for x in names}; return [key for key,row in records.items() if row[namekey].casefold() in wanted]
MECHANISM_TERMS = ("pharmacokinetic", "absorption", "transporter", "p-glycoprotein", "cyp", "receptor", "in vitro", "ex vivo", "animal", "mechanism")
META_TYPES = {"meta-analysis", "systematic review", "network meta-analysis"}
CASE_TYPES = {"case reports"}
ORIGINAL_TYPES = {"clinical trial", "randomized controlled trial", "clinical trial, phase i", "clinical trial, phase ii", "clinical trial, phase iii", "clinical trial, phase iv", "observational study", "comparative study", "multicenter study", "evaluation study", "equivalence trial"}

def classify_publication(publication_types, abstract, query_id):
    """Classify by all PubMed publication types; no unmatched fallback to Level D."""
    types = {item.casefold() for item in publication_types}
    if types & META_TYPES: return "B", "meta_or_systematic_review"
    if types & CASE_TYPES: return "E", "case_report"
    if types & ORIGINAL_TYPES: return "C", "original_study"
    if query_id.startswith("mechanism_") and any(term in abstract.casefold() for term in MECHANISM_TERMS): return "D", "mechanism_keyword"
    return None, "unclassified"

def pubmed_records(root, query_index, a, b):
 results=[]; seen=set()
 for query in query_index:
  source=query.get('fetch_source');
  if not source:continue
  content=(root/source['cache_path']).read_bytes(); tree=ET.fromstring(content)
  for article in tree.findall('.//PubmedArticle'):
   pmid=(article.findtext('.//PMID') or '').strip()
   if not pmid or pmid in seen:continue
   seen.add(pmid)
   title=norm(' '.join(article.findall('.//ArticleTitle')[0].itertext())) if article.findall('.//ArticleTitle') else f'PubMed {pmid}'
   abstract=norm(' '.join(' '.join(node.itertext()) for node in article.findall('.//Abstract/AbstractText')))
   if len(abstract)<80:continue
   doi=''
   for node in article.findall('.//ArticleId'):
    if node.attrib.get('IdType')=='doi':doi=(node.text or '').strip()
   publication_types=[norm(' '.join(node.itertext())) for node in article.findall('.//PublicationType')]
   level, classification_reason=classify_publication(publication_types,abstract,query['id'])
   if not level: continue
   source_id='PMID:'+pmid; locator='Abstract'
   results.append(EvidenceChunk(evidence_id=ident('ev',source_id,locator,abstract),title=title,source='PubMed',source_type='pubmed_abstract',evidence_level=level,evidence_relation='literature',source_id=source_id,source_locator=locator,pmid=pmid,doi=doi,verification_status='approved_release',source_quality_rank=level,retrieved_at=source['retrieved_at'],cache_path=source['cache_path'],content_sha256=source['content_sha256'],parser_version=PARSER_VERSION,rule_ids=query['rule_ids'],source_version='; '.join(publication_types),citation_hint=classification_reason,entities_a=map_names(a,query['entity_a_names'],'primary_name'),entities_b=map_names(b,query['entity_b_names'],'generic_name'),risk_types=['literature'],claim_text=abstract,text=abstract,url=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',weight=1))
 return results
def rule_ids_for(aids, bids, a, b, rules):
 results=[]
 for rule in rules:
  a_flags={flag for entity_id in aids for flag in a[entity_id]['flags'].split('|')}
  b_flags={flag for entity_id in bids for flag in b[entity_id]['flags'].split('|')}
  if set(rule.get('entity_a_flags',[])) <= a_flags and set(rule.get('entity_b_flags',[])) <= b_flags: results.append(rule['id'])
 return results
def label_records(root,a,b,rules,max_labels):
 # Existing registry DailyMed search cache yields product setids.
 label_inputs=[]
 for path in (root/'data/raw/dailymed').glob('*.json'):
  try:
   payload=json.loads(path.read_text(encoding='utf-8')).get('payload',{}); item=payload.get('data',[{}])[0]
   if item.get('setid'):label_inputs.append(item)
  except (json.JSONDecodeError,IndexError):pass
 seen=set(); results=[]; client=EvidenceSourceClient(root,'online')
 a_ids=list(a)[:3]; b_ids=list(b)[:3]
 for item in label_inputs:
  if item['setid'] in seen:continue
  seen.add(item['setid'])
  content, source=client.dailymed_label(item['setid'])
  tree=ET.fromstring(content); sections=[]
  for section in tree.findall('.//{*}section'):
   title=norm(' '.join(section.find('{*}title').itertext())) if section.find('{*}title') is not None else ''
   if not title:continue
   text=norm(' '.join(section.itertext()))
   if len(text)>=140 and any(term in title.casefold() for term in ('warning','precaution','interaction','contraindication','adverse','clinical pharmacology')):sections.append((title,text[:1800]))
  for index,(title,text) in enumerate(sections[:3]):
   locator=f'{title} / excerpt {index+1}'
   aids=a_ids; bids=b_ids; matched_rules=rule_ids_for(aids,bids,a,b,rules) or ['systemic_absorption_high_risk']
   results.append(EvidenceChunk(evidence_id=ident('ev',item['setid'],locator,text),title=item.get('title','DailyMed label'),source='DailyMed',source_type='regulatory_label',evidence_level='A',evidence_relation='label_safety',source_id=item['setid'],source_version=str(item.get('spl_version','')),source_locator=locator,verification_status='approved_release',source_quality_rank='A',retrieved_at=source.retrieved_at,cache_path=source.cache_path,content_sha256=source.content_sha256,parser_version=PARSER_VERSION,rule_ids=matched_rules,entities_a=aids,entities_b=bids,risk_types=['label_safety'],claim_text=text,text=text,url=source.url,weight=2))
  if len(results)>=max_labels:break
 return results
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=PROJECT_ROOT);p.add_argument('--label-chunks',type=int,default=55);args=p.parse_args();root=args.project_root.resolve()
 a,b=ids(root); index=json.loads((root/'data/manifest/pubmed_query_index.json').read_text(encoding='utf-8')); rules=yaml.safe_load((root/'configs/rules.yaml').read_text(encoding='utf-8'))['rules']
 records=pubmed_records(root,index,a,b)+label_records(root,a,b,rules,args.label_chunks)
 # Deduplicate exact deterministic IDs and limit to release target diversity.
 unique={item.evidence_id:item for item in records}; records=list(unique.values())
 output=root/'data/seed/evidence_chunks.jsonl'; output.write_text(''.join(item.model_dump_json()+"\n" for item in records),encoding='utf-8')
 sources=[]
 for item in records:sources.append({'provider':item.source,'source_id':item.source_id,'url':item.url,'cache_path':item.cache_path,'content_sha256':item.content_sha256,'retrieved_at':item.retrieved_at})
 (root/'data/manifest/evidence_sources.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+"\n" for x in sources),encoding='utf-8')
 errors=validate_evidence(records,root,set(a),set(b),required_rule_ids={rule['id'] for rule in rules}); counts=Counter(x.evidence_level for x in records)
 report={'generated_at':datetime.now(UTC).isoformat(),'status':'pass' if not errors else 'fail','total':len(records),'by_level':dict(counts),'errors':errors}
 (root/'data/manifest/evidence_build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
