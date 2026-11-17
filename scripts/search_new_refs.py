# -*- coding: utf-8 -*-
"""search_new_refs.py — 为补充引用检索真实文献（PubMed esearch + esummary）。

只输出候选元数据，不生成引用条目；最终条目经 Crossref DOI 二次核验后手工录入。
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "new_ref_candidates.json"

# (用途标签, PubMed 检索式)
QUERIES = [
    ("absorption_review", "systemic absorption ophthalmic drugs review"),
    ("llm_medicine", "large language models medicine review Nature Medicine"),
    ("llm_hallucination", "hallucination large language models clinical reliability"),
    ("tripod_ai", "TRIPOD+AI statement reporting guideline prediction model artificial intelligence"),
    ("decide_ai", "DECIDE-AI reporting guideline early-stage clinical evaluation decision support artificial intelligence"),
    ("alert_fatigue", "alert fatigue clinical decision support override systematic review"),
    ("kg_ddi", "knowledge graph drug-drug interaction prediction"),
    ("deep_ddi", "deep learning drug-drug interaction prediction DeepDDI"),
    ("polypharmacy", "polypharmacy older adults prevalence review"),
    ("faers_method", "disproportionality analysis FAERS pharmacovigilance methodology"),
    ("ai_ophthalmology", "artificial intelligence deep learning ophthalmology review"),
    ("ddi_ehr", "drug-drug interaction alerts electronic health records override rate"),
]


def get(url, tries=4):
    for a in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2 ** (a + 1))
    return {}


def main():
    results = {}
    for tag, q in QUERIES:
        ids = get(f"{BASE}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(q)}&retmode=json&retmax=5")
        idlist = ids.get("esearchresult", {}).get("idlist", [])
        if not idlist:
            results[tag] = {"query": q, "hits": []}
            print(f"{tag:20s} -> no hits")
            continue
        summ = get(f"{BASE}/esummary.fcgi?db=pubmed&id={','.join(idlist)}&retmode=json").get("result", {})
        hits = []
        for pmid in idlist:
            d = summ.get(pmid, {})
            doi = ""
            for aid in d.get("articleids", []):
                if aid.get("idtype") == "doi":
                    doi = aid.get("value", "")
            hits.append({
                "pmid": pmid,
                "title": d.get("title", ""),
                "journal": d.get("fulljournalname", d.get("source", "")),
                "year": (d.get("pubdate", "") or "")[:4],
                "volume": d.get("volume", ""),
                "issue": d.get("issue", ""),
                "pages": d.get("pages", ""),
                "doi": doi,
                "authors": [a.get("name", "") for a in d.get("authors", [])][:8],
            })
        results[tag] = {"query": q, "hits": hits}
        print(f"\n### {tag}  ({q})")
        for h in hits:
            print(f"  {h['pmid']:>9s} {h['year']:4s} {h['journal'][:34]:34s} {h['title'][:78]}")
            print(f"            doi: {h['doi']}")
        time.sleep(0.5)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsaved -> {OUT}")


if __name__ == "__main__":
    main()
