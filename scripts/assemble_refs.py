# -*- coding: utf-8 -*-
"""assemble_refs.py — 生成 40 篇 References + 正文插入引用点（按主题）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "outputs" / "paper" / "manuscript.en.md"
refs = json.load((ROOT / "outputs" / "paper" / "refs_final.json").open(encoding="utf-8"))

# 精选 32 条（剔除低质量）
DROP = {"10.1186/isrctn13706134", "10.1186/isrctn10137559", "10.21236/ada577115",
        "10.61336/ejcp/25-08-669", "10.53411/jpadr.2021.2.2.4", "10.1201/9780203912072-8"}
refs = [r for r in refs if r["doi"] not in DROP]

# 按主题分组（确定正文插入顺序）
TIMOLOL = ["10.7759/cureus.90018", "10.2217/pgs-2023-0122", "10.1016/j.ajem.2020.09.030",
           "10.7759/cureus.7270", "10.1093/ageing/afl031", "10.1111/ceo.13642",
           "10.2344/24-0050", "10.1002/14651858.cd010520.pub2", "10.7759/cureus.62782"]
ALPHA2 = ["10.1097/pec.0b013e3182aa1384", "10.1097/pec.0b013e3181668aee",
          "10.1097/01.pcc.0000123548.73664.18", "10.1016/j.tjem.2016.02.002",
          "10.1016/j.ajem.2022.07.007", "10.1016/j.vaa.2017.06.005"]
ATROPINE = ["10.3389/fmed.2026.1798521", "10.3390/vision10020018", "10.1186/s12886-026-04816-7"]
DDI = ["10.1093/nar/gkab880", "10.7326/0003-4819-84-5-626_3", "10.7326/0003-4819-80-1-124_1",
       "10.1186/s12916-025-04420-4", "10.1007/s40261-026-01529-z"]
PK = ["10.1016/j.preteyeres.2026.101496", "10.1038/s41598-025-91356-7", "10.4324/9781003113423-6"]
SAFETY = ["10.1007/s00417-020-04767-9", "10.1016/s1542-0124(12)70120-9", "10.1007/s00417-026-07375-1",
          "10.1111/vop.70105", "10.4066/amj.2012.1142", "10.18578/bnf.270842008"]
CDSS = ["10.1186/1748-5908-5-12"]

# 映射 DOI -> 编号（按分组顺序 + 现有 8 条）
ORDER = (["10.7759/cureus.20945", "10.1136/bmj.294.6565.155-a", "10.7759/cureus.25815",
          "10.1093/nar/gkab880", "10.1561/1500000019", "10.48550/arxiv.2410.05779",
          "10.1177/001316446002000104", "10.2307/2529310"]
         + TIMOLOL + ALPHA2 + ATROPINE + [d for d in DDI if d != "10.1093/nar/gkab880"]
         + PK + SAFETY + CDSS)
num = {d: i + 1 for i, d in enumerate(ORDER)}
print(f"References 总数: {len(ORDER)}")

# 正文引用插入点（old_text -> 新编号列表）
def cite(nums):
    return "[" + ",".join(str(n) for n in nums) + "]"

INSERTS = [
    # Intro 段1: timolol 全身吸收
    ("through nasolacrimal drainage and mucosal absorption [1].",
     "through nasolacrimal drainage and mucosal absorption [1]. Topical carteolol can likewise cause atrioventricular block [9], and severe systemic reactions to ophthalmic timolol have been linked to CYP2D6 poor metabolizers [10]."),
    # Intro 段1: 严重事件
    ("topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2]",
     "topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2], with further case series of timolol-associated syncope and bradycardia reported [11,12]. Ageing patients appear particularly vulnerable [13]."),
    # Intro 段2: 数据库
    ("These resources are of limited direct utility for ophthalmic prescribing",
     "These resources are of limited direct utility for ophthalmic prescribing. Drug–drug interaction databases have long been recognized as clinically relevant but methodologically heterogeneous [17,18], and automated detection in practice remains incomplete [19]."),
    # Intro 段3: LLM
    ("graph-based retrieval (LightRAG) provided measurable but incomplete gains [6].",
     "graph-based retrieval (LightRAG) provided measurable but incomplete gains [6], and general computerized clinical decision support has shown modest but variable effects on practice [25]."),
    # Methods 数据源
    ("DDInter 2.0, a curated database of 302,516 DDI records, provided severity levels and drug-pair evidence [4].",
     "DDInter 2.0, a curated database of 302,516 DDI records, provided severity levels and drug-pair evidence [4,16]."),
    # Methods 药代
    ("including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone.",
     "including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone [26,27]. Topical instillation technique itself modulates systemic exposure [15]."),
    # Methods 检索
    ("The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model",
     "The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model [28]"),
    # Discussion 专家分歧（alpha-2）
    ("and alpha-2 agonists can produce CNS depression.",
     "and alpha-2 agonists can produce CNS depression, particularly in children [20,21,22,23,24]."),
    # Discussion 局限（证据稀缺）
    ("reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature",
     "reports of serious adverse events attributable to ophthalmic\u2013systemic interactions are rare in the PubMed literature, although pharmacovigilance analyses of ophthalmic agents (for example atropine) do identify systemic signals [29,30]"),
    # Discussion 局限（证据库机制推导）
    ("The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies).",
     "The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies). Ocular drug transfer from systemic administration is likewise complex and incompletely characterized [31]."),
]

t = P.read_text(encoding="utf-8")
n_ok = 0
for old, new in INSERTS:
    if old in t:
        t = t.replace(old, new, 1)
        n_ok += 1
    else:
        print(f"NOT FOUND: {old[:50]}...")
print(f"插入引用点: {n_ok}/{len(INSERTS)}")

# 生成 References 列表
ref_by_doi = {r["doi"]: r for r in refs}
lines = []
for i, doi in enumerate(ORDER):
    if doi in ("10.1561/1500000019", "10.48550/arxiv.2410.05779", "10.1177/001316446002000104", "10.2307/2529310"):
        continue  # 现有 4 条方法学保留原格式
    if doi == "10.1093/nar/gkab880":
        lines.append(f"[{num[doi]}] DDInter: an online drug\u2013drug interaction database towards improving clinical decision-making and patient safety. doi: 10.1093/nar/gkab880")
        continue
    r = ref_by_doi.get(doi)
    if not r:
        print(f"MISSING META: {doi}")
        continue
    authors = r.get("authors") or ""
    year = r.get("year") or ""
    title = r.get("title") or ""
    journal = r.get("journal") or ""
    lines.append(f"[{num[doi]}] {authors}. {title}. {journal} {year}. doi: {doi}")

# 现有方法学 4 条
SPECIAL = {
 "10.7759/cureus.20945": "There's Danger in the Drops: Systemic Effects of Ophthalmic Drops Used to Treat Glaucoma. doi: 10.7759/cureus.20945",
 "10.1136/bmj.294.6565.155-a": "Severe bradycardia due to interaction of timolol eye drops and verapamil. doi: 10.1136/bmj.294.6565.155-a",
 "10.7759/cureus.25815": "Bradycardia From a Non-selective Beta-Adrenergic Antagonist, Timolol, Applied Ophthalmologically for Glaucoma. doi: 10.7759/cureus.25815",
 "10.1561/1500000019": "The Probabilistic Relevance Framework: BM25 and Beyond. doi: 10.1561/1500000019",
 "10.48550/arxiv.2410.05779": "LightRAG: Simple and Fast Retrieval-Augmented Generation. doi: 10.48550/arXiv.2410.05779",
 "10.1177/001316446002000104": "A Coefficient of Agreement for Nominal Scales. doi: 10.1177/001316446002000104",
 "10.2307/2529310": "The Measurement of Observer Agreement for Categorical Data. doi: 10.2307/2529310",
 "10.1093/nar/gkab880": "DDInter: an online drug–drug interaction database towards improving clinical decision-making and patient safety. doi: 10.1093/nar/gkab880",
 "10.1186/s12886-026-04816-7": "Efficacy and safety of low-concentration atropine combined with orthokeratology for children with myopia: a systematic review. BMC Ophthalmology 2026. doi: 10.1186/s12886-026-04816-7",
}
ref_by_doi = {r["doi"]: r for r in refs}
final_lines = []
for i, doi in enumerate(ORDER):
    if doi in SPECIAL:
        final_lines.append(f"[{i+1}] {SPECIAL[doi]}")
    else:
        r = ref_by_doi.get(doi)
        if r:
            authors = r.get("authors") or ""
            final_lines.append(f"[{i+1}] {authors}. {r.get('title') or ''}. {r.get('journal') or ''} {r.get('year') or ''}. doi: {doi}")
        else:
            print(f"MISSING: {doi}")

P.write_text(t, encoding="utf-8")
print(f"References 写入: {len(final_lines)} 条")
