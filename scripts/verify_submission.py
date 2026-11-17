# -*- coding: utf-8 -*-
"""verify_submission.py — 内容级 QC：docx 字数/引用数/残留重复句/表格图数量。"""
import re
import sys
from pathlib import Path

from docx import Document

DOCX = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds\outputs\submission\manuscript.docx")
MD = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds\outputs\paper\manuscript.en.md")

d = Document(str(DOCX))
text = "\n".join(p.text for p in d.paragraphs)
print("docx words:", len(re.findall(r"\S+", text)))
print("refs listed:", len(re.findall(r"^\[\d+\] ", text, re.M)))
probes = [
    "Topical carteolol can likewise", "Ocular drug transfer from systemic",
    "although pharmacovigilance analyses", "29 disagreements", "0.398",
    "10 of 12 cases one level lower", "229 agents", "kappa 0.840",
    "negative system", "only fully concordant case was R07",
    "There's Danger in the Drops", "[33] [28]", "Haynes",
]
for p in probes:
    print(f"  '{p}': {text.count(p)}x")
print("tables in docx:", len(d.tables))
print("inline images:", len(d.inline_shapes))

md = MD.read_text(encoding="utf-8")
body = md.split("## References")[0]
first = []
for cm in re.finditer(r"\[([\d,\-]+)\]", body):
    for part in cm.group(1).split(","):
        if re.match(r"^\d+$", part):
            n = int(part)
        elif re.match(r"^(\d+)-(\d+)$", part):
            lo, hi = map(int, re.match(r"^(\d+)-(\d+)$", part).groups())
            for n in range(lo, hi + 1):
                if n not in first:
                    first.append(n)
            continue
        if n not in first:
            first.append(n)
print("citation first-appearance monotonic:", first == sorted(first), "| n cited:", len(first))
refs_section = md.split("## References")[1]
listed = [int(m.group(1)) for m in re.finditer(r"^\[(\d+)\]", refs_section, re.M)]
print("listed refs:", len(listed), "| missing:", sorted(set(range(1, 30)) - set(first)))
