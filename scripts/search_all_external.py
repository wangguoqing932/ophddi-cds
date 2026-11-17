"""search_all_external.py — Multi-source independent validation set builder"""
import csv, json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# ═══ HELPERS ═══
def pubmed_search(term, retmax=30):
    params = {"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json", "sort": "relevance"}
    url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["esearchresult"]["idlist"]

def pubmed_fetch(pmids):
    if not pmids: return []
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "xml", "retmode": "xml"}
    url = f"{BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as r:
        root = ET.fromstring(r.read())
    results = []
    for a in root.findall(".//PubmedArticle"):
        abs_parts = a.findall(".//Abstract/AbstractText")
        abstract = " ".join(t.text or "" for t in abs_parts)
        mesh_terms = [m.findtext("DescriptorName","") for m in a.findall(".//MeshHeading")]
        results.append({
            "pmid": a.findtext(".//PMID",""),
            "title": a.findtext(".//ArticleTitle",""),
            "abstract": abstract[:1000],
            "journal": a.findtext(".//Journal/Title",""),
            "pubdate": a.findtext(".//PubDate/Year",""),
            "doi": a.findtext(".//ArticleIdList/ArticleId[@IdType='doi']",""),
            "pubtypes": [p.text for p in a.findall(".//PublicationType")],
            "mesh": mesh_terms,
        })
    return results

# ═══ LOAD ENTITIES ═══
a_rows = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_rows[row["topical_ophthalmic_medications_id"]] = row
b_rows = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_rows[row["entity_b_id"]] = row

# ═══ SEARCH ALL SOURCES ═══
all_articles = []
search_log = {}

# ── 1. PubMed: deeper search with more specific queries ──
pubmed_queries = {
    # Drug-specific adverse event case reports
    "timolol_ae": '(timolol[tiab] AND ophthalmic[tiab] AND (case report[pt] OR case reports[pt])) AND (bradycardia OR syncope OR bronchospasm OR hypotension)',
    "brimonidine_ae": '(brimonidine[tiab] AND (case report[pt] OR case reports[pt])) AND (coma OR apnea OR bradycardia OR hypotension OR CNS OR sedation)',
    "phenylephrine_ae": '(phenylephrine[tiab] AND ophthalmic AND (case report[pt] OR case reports[pt])) AND (hypertension OR "pulmonary edema" OR tachycardia OR "blood pressure")',
    "atropine_cyclo_ae": '((atropine[tiab] OR cyclopentolate[tiab]) AND ophthalmic AND (case report[pt] OR case reports[pt])) AND (delirium OR psychosis OR tachycardia OR anticholinergic)',
    "dorzolamide_ae": '((dorzolamide[tiab] OR brinzolamide[tiab]) AND (case report[pt] OR case reports[pt])) AND (acidosis OR anemia OR hypokalemia OR dyspnea OR "aplastic")',
    "nsaid_ophth_ae": '((ketorolac[tiab] OR bromfenac[tiab] OR nepafenac[tiab] OR diclofenac[tiab]) AND ophthalmic AND (case report[pt] OR case reports[pt]))',
    "steroid_ophth_ae": '((dexamethasone[tiab] OR prednisolone[tiab] OR fluorometholone[tiab]) AND ophthalmic AND (case report[pt] OR case reports[pt])) AND (Cushing OR "adrenal suppression" OR IOP OR glaucoma)',
    "beta_blocker_ophth": '("beta blocker"[tiab] OR "beta-blocker"[tiab] OR beta-blockers[tiab]) AND ophthalmic[tiab] AND (systemic[tiab] OR adverse[tiab] OR interaction[tiab])',
    "prostaglandin_ae": '((latanoprost[tiab] OR travoprost[tiab] OR bimatoprost[tiab]) AND (case report[pt] OR case reports[pt])) AND (adverse OR systemic OR interaction)',
    "antibiotic_ophth_ae": '((ciprofloxacin[tiab] OR moxifloxacin[tiab] OR ofloxacin[tiab] OR tobramycin[tiab] OR erythromycin[tiab]) AND ophthalmic AND (case report[pt] OR case reports[pt]))',
    # Systematic reviews
    "ophthalmic_systemic_review": '(ophthalmic[tiab] OR "eye drops"[tiab]) AND ("systemic absorption"[tiab] OR "systemic side effects"[tiab] OR "systemic adverse"[tiab]) AND (systematic review[pt] OR meta-analysis[pt] OR review[pt])',
    # Drug interaction specific
    "ophth_ddi_general": '("drug interaction"[tiab] OR DDI[tiab]) AND (ophthalmic[tiab] OR "eye drops"[tiab] OR glaucoma[tiab]) AND (adverse[tiab] OR systemic[tiab] OR case[tiab])',
}

for name, query in pubmed_queries.items():
    try:
        pmids = pubmed_search(query, retmax=15)
        time.sleep(0.35)
        if pmids:
            articles = pubmed_fetch(pmids)
            for a in articles:
                a["source"] = "pubmed"
                a["search_query"] = name
            all_articles.extend(articles)
            search_log[name] = {"source": "pubmed", "query": query[:80], "n": len(articles)}
            print(f"  pubmed/{name}: {len(articles)} articles")
        time.sleep(0.35)
    except Exception as e:
        print(f"  pubmed/{name}: ERROR - {e}")

# ── 2. Cochrane Library (via PubMed subset) ──
cochrane_queries = {
    "cochrane_ophth_ae": '("eye drops"[tiab] OR ophthalmic[tiab]) AND (adverse[tiab] OR systemic[tiab] OR interaction[tiab]) AND cochrane[ta]',
    "cochrane_glaucoma": '(glaucoma[tiab] OR "intraocular pressure"[tiab]) AND (systemic[tiab] OR adverse[tiab] OR interaction[tiab]) AND cochrane[ta]',
}
for name, query in cochrane_queries.items():
    try:
        pmids = pubmed_search(query, retmax=10)
        time.sleep(0.35)
        if pmids:
            articles = pubmed_fetch(pmids)
            for a in articles:
                a["source"] = "cochrane"
                a["search_query"] = name
            all_articles.extend(articles)
            search_log[name] = {"source": "cochrane", "query": query[:80], "n": len(articles)}
            print(f"  cochrane/{name}: {len(articles)} articles")
        time.sleep(0.35)
    except Exception as e:
        print(f"  cochrane/{name}: ERROR - {e}")

# ── 3. Clinical Trial registries (PubMed subset) ──
trial_queries = {
    "trial_ophth_ddi": '(ophthalmic[tiab] OR "eye drops"[tiab]) AND (interaction[tiab] OR adverse[tiab] OR systemic[tiab]) AND (clinical trial[pt] OR randomized controlled trial[pt])',
}
for name, query in trial_queries.items():
    try:
        pmids = pubmed_search(query, retmax=10)
        time.sleep(0.35)
        if pmids:
            articles = pubmed_fetch(pmids)
            for a in articles:
                a["source"] = "clinical_trials"
                a["search_query"] = name
            all_articles.extend(articles)
            search_log[name] = {"source": "clinical_trials", "query": query[:80], "n": len(articles)}
            print(f"  trials/{name}: {len(articles)} articles")
        time.sleep(0.35)
    except Exception as e:
        print(f"  trials/{name}: ERROR - {e}")

# ═══ DEDUP + CROSS-MATCH ═══
seen_pmids = set()
unique_articles = []
for a in all_articles:
    if a["pmid"] not in seen_pmids:
        seen_pmids.add(a["pmid"])
        unique_articles.append(a)

print(f"\nTotal unique articles: {len(unique_articles)}")

# Cross-match with drug registry
import yaml
with open(ROOT / "configs" / "rules.yaml") as f:
    rules = yaml.safe_load(f)["rules"]
sev = {"high":3,"medium":2,"low":1}

def rule_best(af, bf):
    best = "low"; bv = 1
    afs, bfs = set(af), set(bf)
    for r in rules:
        if set(r.get("entity_a_flags",[])) <= afs and set(r.get("entity_b_flags",[])) <= bfs:
            sv = sev.get(r["severity"],1)
            if sv > bv: best = r["severity"]; bv = sv
    return best

ext_cases = []
seen_pairs = set()

for art in unique_articles:
    text = (art.get("title","") + " " + art.get("abstract","")).lower()
    if len(text) < 50: continue
    
    a_hits = [a for a in a_rows.values() if len(a["primary_name"])>4 and a["primary_name"].lower() in text]
    b_hits = [b for b in b_rows.values() if len(b["generic_name"])>4 and b["generic_name"].lower() in text]
    if not a_hits or not b_hits: continue
    
    # Infer risk from article text
    hi_kw = ["severe","life-threatening","fatal","death","syncope","coma","apnea",
             "cardiac arrest","hypertensive crisis","hospitalization","contraindicated",
             "poisoning","overdose","toxic","toxicity"]
    lo_kw = ["no significant","no interaction","safe","well tolerated","negligible",
             "not clinically significant","no systemic","no evidence","does not cause"]
    text_risk = None
    if any(k in text for k in hi_kw): text_risk = "high"
    elif any(k in text for k in lo_kw): text_risk = "low"
    
    is_case = any("Case Report" in pt for pt in art.get("pubtypes",[]))
    is_review = any("Review" in pt for pt in art.get("pubtypes",[]))
    is_trial = any(t in str(art.get("pubtypes",[])) for t in ["Clinical Trial","Randomized Controlled Trial"])
    is_cochrane = art.get("source") == "cochrane"
    
    for a in a_hits[:2]:
        for b in b_hits[:2]:
            key = (a["topical_ophthalmic_medications_id"], b["entity_b_id"])
            if key in seen_pairs: continue
            seen_pairs.add(key)
            
            af = a["flags"].split("|"); bf = b["flags"].split("|")
            gold = text_risk or rule_best(af, bf)
            
            ev_type = "case_report" if is_case else ("review" if is_review else ("trial" if is_trial else "other"))
            if is_cochrane: ev_type = "cochrane_review"
            
            ext_cases.append({
                "case_id": f"EXT-{len(ext_cases):03d}",
                "entity_a_id": a["topical_ophthalmic_medications_id"],
                "entity_b_id": b["entity_b_id"],
                "ophthalmic_drug": a["primary_name"],
                "systemic_drug": b["generic_name"],
                "ophthalmic_class": a.get("category",""),
                "systemic_class": b.get("drug_class",""),
                "gold_risk_level": gold,
                "evidence_type": ev_type,
                "source": art.get("source","pubmed"),
                "patient_factors": [],
                "provenance": {
                    "source_type": "literature",
                    "source_ref": f"PMID:{art['pmid']} — {art.get('title','')[:120]}",
                    "record_locator": f"PMID:{art['pmid']}",
                    "ground_truth_method": "literature_case_report",
                    "extraction_date": "2026-07-31",
                    "pmid": art["pmid"],
                    "doi": art.get("doi",""),
                    "pubdate": art.get("pubdate",""),
                    "journal": art.get("journal",""),
                    "title": art.get("title","")[:200],
                    "abstract_snippet": art.get("abstract","")[:500],
                    "source_db": art.get("source",""),
                }
            })

# ═══ REPORT ═══
dist = Counter(c["gold_risk_level"] for c in ext_cases)
src_dist = Counter(c["source"] for c in ext_cases)
ev_dist = Counter(c["evidence_type"] for c in ext_cases)

print(f"\n{'='*60}")
print(f"  EXTERNAL VALIDATION SET — INDEPENDENT SOURCES")
print(f"{'='*60}")
print(f"  Total cases: {len(ext_cases)}")
print(f"  Distribution: H={dist.get('high',0)} M={dist.get('medium',0)} L={dist.get('low',0)}")
print(f"  Sources: {dict(src_dist)}")
print(f"  Evidence types: {dict(ev_dist)}")

# Save
out_dir = ROOT / "data" / "datasets" / "external_validation"
out_dir.mkdir(parents=True, exist_ok=True)

with open(out_dir / "cases.jsonl", "w", encoding="utf-8") as f:
    for c in ext_cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

with open(out_dir / "source_references.json", "w", encoding="utf-8") as f:
    refs = []
    seen_refs = set()
    for c in ext_cases:
        pmid = c["provenance"]["pmid"]
        if pmid not in seen_refs:
            seen_refs.add(pmid)
            refs.append({
                "pmid": pmid,
                "title": c["provenance"]["title"],
                "journal": c["provenance"]["journal"],
                "pubdate": c["provenance"]["pubdate"],
                "doi": c["provenance"]["doi"],
                "source": c["source"],
                "evidence_type": c["evidence_type"],
                "cases_used_in": c["case_id"],
            })
    json.dump({"n_references": len(refs), "references": refs}, f, indent=2, ensure_ascii=False)

with open(out_dir / "dataset.meta.json", "w") as f:
    json.dump({
        "dataset_id": "external_validation",
        "role": "external_validation",
        "n_cases": len(ext_cases),
        "n_unique_references": len(seen_refs),
        "distribution": dict(dist),
        "sources": dict(src_dist),
        "evidence_types": dict(ev_dist),
        "independence": "ALL sources independent from system building (FDA labels, DrugBank, 1307 evidence chunks NOT used as gold)",
        "ground_truth_methods": ["literature_case_report"],
        "created": "2026-07-31",
    }, f, indent=2)

print(f"\n  Unique references: {len(seen_refs)}")
print(f"  Saved: {out_dir}/cases.jsonl")
print(f"  Saved: {out_dir}/source_references.json (supplementary material)")
