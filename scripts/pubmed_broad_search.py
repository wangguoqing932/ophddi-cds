"""pubmed_broad_search.py — Comprehensive PubMed search for ophthalmic DDI evidence"""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search(term, retmax=30):
    params = {"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json"}
    url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["esearchresult"]["idlist"]

def fetch(pmids):
    if not pmids: return []
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "xml", "retmode": "xml"}
    url = f"{BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as r:
        root = ET.fromstring(r.read())
    results = []
    for a in root.findall(".//PubmedArticle"):
        results.append({
            "pmid": a.findtext(".//PMID",""),
            "title": a.findtext(".//ArticleTitle",""),
            "abstract": " ".join(t.text or "" for t in a.findall(".//Abstract/AbstractText")),
            "journal": a.findtext(".//Journal/Title",""),
            "pubdate": a.findtext(".//PubDate/Year",""),
            "doi": a.findtext(".//ArticleIdList/ArticleId[@IdType='doi']",""),
            "pubtypes": [p.text for p in a.findall(".//PublicationType")],
        })
    return results

# ═══ EXPANDED SEARCH STRATEGY ═══
SEARCHES = {
    # 1. MeSH-based: Drug Interactions + Ophthalmic Solutions
    "mesh_ddi": '("Drug Interactions"[MeSH] OR "Drug-Related Side Effects and Adverse Reactions"[MeSH]) AND "Ophthalmic Solutions"[MeSH] AND (english[la] OR chinese[la])',
    
    # 2. Specific well-known ophthalmic-systemic interactions
    "timolol_cardiac": '(timolol[tiab] AND ophthalmic[tiab]) AND (bradycardia[tiab] OR syncope[tiab] OR "heart block"[tiab] OR "cardiac arrest"[tiab])',
    "timolol_respiratory": '(timolol[tiab] AND ophthalmic[tiab]) AND (bronchospasm[tiab] OR asthma[tiab] OR "respiratory failure"[tiab] OR COPD[tiab])',
    "brimonidine_pediatric": '(brimonidine[tiab]) AND (pediatric[tiab] OR infant[tiab] OR child[tiab] OR neonate[tiab]) AND (coma[tiab] OR apnea[tiab] OR hypotension[tiab] OR bradycardia[tiab] OR CNS[tiab])',
    "phenylephrine_cardiovascular": '(phenylephrine[tiab] AND ophthalmic[tiab] OR "eye drops"[tiab]) AND (hypertension[tiab] OR "blood pressure"[tiab] OR tachycardia[tiab] OR "pulmonary edema"[tiab])',
    "atropine_systemic": '(atropine[tiab] OR cyclopentolate[tiab]) AND ("eye drops"[tiab] OR ophthalmic[tiab]) AND (delirium[tiab] OR psychosis[tiab] OR tachycardia[tiab] OR fever[tiab] OR "systemic absorption"[tiab])',
    "dorzolamide_acidosis": '(dorzolamide[tiab] OR brinzolamide[tiab]) AND (acidosis[tiab] OR "metabolic acidosis"[tiab] OR hypokalemia[tiab] OR "aplastic anemia"[tiab] OR dyspnea[tiab])',
    "nsaid_ophthalmic_bleeding": '(ketorolac[tiab] OR bromfenac[tiab] OR nepafenac[tiab] OR diclofenac[tiab]) AND ophthalmic[tiab] AND (bleeding[tiab] OR hemorrhage[tiab] OR "corneal melt"[tiab] OR "corneal perforation"[tiab])',
    "steroid_iop_systemic": '(dexamethasone[tiab] OR prednisolone[tiab] OR fluorometholone[tiab]) AND ophthalmic[tiab] AND ("intraocular pressure"[tiab] OR glaucoma[tiab] OR "Cushing"[tiab] OR "adrenal suppression"[tiab])',
    "prostaglandin_ophthalmic": '(latanoprost[tiab] OR travoprost[tiab] OR bimatoprost[tiab]) AND ophthalmic[tiab] AND (adverse[tiab] OR systemic[tiab] OR interaction[tiab])',
    "antibiotic_ophthalmic_systemic": '(ciprofloxacin[tiab] OR moxifloxacin[tiab] OR tobramycin[tiab] OR erythromycin[tiab]) AND ophthalmic[tiab] AND (systemic[tiab] OR absorption[tiab] OR adverse[tiab])',
    
    # 3. Reviews and meta-analyses
    "review_systemic": '("eye drops"[tiab] OR ophthalmic[tiab]) AND ("systemic absorption"[tiab] OR "systemic side effects"[tiab] OR "systemic adverse"[tiab]) AND (review[pt] OR systematic[tiab])',
    
    # 4. Pharmacokinetic studies
    "pk_ophthalmic": '(ophthalmic[tiab] OR "eye drops"[tiab]) AND (pharmacokinetic[tiab] OR bioavailability[tiab] OR "plasma concentration"[tiab] OR "systemic exposure"[tiab]) AND human[tiab]',
    
    # 5. Drug interaction specific
    "ddi_ophthalmic": '("drug interaction"[tiab] OR "drug-drug interaction"[tiab] OR DDI[tiab]) AND (ophthalmic[tiab] OR "eye drops"[tiab] OR glaucoma[tiab])',
}

all_pmids = set()
for name, query in SEARCHES.items():
    try:
        pmids = search(query, retmax=20)
        all_pmids.update(pmids)
        print(f"  {name}: {len(pmids)} results")
        time.sleep(0.35)
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

print(f"\nTotal unique PMIDs: {len(all_pmids)}")

# Fetch in batches
all_articles = []
batch = list(all_pmids)
for i in range(0, len(batch), 50):
    chunk = batch[i:i+50]
    try:
        arts = fetch(chunk)
        all_articles.extend(arts)
        print(f"  Fetched {i+len(chunk)}/{len(batch)}")
    except Exception as e:
        print(f"  Batch {i} error: {e}")
    time.sleep(0.5)

# Save
out = ROOT / "output" / "pubmed_broad_search.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({
        "search_date": "2026-07-31",
        "n_searches": len(SEARCHES),
        "n_articles": len(all_articles),
        "articles": all_articles,
    }, f, indent=2, ensure_ascii=False)

# Quick stats
n_case_reports = sum(1 for a in all_articles if any("Case Reports" in pt for pt in a.get("pubtypes",[])))
n_reviews = sum(1 for a in all_articles if any("Review" in pt for pt in a.get("pubtypes",[])))
n_clinical = sum(1 for a in all_articles if any("Clinical" in pt or "Trial" in pt for pt in a.get("pubtypes",[])))

print(f"\n{'='*50}")
print(f"  BROAD SEARCH RESULTS")
print(f"{'='*50}")
print(f"  Total articles: {len(all_articles)}")
print(f"  Case reports: {n_case_reports}")
print(f"  Reviews: {n_reviews}")
print(f"  Clinical trials: {n_clinical}")
print(f"\nSaved: {out}")
