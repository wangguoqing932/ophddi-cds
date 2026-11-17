"""search_evidence_types.py — PK studies, clinical trials, animal studies, reviews"""
import csv, json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search(term, retmax=15):
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
        abs_parts = a.findall(".//Abstract/AbstractText")
        abstract = " ".join(t.text or "" for t in abs_parts)
        results.append({
            "pmid": a.findtext(".//PMID",""),
            "title": a.findtext(".//ArticleTitle",""),
            "abstract": abstract[:800],
            "journal": a.findtext(".//Journal/Title",""),
            "pubdate": a.findtext(".//PubDate/Year",""),
            "doi": a.findtext(".//ArticleIdList/ArticleId[@IdType='doi']",""),
            "pubtypes": [p.text for p in a.findall(".//PublicationType")],
        })
    return results

# ═══ SEARCH BY EVIDENCE TYPE ═══
QUERIES = {
    # 1. PK studies: plasma levels after ophthalmic administration
    "pk_timolol": '(timolol[tiab] AND ophthalmic[tiab]) AND (pharmacokinetic[tiab] OR "plasma concentration"[tiab] OR bioavailability[tiab] OR "systemic absorption"[tiab])',
    "pk_brimonidine": '(brimonidine[tiab]) AND (pharmacokinetic[tiab] OR "plasma concentration"[tiab] OR "systemic absorption"[tiab] OR bioavailability[tiab])',
    "pk_latanoprost": '(latanoprost[tiab] OR travoprost[tiab] OR bimatoprost[tiab]) AND (pharmacokinetic[tiab] OR "plasma concentration"[tiab] OR "systemic exposure"[tiab])',
    "pk_corticosteroid": '(dexamethasone[tiab] OR prednisolone[tiab]) AND ophthalmic[tiab] AND ("systemic absorption"[tiab] OR pharmacokinetic[tiab] OR bioavailability[tiab])',
    "pk_general": '("eye drops"[tiab] AND (pharmacokinetic[tiab] OR "systemic absorption"[tiab])) AND (human[tiab] OR plasma[tiab]) AND (review[pt] OR clinical trial[pt])',

    # 2. Clinical studies: actual patient outcomes
    "clinical_timolol_cardiac": '(timolol[tiab] AND ophthalmic[tiab]) AND (bradycardia[tiab] OR syncope[tiab] OR "heart rate"[tiab]) AND (clinical trial[pt] OR observational[tiab] OR cohort[tiab])',
    "clinical_beta_blocker": '("beta blocker"[tiab] OR "beta-blocker"[tiab]) AND ophthalmic[tiab] AND (systemic[tiab] OR cardiovascular[tiab]) AND (clinical[tiab] OR patient[tiab])',
    "clinical_phenylephrine": '(phenylephrine[tiab] AND ophthalmic[tiab]) AND ("blood pressure"[tiab] OR hypertension[tiab] OR cardiovascular[tiab]) AND (clinical[tiab] OR patient[tiab])',
    "clinical_nsaid": '(ketorolac[tiab] OR bromfenac[tiab] OR diclofenac[tiab] OR nepafenac[tiab]) AND ophthalmic[tiab] AND (bleeding[tiab] OR "corneal melt"[tiab] OR adverse[tiab]) AND (study[tiab] OR trial[tiab] OR series[tiab])',

    # 3. Animal studies
    "animal_ophthalmic": '(ophthalmic[tiab] OR "eye drops"[tiab]) AND (systemic[tiab] OR absorption[tiab] OR interaction[tiab]) AND (rabbit[tiab] OR rat[tiab] OR mouse[tiab] OR animal[tiab] OR "in vivo"[tiab])',

    # 4. Reviews summarizing ophthalmic systemic effects
    "review_ophthalmic_systemic": '("eye drops"[tiab] OR ophthalmic[tiab]) AND ("systemic side effects"[tiab] OR "systemic adverse"[tiab] OR "systemic complications"[tiab]) AND (review[pt] OR systematic[tiab])',
    "review_ddi_ophthalmic": '("drug interaction"[tiab] AND ophthalmic[tiab]) AND (review[pt] OR systematic[tiab])',

    # 5. Specific interaction studies
    "interaction_beta_calcium": '(timolol[tiab] AND (verapamil[tiab] OR diltiazem[tiab] OR "calcium channel"[tiab])) AND (interaction[tiab] OR bradycardia[tiab] OR "heart block"[tiab])',
    "interaction_alpha2_opioid": '(brimonidine[tiab] OR apraclonidine[tiab]) AND (fentanyl[tiab] OR opioid[tiab] OR morphine[tiab]) AND (CNS[tiab] OR sedation[tiab] OR interaction[tiab])',
    "interaction_anticholinergic": '(atropine[tiab] OR cyclopentolate[tiab] OR tropicamide[tiab]) AND (anticholinergic[tiab] OR delirium[tiab] OR "drug interaction"[tiab])',
}

all_articles = []
for name, query in QUERIES.items():
    try:
        pmids = search(query)
        time.sleep(0.35)
        if pmids:
            arts = fetch(pmids)
            for a in arts: a["search_name"] = name
            all_articles.extend(arts)
            print(f"  {name}: {len(arts)} articles")
        time.sleep(0.35)
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

# Dedup
seen = set()
unique = []
for a in all_articles:
    if a["pmid"] not in seen:
        seen.add(a["pmid"])
        unique.append(a)

# Categorize evidence types
types = Counter()
for a in unique:
    pts = a.get("pubtypes",[])
    if any("Review" in p for p in pts): types["review"] += 1
    elif any("Clinical Trial" in p for p in pts): types["clinical_trial"] += 1
    elif any("Randomized Controlled Trial" in p for p in pts): types["rct"] += 1
    elif any("Case Reports" in p for p in pts): types["case_report"] += 1
    else: types["other_study"] += 1

print(f"\n{'='*50}")
print(f"  EVIDENCE SEARCH RESULTS")
print(f"{'='*50}")
print(f"  Total unique: {len(unique)}")
print(f"  Types: {dict(types)}")

# Save
out = ROOT / "output" / "pubmed_evidence_types.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"search_date": "2026-07-31", "n_articles": len(unique),
               "evidence_types": dict(types), "articles": unique}, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")
