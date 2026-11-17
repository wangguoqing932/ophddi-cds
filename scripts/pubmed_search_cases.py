"""pubmed_search_cases.py — Search PubMed for ophthalmic DDI case reports"""

import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def pubmed_search(term, retmax=20):
    """Search PubMed, return list of PMIDs."""
    params = {"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json"}
    url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    return data["esearchresult"]["idlist"]

def pubmed_fetch(pmids):
    """Fetch abstracts for given PMIDs, return list of dicts."""
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "xml", "retmode": "xml"}
    url = f"{BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as resp:
        root = ET.fromstring(resp.read())
    
    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID", "")
        title = article.findtext(".//ArticleTitle", "")
        abstract = article.findtext(".//Abstract/AbstractText", "")
        if not abstract:
            # Try multiple AbstractText elements
            abs_parts = article.findall(".//Abstract/AbstractText")
            abstract = " ".join(a.text or "" for a in abs_parts)
        journal = article.findtext(".//Journal/Title", "")
        pubdate = article.findtext(".//PubDate/Year", "")
        authors = []
        for auth in article.findall(".//Author"):
            ln = auth.findtext("LastName", "")
            fn = auth.findtext("ForeName", "")
            if ln:
                authors.append(f"{ln} {fn}".strip())
        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract[:800] if abstract else "",
            "journal": journal,
            "pubdate": pubdate,
            "first_author": authors[0] if authors else "",
        })
    return results

# ═══ Search queries for known ophthalmic DDI mechanisms ═══
SEARCHES = [
    # Beta-blocker DDIs
    ("timolol_bradycardia", 
     '(timolol[tiab] AND ophthalmic[tiab]) AND (bradycardia[tiab] OR heart block[tiab] OR syncope[tiab]) AND case reports[pt]'),
    ("timolol_systemic_beta", 
     '(timolol ophthalmic[tiab]) AND (atenolol[tiab] OR propranolol[tiab] OR metoprolol[tiab]) AND (interaction[tiab] OR adverse[tiab])'),
    
    # Brimonidine CNS
    ("brimonidine_cns", 
     '(brimonidine[tiab] AND ophthalmic[tiab]) AND (CNS depression[tiab] OR sedation[tiab] OR coma[tiab] OR apnea[tiab]) AND (child[tiab] OR infant[tiab] OR pediatric[tiab])'),
    
    # Atropine anticholinergic
    ("atropine_anticholinergic", 
     '(atropine[tiab] AND eye drops[tiab]) AND (anticholinergic[tiab] OR delirium[tiab] OR tachycardia[tiab] OR systemic[tiab]) AND (adverse[tiab] OR toxicity[tiab] OR case[tiab])'),
    
    # Phenylephrine hypertension
    ("phenylephrine_hypertension", 
     '(phenylephrine[tiab] AND ophthalmic[tiab]) AND (hypertension[tiab] OR hypertensive crisis[tiab] OR blood pressure[tiab]) AND (adverse[tiab] OR interaction[tiab])'),
    
    # Dorzolamide metabolic
    ("dorzolamide_metabolic", 
     '(dorzolamide[tiab] OR brinzolamide[tiab]) AND (metabolic acidosis[tiab] OR electrolyte[tiab] OR hypokalemia[tiab]) AND (adverse[tiab] OR case[tiab])'),
    
    # NSAID bleeding
    ("ketorolac_bleeding", 
     '(ketorolac[tiab] OR bromfenac[tiab] OR nepafenac[tiab]) AND ophthalmic[tiab] AND (bleeding[tiab] OR hemorrhage[tiab] OR anticoagulant[tiab]) AND case[tiab]'),
    
    # Corticosteroid IOP/systemic
    ("corticosteroid_systemic",
     '(dexamethasone[tiab] OR prednisolone[tiab]) AND ophthalmic[tiab] AND (systemic absorption[tiab] OR Cushing[tiab] OR adrenal suppression[tiab]) AND case[tiab]'),
    
    # General ophthalmic systemic adverse events
    ("ophthalmic_systemic_review",
     '(ophthalmic[tiab] AND eye drops[tiab]) AND (systemic adverse[tiab] OR systemic absorption[tiab] OR systemic side effects[tiab]) AND (review[pt] OR meta-analysis[pt])'),
]

all_pmids = set()
search_results = {}

print("Searching PubMed for ophthalmic DDI case reports...\n")
for name, query in SEARCHES:
    pmids = pubmed_search(query, retmax=10)
    all_pmids.update(pmids)
    search_results[name] = {"query": query[:100], "pmids": pmids, "count": len(pmids)}
    print(f"  {name}: {len(pmids)} results")
    time.sleep(0.35)

print(f"\nTotal unique PMIDs: {len(all_pmids)}")

# Fetch all abstracts
print("Fetching abstracts...")
all_articles = pubmed_fetch(list(all_pmids))
print(f"Fetched {len(all_articles)} articles")

# Save
out_path = ROOT / "output" / "pubmed_case_reports.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "search_date": "2026-07-31",
        "searches": {k: {"query": v["query"], "n_results": v["count"]} for k,v in search_results.items()},
        "articles": all_articles,
        "total_unique_pmids": len(all_pmids),
    }, f, indent=2, ensure_ascii=False)

# Print summary
print(f"\n{'='*60}")
print(f"  PUBMED CASE REPORTS SUMMARY")
print(f"{'='*60}")
for art in all_articles[:20]:
    print(f"\n  PMID:{art['pmid']} | {art['pubdate']} | {art['journal'][:40]}")
    print(f"  {art['title'][:120]}")
    print(f"  First author: {art['first_author']}")
    print(f"  Abstract: {art['abstract'][:200]}...")

print(f"\nSaved: {out_path}")
print(f"Total articles: {len(all_articles)}")
