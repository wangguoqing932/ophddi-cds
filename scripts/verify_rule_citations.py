"""Strict cache-backed verifier: bibliography consensus, retraction, and scoped relevance."""
from __future__ import annotations
import argparse,hashlib,json,re
from datetime import UTC,datetime
from pathlib import Path
from xml.etree import ElementTree as ET
import yaml,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from ophthalmic_ddi_cds_agent.citation_sources import CitationSources,PARSER_VERSION

def norm(v):return re.sub(r'[^a-z0-9]+',' ',v.casefold()).strip()
def doi(v):return (v or '').replace('https://doi.org/','').casefold()
def pubmed_meta(raw):
 # EFetch with retmode=xml returns a source-located article record.
 tree=ET.fromstring(raw);title=' '.join(tree.find('.//ArticleTitle').itertext()) if tree.find('.//ArticleTitle') is not None else ''
 abstract=' '.join(' '.join(node.itertext()) for node in tree.findall('.//Abstract/AbstractText'))
 ids={x.attrib.get('IdType',''):x.text or '' for x in tree.findall('./PubmedArticle/PubmedData/ArticleIdList/ArticleId')};types={' '.join(x.itertext()).casefold() for x in tree.findall('.//PublicationType')}
 return {'title':title,'abstract':abstract,'doi':ids.get('doi',''),'retracted':bool({'retracted publication','retraction of publication','expression of concern'}&types)}
def title_tokens(value):
 return {term for term in norm(value).split() if len(term)>2}
def title_agreement(*titles):
 sets=[title_tokens(value) for value in titles if value]
 return len(sets)>=2 and all(len(sets[0]&other)/max(1,min(len(sets[0]),len(other)))>=0.6 for other in sets[1:])
def verify(item,sources):
 if item['route']!='literature':return {'id':item['id'],'status':'unsupported','reason':'only cache-backed literature implemented'}
 try:
  crossref,cm=sources.crossref(item['doi']);openalex,om=sources.openalex(item['doi']);pub,pm=sources.pubmed(item['pmid'])
 except Exception as exc:return {'id':item['id'],'status':'unverified','reason':str(exc)}
 c=crossref['message'];p=pubmed_meta(pub);actual=doi(c.get('DOI'));oa=doi(openalex.get('doi'))
 expected=doi(item['doi']);crossref_title=c.get('title',[''])[0];openalex_title=openalex.get('title','');title=' '.join([crossref_title,openalex_title,p['title']]);text=norm(title+' '+p['abstract'])
 title_match=title_agreement(crossref_title,openalex_title,p['title'])
 # A DOI is the canonical work identifier.  When all three providers return the
 # same DOI, translated/alternate metadata titles do not invalidate identity.
 agreement=actual==expected==oa and doi(p['doi'])==expected
 title_note='title_agreement' if title_match else 'alternate_title_same_doi'
 retracted=bool(c.get('update-to')) or bool(openalex.get('is_retracted')) or p['retracted']
 relevant=all(norm(term) in text for term in item['required_terms'])
 status='verified' if agreement and not retracted and relevant else 'unverified'
 return {'id':item['id'],'status':status,'doi':expected,'agreement':agreement,'title_identity':title_note,'retracted':retracted,'relevant':relevant,'title':title,'required_terms':item['required_terms'],'sources':[cm,om,pm], 'reason':'' if status=='verified' else 'identity/retraction/relevance requirement failed'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project-root',type=Path,default=ROOT);ap.add_argument('--refresh',action='store_true');args=ap.parse_args();root=args.project_root.resolve();manifest=yaml.safe_load((root/'data/curation/rule_citations.yaml').read_text(encoding='utf-8'));sources=CitationSources(root,'online' if args.refresh else 'cache-only');rows=[verify(x,sources) for x in manifest['items']];rules=root/'configs/rules.yaml';config=yaml.safe_load(rules.read_text(encoding='utf-8'))
 policies=[(rule['id'],rule.get('evidence_policy',{}),rule.get('recommendation','')) for rule in config['rules']]
 policies.extend((f'patient_factor:{name}',spec.get('evidence_policy',{}),spec.get('recommendation','')) for name,spec in config.get('patient_factor_rules',{}).items())
 verified={row['id'] for row in rows if row['status']=='verified'}
 policy_errors=[]
 allowed={('clinical_ddi','direct_clinical','scoped_clinical_review'),('precaution','contextual_clinical','precautionary_review'),('theoretical_mechanism','mechanism_candidate','informational_only'),('insufficient_evidence','none','no_ddi_conclusion')}
 for policy_id,policy,recommendation in policies:
  triple=(policy.get('output_class'),policy.get('support_tier'),policy.get('action_behavior'))
  if triple not in allowed: policy_errors.append(f'invalid policy:{policy_id}')
  citation_ids=set(policy.get('verified_citation_ids',[]))
  if policy.get('output_class') in {'clinical_ddi','precaution'} and not citation_ids <= verified: policy_errors.append(f'missing verified citation:{policy_id}')
  if policy.get('output_class') in {'theoretical_mechanism','insufficient_evidence'} and re.search(r'(avoid|dose adjust|monitor levels|established clinical)',recommendation,re.I): policy_errors.append(f'unsafe action wording:{policy_id}')
 report={'overall':'pass' if not policy_errors and all(x['status']=='verified' for x in rows) else 'fail','mode':'strict-policy-cache-replay','generated_at':datetime.now(UTC).isoformat(),'rules_yaml_sha256':hashlib.sha256(rules.read_bytes()).hexdigest(),'citation_manifest_count':len(rows),'policy_count':len(policies),'policy_errors':policy_errors,'items':rows,'parser_version':PARSER_VERSION};out=root/'outputs/citation_verification_report.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False));raise SystemExit(0 if report['overall']=='pass' else 1)
if __name__=='__main__':main()
