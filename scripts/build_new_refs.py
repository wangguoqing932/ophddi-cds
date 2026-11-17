# -*- coding: utf-8 -*-
"""build_new_refs.py — 为新增引用生成规范条目（PubMed 元数据 + Crossref DOI 核验）。

输出 outputs/paper/new_refs_built.json：{key: {entry, verify}}。
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUT = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "new_refs_built.json"

# key -> (PMID, 用途)
PICKS = {
    "N1": ("38626948", "TRIPOD+AI 报告规范 -> §4.2 validation discipline"),
    "N2": ("35585198", "DECIDE-AI 报告规范 -> §4.2 validation discipline"),
    "N3": ("10080340", " topical ophthalmic beta-blocker 全身效应 -> Intro"),
    "N4": ("29017448", "polypharmacy 定义系统综述 -> Intro 老年用药"),
    "N5": ("42618758", "LLM 医疗安全与可靠性 -> §4.2 LLM"),
    "N6": ("42618632", "LLM 临床决策支持前瞻评估 -> §4.2 LLM"),
    "N7": ("29666228", "DeepDDI 深度学习 DDI 预测 -> §4.2 计算预测"),
    "N8": ("42670841", "知识图谱 DDI 预测 -> §4.2 计算预测"),
    "N9": ("32337561", "DDI 警报 override -> §4.2 覆盖度"),
    "N10": ("42148822", "警报疲劳系统综述 -> Intro alert-override"),
    "N11": ("33763631", "情境化 DDI 算法设计 -> §4.2 数据库对比"),
}


def get(url, tries=4):
    for a in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2 ** (a + 1))
    return {}


def normalize(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def crossref(doi):
    try:
        req = urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(doi),
                                     headers={"User-Agent": "ophddi-refcheck/1.0 (mailto:research@example.org)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            m = json.loads(r.read())["message"]
        return {
            "ok": True,
            "title": (m.get("title") or [""])[0],
            "journal": (m.get("container-title") or [""])[0],
            "year": str((m.get("issued", {}).get("date-parts") or [[""]])[0][0]),
            "volume": m.get("volume", ""),
            "issue": m.get("issue", ""),
            "page": m.get("page", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def fmt_authors(authors):
    names = [a.get("name", "") for a in authors if a.get("name")]
    if len(names) > 6:
        return ", ".join(names[:6]) + ", et al."
    return ", ".join(names)


def main():
    pmids = [p for p, _ in PICKS.values()]
    summ = get(f"{BASE}/esummary.fcgi?db=pubmed&id={','.join(pmids)}&retmode=json").get("result", {})
    built = {}
    for key, (pmid, note) in PICKS.items():
        d = summ.get(pmid, {})
        doi = ""
        for aid in d.get("articleids", []):
            if aid.get("idtype") == "doi":
                doi = aid.get("value", "")
        year = (d.get("pubdate", "") or "")[:4]
        vol, iss, pg = d.get("volume", ""), d.get("issue", ""), d.get("pages", "")
        journal = d.get("source", "")
        title = (d.get("title", "") or "").rstrip(".")
        auth = fmt_authors(d.get("authors", [])).rstrip(".")

        loc = f"{year}"
        if vol:
            loc += f";{vol}"
            if iss:
                loc += f"({iss})"
            if pg:
                loc += f":{pg}"
        entry = f"{auth}. {title}. {journal}. {loc}."
        if doi:
            entry += f" doi: {doi}"

        xr = crossref(doi) if doi else {"ok": False, "error": "no doi"}
        tmatch = False
        if xr.get("ok"):
            tmatch = normalize(title)[:60] in normalize(xr.get("title", "")) or \
                     normalize(xr.get("title", ""))[:60] in normalize(title)
        built[key] = {"pmid": pmid, "note": note, "entry": entry,
                      "verify": {"crossref_ok": xr.get("ok"), "title_match": tmatch,
                                 "crossref_journal": xr.get("journal"), "crossref_year": xr.get("year"),
                                 "crossref_page": xr.get("page"), "doi": doi}}
        flag = "OK " if (xr.get("ok") and tmatch) else "!! "
        print(f"{flag}{key}  {entry[:120]}")
        if not (xr.get("ok") and tmatch):
            print(f"      verify={built[key]['verify']}")
        time.sleep(0.4)

    OUT.write_text(json.dumps(built, indent=2, ensure_ascii=False), encoding="utf-8")
    bad = [k for k, v in built.items() if not (v["verify"]["crossref_ok"] and v["verify"]["title_match"])]
    print(f"\nsaved -> {OUT}")
    print("unverified:", bad if bad else "none — all 11 passed dual-source check")


if __name__ == "__main__":
    main()
