# -*- coding: utf-8 -*-
"""fix_docx_pagination.py — keep table captions with their tables and unsplit small tables."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt


def is_caption(text: str) -> bool:
    t = text.strip()
    return (t.startswith("Supplementary Table S") or t.startswith("Table S")
            or t.startswith("Supplementary Figure S") or t.startswith("Figure S"))


def keep_row_together(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:cantSplit")) is None:
        trPr.append(OxmlElement("w:cantSplit"))


def main(path: str) -> None:
    p = Path(path)
    doc = Document(p)
    for para in doc.paragraphs:
        if not is_caption(para.text):
            continue
        para.paragraph_format.keep_with_next = True
        nxt = para._p.getnext()
        if nxt is not None and nxt.tag.endswith("}p") and not "".join(nxt.itertext()).strip():
            for q in doc.paragraphs:
                if q._p is nxt:
                    q.paragraph_format.keep_with_next = True
                    break
    for table in doc.tables:
        tblPr = table._tbl.tblPr
        if tblPr.find(qn("w:tblCellMar")) is None:
            mar = OxmlElement("w:tblCellMar")
            for side in ("top", "left", "bottom", "right"):
                el = OxmlElement(f"w:{side}")
                el.set(qn("w:w"), "90" if side in ("left", "right") else "0")
                el.set(qn("w:type"), "dxa")
                mar.append(el)
            tblPr.append(mar)
        header = " ".join(c.text for c in table.rows[0].cells).lower() if table.rows else ""
        size = 7.2 if ("ophthalmic row key" in header or "ra-ddinter" in header) else (7.5 if "patient factor" in header else 8)
        rows = table.rows
        for row in rows:
            keep_row_together(row)
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(size)
                        # no zero-width break hints: they render as visible gaps in Word
        if len(rows) <= 12:
            for row in rows[:-1]:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        para.paragraph_format.keep_with_next = True
        # repeat header row
        for row in rows[:1]:
            trPr = row._tr.get_or_add_trPr()
            if trPr.find(qn("w:tblHeader")) is None:
                hdr = OxmlElement("w:tblHeader")
                hdr.set(qn("w:val"), "true")
                trPr.append(hdr)
    doc.save(p)
    print("fixed", p)


if __name__ == "__main__":
    main(sys.argv[1])
