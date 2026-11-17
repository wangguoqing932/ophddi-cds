# -*- coding: utf-8 -*-
"""paginate_supplement.py — keep Supplementary Table S18b on a fresh page.

Word's table flow otherwise starts the S18b heading at the bottom of the S18
page. A paragraph-level pageBreakBefore is enough and does not add a blank
paragraph or a blank page.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material.docx"


def main() -> None:
    doc = Document(SRC)
    hit = False
    for p in doc.paragraphs:
        if p.text.strip().startswith("Supplementary Table S18b"):
            pPr = p._p.get_or_add_pPr()
            if pPr.find(qn("w:pageBreakBefore")) is None:
                pPr.append(OxmlElement("w:pageBreakBefore"))
            hit = True
            break
    if not hit:
        sys.exit("S18b heading not found")
    doc.save(SRC)
    print(f"page break before S18b -> {SRC}")


if __name__ == "__main__":
    main()
