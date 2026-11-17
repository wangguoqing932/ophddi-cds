# -*- coding: utf-8 -*-
"""Scan PubMed for pair-specific ophthalmic outcome literature.

For each high-risk disagreement pair, run two queries:
  1) both drugs + an ophthalmic/topical/eye term
  2) both drugs only
and return counts plus the top titles. This is a scoping scan, not a systematic
review and not an independent adjudication of the 30 audit cases.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "audits" / "pubmed_outcome_scan.json"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

PAIRS = [
    ("D3-001", "Timolol", "Theophylline", "unsupported_undergrading"),
    ("D3-004", "Timolol", "Epinephrine", "unsupported_undergrading"),
    ("D3-006", "Scopolamine", "Topiramate", "unsupported_undergrading"),
    ("D3-014", "Timolol", "Spironolactone", "unsupported_undergrading"),
    ("D3-018", "Carteolol", "Diazepam", "unsupported_undergrading"),
    ("D3-026", "Apraclonidine", "Linezolid", "ddinter_high_default_path"),
    ("D3-029", "Betaxolol", "Clonidine", "ddinter_high_default_path"),
    ("D3-033", "Homatropine", "Topiramate", "ddinter_high_default_path"),
    ("D3-080", "Aflibercept", "Leflunomide", "ddinter_high_default_path"),
    ("D3-035", "Apraclonidine", "Midazolam", "system_overgrading"),
    ("D3-038", "Apraclonidine", "Loperamide", "system_overgrading"),
    ("D3-057", "Tacrolimus", "Ibuprofen", "system_overgrading"),
    ("D3-063", "Bromfenac", "Enalapril", "system_overgrading"),
]
OPH = '(ophthalmic[tiab] OR topical[tiab] OR "eye drops"[tiab] OR eye[tiab] OR ocular[tiab] OR intravitreal[tiab])'


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def esearch(term: str, retmax: int = 10) -> dict:
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json",
                                "retmax": retmax, "sort": "relevance",
                                "tool": "ophddi_cds_audit", "email": "registry@example.invalid"})
    return get(f"{BASE}/esearch.fcgi?{q}")


def esummary(pmids: list[str]) -> dict:
    if not pmids:
        return {}
    q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
                                "retmode": "json", "tool": "ophddi_cds_audit",
                                "email": "registry@example.invalid"})
    return get(f"{BASE}/esummary.fcgi?{q}").get("result", {})


def main() -> None:
    out = []
    for cid, a, b, cls in PAIRS:
        pair = f"({a}[tiab] AND {b}[tiab])"
        for label, term in (("ophthalmic", f"{pair} AND {OPH}"), ("pair_only", pair)):
            try:
                r = esearch(term)
                ids = r.get("esearchresult", {}).get("idlist", [])
                count = int(r.get("esearchresult", {}).get("count", 0))
            except Exception as e:  # network/API failure should be visible, not silent
                out.append({"case": cid, "pair": [a, b], "class": cls, "query": label,
                            "count": None, "error": repr(e), "items": []})
                time.sleep(0.4)
                continue
            summary = esummary(ids)
            items = []
            for pmid in ids:
                rec = summary.get(pmid, {})
                items.append({"pmid": pmid, "title": rec.get("title", ""),
                              "journal": rec.get("fulljournalname", ""),
                              "year": (rec.get("pubdate", "") or "")[:4]})
            out.append({"case": cid, "pair": [a, b], "class": cls, "query": label,
                        "term": term, "count": count, "items": items})
            time.sleep(0.4)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for row in out:
        if row["query"] != "ophthalmic":
            continue
        print(f'{row["case"]} {row["pair"][0]}+{row["pair"][1]}: oph {row["count"]}')
        for it in row["items"][:3]:
            print(f'   {it["pmid"]} {it["year"]} {it["title"][:110]}')
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
