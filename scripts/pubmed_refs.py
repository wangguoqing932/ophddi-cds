# -*- coding: utf-8 -*-
"""pubmed_refs.py — PubMed 检索 + 双源交叉验证参考文献（kuku 风格 Rule 3）。

流程: esearch 检索式 -> esummary 元数据(PMID/title/DOI) -> Crossref 验证 DOI
存在且标题一致 -> 生成引用列表 outputs/paper/refs_pubmed.json
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ROOT = Path(__file__).resolve().parents[1]


def esearch(term, retmax=4):
    url = f"{BASE}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}&retmode=json&retmax={retmax}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read())["esearchresult"].get("idlist", [])
    except Exception:
        return []


def esummary(pmids):
    url = f"{BASE}/esummary.fcgi?db=pubmed&id={','.join(pmids)}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read()).get("result", {})
    except Exception:
        return {}


def crossref_verify(doi):
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}",
                                     headers={"User-Agent": "paper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            m = json.loads(r.read())["message"]
        title = (m.get("title") or [""])[0]
        year = (m.get("issued", {}).get("date-parts", [[None]])[0][0])
        journal = (m.get("container-title") or [""])[0]
        authors = m.get("author", [])
        al = ", ".join(f"{a.get('family','')} {a.get('given','')[:1]}." for a in authors[:6])
        if len(authors) > 6:
            al += ", et al."
        return {"title": title, "year": year, "journal": journal, "authors": al}
    except Exception:
        return None


QUERIES = [
    "timolol eye drops systemic adverse effects",
    "ophthalmic beta-blocker bradycardia",
    "brimonidine toxicity pediatric systemic",
    "atropine eye drops systemic absorption",
    "glaucoma medications systemic side effects",
    "ophthalmic drug drug interaction systemic",
    "carbonic anhydrase inhibitor dorzolamide systemic acidosis",
    "topical NSAID eye drops systemic",
    "nasolacrimal occlusion systemic absorption eye drops",
    "DDInter drug interaction database",
    "retrieval augmented generation large language models",
    "clinical decision support systems medication safety",
    "pharmacovigilance adverse drug reactions ophthalmology",
    "topical corticosteroid eye drops systemic",
    "alpha-2 agonist eye drops central nervous system",
    "eye drops systemic toxicity case series",
]


def main():
    seen_doi = {"10.7759/cureus.20945", "10.1136/bmj.294.6565.155-a",
                "10.7759/cureus.25815", "10.1561/1500000019",
                "10.48550/arxiv.2410.05779", "10.1177/001316446002000104",
                "10.2307/2529310", "10.1111/pde.12868", "10.1111/bcp.13499",
                "10.53738/revmed.2025.21.931.47723"}
    refs = []
    for q in QUERIES:
        ids = esearch(q, retmax=4)
        if not ids:
            time.sleep(0.5)
            continue
        res = esummary(ids)
        for pid in ids:
            item = res.get(pid, {})
            doi = (item.get("elocationid") or "").replace("doi: ", "").strip().lower()
            if not doi or doi in seen_doi:
                continue
            title = item.get("title", "")
            # 交叉验证：Crossref 解析 DOI + 标题一致
            cr = crossref_verify(doi)
            if not cr:
                continue
            t1 = (title or "").lower()[:60]
            t2 = (cr["title"] or "").lower()[:60]
            if t1 and t2 and t1[:30] != t2[:30] and t1[:30] not in t2 and t2[:30] not in t1:
                continue  # 标题不一致 -> 剔除（防 DOI 错配）
            seen_doi.add(doi)
            refs.append({
                "pmid": pid, "doi": doi, "pubmed_title": title,
                "title": cr["title"], "year": cr["year"],
                "journal": cr["journal"], "authors": cr["authors"],
            })
            if len(refs) >= 32:
                break
        if len(refs) >= 32:
            break
        time.sleep(0.6)
    Path("outputs/paper/refs_pubmed.json").write_text(
        json.dumps(refs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"交叉验证通过: {len(refs)} 条 -> outputs/paper/refs_pubmed.json")
    for r in refs:
        print(f"  PMID {r['pmid']} ({r['year']}) {r['title'][:58]} | {r['doi']}")


if __name__ == "__main__":
    main()
