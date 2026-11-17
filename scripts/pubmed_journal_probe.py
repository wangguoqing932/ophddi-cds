# -*- coding: utf-8 -*-
"""pubmed_journal_probe.py — 搜同类文章发表期刊分布（PubMed）。"""
import json, time, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esearch(term, retmax=30):
    # 用 sort=relevance 获取与主题相关的文献
    url = (f"{BASE}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}"
           f"&retmode=json&retmax={retmax}&sort=relevance")
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read())["esearchresult"].get("idlist", [])
    except Exception as e:
        print('esearch err:', e)
        return []

def esummary(pmids):
    url = f"{BASE}/esummary.fcgi?db=pubmed&id={','.join(pmids)}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read()).get("result", {})
    except Exception:
        return {}

TERMS = [
    # 主题1: 眼科局部药 vs 全身系统药 相互作用
    'ophthalmic AND systemic AND drug interaction AND adverse',
    # 主题2: 临床决策支持 + 药物相互作用
    'clinical decision support AND drug interaction AND (ophthalmic OR ophthalmic medication)',
    # 主题3: 确定性疾病诊断/知识工程 + LLM 对比
    'deterministic OR rule-based AND drug interaction AND decision support',
]

journals = Counter()
details = []
for term in TERMS:
    ids = esearch(term, 30)
    print(f"['{term}'] -> {len(ids)} hits")
    if not ids:
        time.sleep(1)
        continue
    res = esummary(ids)
    for pid in ids:
        it = res.get(pid, {})
        j = it.get("fulljournalname") or it.get("source", "")
        if j:
            journals[j] += 1
            details.append((j, it.get("pubdate",""), it.get("title","")[:80]))
    time.sleep(1)

print("\n=== 期刊分布 ===")
for j, n in journals.most_common(20):
    print(f"{n:2d}  {j}")
Path('outputs/pubmed_journal_probe.json').write_text(
    json.dumps({"journals": dict(journals), "details": details}, ensure_ascii=False, indent=2), encoding='utf-8')
