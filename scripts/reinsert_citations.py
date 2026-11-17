# -*- coding: utf-8 -*-
"""reinsert_citations.py — 按新 40 条 ORDER 重建正文引用插入（先还原旧插入）。"""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "manuscript.en.md"
t = P.read_text(encoding="utf-8")

# 1) 还原已插入的文本（带编号 -> 无编号原句）
REVERT = [
    ("through nasolacrimal drainage and mucosal absorption [1]. Topical carteolol can likewise cause atrioventricular block [9], and severe systemic reactions to ophthalmic timolol have been linked to CYP2D6 poor metabolizers [10].",
     "through nasolacrimal drainage and mucosal absorption [1]."),
    ("topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2], with further case series of timolol-associated syncope and bradycardia reported [11,12]. Ageing patients appear particularly vulnerable [13].",
     "topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2]."),
    ("and alpha-2 agonists can produce CNS depression, particularly in children [20,21,22,23,24].",
     "and alpha-2 agonists can produce CNS depression."),
    ("These resources are of limited direct utility for ophthalmic prescribing. Drug\u2013drug interaction databases have long been recognized as clinically relevant but methodologically heterogeneous [17,18], and automated detection in practice remains incomplete [19].",
     "These resources are of limited direct utility for ophthalmic prescribing."),
    ("while graph-based retrieval (LightRAG) provided measurable but incomplete gains [6], and general computerized clinical decision support has shown modest but variable effects on practice [25].",
     "while graph-based retrieval (LightRAG) provided measurable but incomplete gains [6]."),
    ("including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone [26,27]. Topical instillation technique itself modulates systemic exposure [15].",
     "including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone."),
    ("The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model [28]",
     "The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model"),
    ("reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature, although pharmacovigilance analyses of ophthalmic agents (for example atropine) do identify systemic signals [29,30]",
     "reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature"),
    ("The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies). Ocular drug transfer from systemic administration is likewise complex and incompletely characterized [31].",
     "The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies)."),
]
for old, new in REVERT:
    if old in t:
        t = t.replace(old, new, 1)
    else:
        print(f"REVERT NOT FOUND: {old[:50]}...")

# 2) 按新 ORDER 重新插入（编号 9-40）
INSERTS = [
    ("through nasolacrimal drainage and mucosal absorption [1].",
     "through nasolacrimal drainage and mucosal absorption [1]. Topical carteolol can likewise cause atrioventricular block [9], and severe systemic reactions to ophthalmic timolol have been linked to CYP2D6 poor metabolizers [10]."),
    ("topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2].",
     "topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2], with further case series of timolol-associated syncope reported [11,12]. Ageing patients appear particularly vulnerable [13], and the tissue-press technique can reduce systemic exposure from topical timolol [14]."),
    ("and alpha-2 agonists can produce CNS depression.",
     "and alpha-2 agonists can produce CNS depression, particularly in children [18,19,20,21,22,23]."),
    ("These resources are of limited direct utility for ophthalmic prescribing.",
     "These resources are of limited direct utility for ophthalmic prescribing. Drug\u2013drug interaction databases have long been recognized as clinically relevant but methodologically heterogeneous [27,28], and automated detection in practice remains incomplete [29]."),
    ("graph-based retrieval (LightRAG) provided measurable but incomplete gains [6].",
     "graph-based retrieval (LightRAG) provided measurable but incomplete gains [6], and general computerized clinical decision support has shown modest but variable effects on practice [40]."),
    ("including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone.",
     "including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone [31,32]. Topical instillation technique itself modulates systemic exposure [16]."),
    ("The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model",
     "The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model [33]"),
    ("reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature",
     "reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature, although pharmacovigilance analyses of ophthalmic agents (for example atropine) do identify systemic signals [24,25]"),
    ("The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies).",
     "The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies). Ocular drug transfer from systemic administration is likewise complex and incompletely characterized [33]."),
]
for old, new in INSERTS:
    if old in t:
        t = t.replace(old, new, 1)
    else:
        print(f"INSERT NOT FOUND: {old[:50]}...")

P.write_text(t, encoding="utf-8")

# 3) 验证正文引用
import re
body = t.split("## References")[0]
cites = set()
for m in re.finditer(r"\[(\d+(?:,\d+)*)\]", body):
    for n in m.group(1).split(","):
        cites.add(int(n))
missing = [n for n in range(1, 41) if n not in cites]
print("正文引用编号:", sorted(cites))
print("未引用:", missing if missing else "无")
