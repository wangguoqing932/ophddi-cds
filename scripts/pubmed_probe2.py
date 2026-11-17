# -*- coding: utf-8 -*-
import json, time, urllib.parse, urllib.request
from collections import Counter
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def esearch(term, retmax=20):
    url = (f"{BASE}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}"
           f"&retmode=json&retmax={retmax}&sort=relevance")
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read())["esearchresult"].get("idlist", [])
    except Exception:
        return []
def esummary(pmids):
    url = f"{BASE}/esummary.fcgi?db=pubmed&id={','.join(pmids)}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read()).get("result", {})
    except Exception:
        return {}
TERMS = [
    'large language model AND drug interaction AND evaluation',
    'knowledge graph AND drug interaction AND clinical',
    'rule engine AND medication safety AND hospital',
    'expert system AND drug interaction AND (ophthalmic OR eye)',
]
journals = Counter()
for term in TERMS:
    ids = esearch(term, 20)
    print(f"['{term}'] -> {len(ids)}")
    if not ids:
        time.sleep(1); continue
    res = esummary(ids)
    for pid in ids:
        it = res.get(pid, {})
        j = it.get("fulljournalname") or it.get("source","")
        if j: journals[j] += 1
    time.sleep(1)
print("\n=== LLM/KG/规则引擎类 期刊分布 ===")
for j, n in journals.most_common(25):
    print(f"{n:2d}  {j}")
