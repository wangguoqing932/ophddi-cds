# -*- coding: utf-8 -*-
"""final_consistency_check.py — hard gate after the revision fixes."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import fitz
from docx import Document
from docx.shared import RGBColor

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "outputs/paper/manuscript.en.md"
SUP = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material.md"
MS_PDF = ROOT / "outputs/deliverables/manuscript.pdf"
SUP_PDF = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material.pdf"
FRONT = ROOT / "outputs/deliverables/frontiers"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pdf_text(path: Path) -> str:
    return re.sub(r"\s+", " ", "\n".join(p.get_text() for p in fitz.open(path)))


ms = text(MS)
sup = text(SUP)
ms_pdf = pdf_text(MS_PDF)
sup_pdf = pdf_text(SUP_PDF)

# 1. Page counts
check("main PDF 53 pages", len(fitz.open(MS_PDF)) == 53, str(len(fitz.open(MS_PDF))))
check("supplement PDF 32 pages", len(fitz.open(SUP_PDF)) == 32, str(len(fitz.open(SUP_PDF))))

# 2. Counts
abstract = re.search(r"## Abstract\s*\n(.*?)\n\n## ", ms, re.S).group(1)
check("abstract 346 words", len(abstract.split()) == 346, str(len(abstract.split())))
body = ms.split("## References")[0]
i, j = body.find("## 1. Introduction"), body.find("## Keywords")
imrad = re.sub(r"^#+ .*$", "", body[i:j], flags=re.M)
check("main text 8,184 words", len(imrad.split()) == 8184, str(len(imrad.split())))
check("45 references", len(re.findall(r"^\[\d+\]", ms.split("## References")[-1], re.M)) == 45)

# 3. Fixed numbers / stale numbers
for token in ("0.882", "0.984", "0.977"):
    check(f"manuscript has {token}", token in ms_pdf)
for token in ("0.353", "76.1%", "maximum of the rule and matrix layers", "maximum of the two layers"):
    check(f"manuscript free of {token!r}", token not in ms and token not in ms_pdf)
check("abstract includes token allowance", "model, token allowance and sampling" in abstract)
check("manuscript has three-layer maximum", "maximum of the three layers" in ms)

check("supplement has 77.7%", "77.7%" in sup and "77.7%" in sup_pdf)
check("supplement free of 76.1%", "76.1%" not in sup and "76.1%" not in sup_pdf)
check("supplement S13 uses rule_context", "| applied | all 92 | rule_context |" in sup)

# 4. Response numbering
r1 = text(ROOT / "outputs/submission/response_to_reviewers_r1.md")
check("R1 response says S1-S19", "Tables S1-S19" in r1 and "Tables S1-S18" not in r1)

# 5. Metadata
front_readme = text(FRONT / "README.md")
status = text(ROOT / "SUBMISSION_STATUS.md")
for label, cond in [
    ("frontiers README abstract 346", "| Abstract | 346 words |" in front_readme),
    ("frontiers README main 8,184", "| 8,184 words |" in front_readme),
    ("frontiers README 19 supplementary tables", "19 supplementary tables" in front_readme),
    ("status says 32-page supplement", "32 页" in status),
    ("status says 8,184 words", "8,184 词" in status),
]:
    check(label, cond)

# 6. Supplement numbering
for n in range(1, 20):
    check(f"S{n} heading once", sup.count(f"Supplementary Table S{n}.") == 1, str(sup.count(f"Supplementary Table S{n}.")))
for n in range(1, 11):
    check(f"Text S{n} heading once", sup.count(f"Supplementary Text S{n}.") == 1, str(sup.count(f"Supplementary Text S{n}.")))

# 7. Numbers files
nums = json.loads(text(ROOT / "outputs/recomputed/numbers.json"))
for method, acc in [("pure_llm", 0.6304), ("naive_rag", 0.5348), ("rule_context", 0.6022)]:
    got = nums[f"audit.multi.{method}"]["acc3"]
    check(f"numbers audit.multi {method}", abs(got - acc) < 5e-4, f"{got:.4f}")
dev = json.loads(text(ROOT / "outputs/recomputed/development_gate_metrics.json"))
check("dev internal gated sens 0.8824", abs(dev["gated"]["internal_validation_78"]["sensitivity_high"] - 0.8824) < 1e-4)
check("dev internal gated spec 0.9836", abs(dev["gated"]["internal_validation_78"]["specificity_high"] - 0.9836) < 1e-4)
check("dev200 gated spec 0.9766", abs(dev["gated"]["dev_ddinter_200"]["specificity_high"] - 0.9766) < 1e-4)
gate = json.loads(text(ROOT / "outputs/recomputed/rule_gating_experiment.json"))
check("S19 ungated corrected 106/118", gate["ungated"]["l1"]["corrected"]["correct"] == 106)

# 7b. Cross-document numeric claims that previously drifted
check("kappa CI matches numbers.json",
      "0.678-0.870" in ms_pdf and "0.676-0.871" not in ms and "0.676-0.871" not in ms_pdf)
for name, b, c in [("pure_llm", 48, 2), ("naive_rag", 54, 4), ("lightrag", 19, 3)]:
    entry = nums[f"l1.frozen.mcnemar_vs_{name}"]
    check(f"frozen McNemar {name}", (entry["b"], entry["c"]) == (b, c), f"{entry['b']}/{entry['c']}")
check("9,600 rows stated with 480 cases", "480 cases" in ms and "9,600 rows" in ms)
check("157 low-tier has 83 within 1,933", "83 within the 1,933" in ms)
check("Figure 6 legend uses 33 defined-cell keys", "33 with defined cells" in ms_pdf and "34 used" not in ms_pdf)
check("abstract uses author-derived cases", "118 author-derived cases" in abstract)
check("no false development-free claim", "without development exposure" not in ms and "no development exposure" not in ms)
check("B-only frozen/corrected results present", "18 of 20" in ms and "20 of 20" in ms)
check("RA 296 tier breakdown present", "194 medium-tier and 102 high-tier" in ms)
check("expert mapping is 11 of 12 blind cases", "eleven are from the frozen blind subset" in ms)
check("1,933 decision paths updated",
      all(x in ms for x in ["504 pairs (26.1%)", "507 (26.2%)", "746 (38.6%)", "176 (9.1%)"]))
check("assessed downgrade share updated", "1,341 (76.3%)" in ms)
check("unassessed composition updated",
      "151 DDInter-medium, 10 DDInter-high and 15 DDInter-low" in ms)
check("Figure 1 shares updated", all(x in ms_pdf for x in ["25.7%", "42.9%", "19.7%"]))

# 8. Table row counts
def table_rows(start: str, end: str) -> int:
    block = sup.split(start)[1].split(end)[0]
    return len([l for l in block.splitlines() if l.startswith("|") and "---" not in l]) - 1

check("S5 has 113 rows", table_rows("**Supplementary Table S5.", "**Supplementary Table S5b") == 113)
check("S14 has 104 rows", table_rows("**Supplementary Table S14.", "**Supplementary Table S15") == 104)
check("S2 has 30 rows", table_rows("**Supplementary Table S2.", "**Supplementary Table S3") == 30)
check("S18 has 42 rows", table_rows("**Supplementary Table S18.", "**Supplementary Table S18b") == 42)
check("S18b present", "**Supplementary Table S18b." in sup)
check("S18b has binary analysis", "Binary analysis (C/D/X actionable)" in sup)

# 9. Redline distribution
marked = Document(ROOT / "outputs/deliverables/manuscript_marked_changes.docx")
full = part = black = 0
for p in marked.paragraphs:
    runs = [r for r in p.runs if r.text.strip()]
    if not runs:
        continue
    red = sum(len(r.text.split()) for r in runs if r.font.color and r.font.color.rgb == RGBColor(0xC0, 0, 0))
    blk = sum(len(r.text.split()) for r in runs if not (r.font.color and r.font.color.rgb == RGBColor(0xC0, 0, 0)))
    if red and not blk:
        full += 1
    elif red:
        part += 1
    else:
        black += 1
check("redline 57 full / 87 partial / 51 black", (full, part, black) == (57, 87, 51), f"{full}/{part}/{black}")

# 10. Source vs frontiers hashes
for name in ["manuscript.md", "manuscript.docx", "manuscript.pdf",
             "Supplementary_Material.md", "Supplementary_Material.docx", "Supplementary_Material.pdf",
             "response_to_reviewers_r1.md", "response_to_reviewers_r1.pdf"]:
    src = (ROOT / "outputs/deliverables" / name) if name.startswith("manuscript") else \
          (ROOT / "outputs/deliverables/supplementary_files" / name) if name.startswith("Supplementary") else \
          (ROOT / "outputs/submission" / name)
    dst = FRONT / name
    h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    check(f"frontiers copy {name}", src.exists() and dst.exists() and h(src) == h(dst))

# 11. Form fields
form = json.loads(text(FRONT / "_form_fields.json"))
check("form abstract 346", len(form["abstract"].split()) == 346, str(len(form["abstract"].split())))
plain = text(FRONT / "_abstract_plain.txt")
check("plain abstract 346", len(plain.split()) == 346, str(len(plain.split())))

# report
fails = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
print(f"\nTOTAL {len(results)}  PASS {len(results)-len(fails)}  FAIL {len(fails)}")
sys.exit(1 if fails else 0)
