# -*- coding: utf-8 -*-
"""build_docx.py — 把 markdown 转成排版统一的 Word 文档。

统一规范（与 manuscript.docx / Supplementary_Material.docx 一致）：
Times New Roman、正文 12 pt、1.5 倍行距、标题加粗（H1 16 / H2 14 / H3 12）。

用法: python scripts/build_docx.py <input.md> <output.docx>
"""
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from finalize_docx2 import set_table_borders, fit_table_width, set_cell_margins  # noqa: E402

PANDOC = r"C:\Users\Administrator\AppData\Local\Pandoc\pandoc.exe"


def build(src: Path, dst: Path):
    tmp = dst.with_name(dst.stem + "_raw.docx")
    subprocess.run([PANDOC, str(src), "-o", str(tmp), "--standalone"], check=True)
    doc = Document(tmp)

    name = dst.name.lower()
    compact = "supp" in name or "response" in name
    body_size = 10 if "supp" in name else (10.5 if "response" in name else 12)
    table_size = 7.5 if "supp" in name else 8.5
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(body_size)
    if "supp" in name:
        normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    else:
        normal.paragraph_format.line_spacing = 1.15 if "response" in name else 1.5
    normal.paragraph_format.space_after = Pt(3 if compact else 6)
    for lvl, size in ([(1, 14), (2, 12), (3, 10.5)] if compact else [(1, 16), (2, 14), (3, 12)]):
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor(0, 0, 0)

    for p in doc.paragraphs:
        if "supp" in name:
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        else:
            p.paragraph_format.line_spacing = 1.15 if "response" in name else 1.5
        for run in p.runs:
            run.font.name = "Times New Roman"
        if p.style.name.startswith("Heading"):
            for run in p.runs:
                run.bold = True

    # Journal-style tables: three-line borders, fixed column widths, 8.5 pt cells.
    for table in doc.tables:
        rows = [[cell.text for cell in row.cells] for row in table.rows]
        if not rows:
            continue
        set_table_borders(table)
        fit_table_width(table, rows)
        set_cell_margins(table)
        for i, row in enumerate(table.rows):
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    para.paragraph_format.space_after = Pt(0)
                    for run in para.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(table_size)
                        if i == 0:
                            run.bold = True

    # Keep captions/subheadings with their table and the header row with its first data row.
    for para in doc.paragraphs:
        t = para.text.strip()
        if t.startswith("Supplementary Table S") or t.startswith("A. ") or t.startswith("B. "):
            para.paragraph_format.keep_with_next = True
    for table in doc.tables:
        if len(table.rows) > 1:
            for cell in table.rows[0].cells:
                for para in cell.paragraphs:
                    para.paragraph_format.keep_with_next = True

    # Keep rows intact; draw the closing rule only on the final row, so a table
    # that continues on the next page does not look finished at the page break.
    for table in doc.tables:
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            if trPr.find(qn("w:cantSplit")) is None:
                trPr.append(OxmlElement("w:cantSplit"))
        tblPr = table._tbl.tblPr
        borders = tblPr.find(qn("w:tblBorders"))
        if borders is not None:
            bottom = borders.find(qn("w:bottom"))
            if bottom is not None:
                bottom.set(qn("w:val"), "nil")
        for cell in table.rows[-1].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = tcPr.find(qn("w:tcBorders"))
            if tcBorders is None:
                tcBorders = OxmlElement("w:tcBorders")
                tcPr.append(tcBorders)
            el = OxmlElement("w:bottom")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "12")
            el.set(qn("w:color"), "000000")
            tcBorders.append(el)

    cp = doc.core_properties
    if "supp" in dst.name.lower():
        cp.title = ("Supplementary Material for OphDDI-CDS: An Absorption-First "
                    "Deterministic Cascade for Ophthalmic Drug-Drug Interaction Screening")
        cp.subject = "Supplementary texts and tables"
    else:
        cp.title = dst.stem.replace("_", " ").title()
    cp.author = "Guoqing Wang; Lumei Hu; Shaocheng Wang; Xianglong Yi"
    cp.last_modified_by = "Xianglong Yi"

    doc.save(dst)
    tmp.unlink(missing_ok=True)
    print(f"built {dst} ({dst.stat().st_size/1024:.0f} KB)")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())


if __name__ == "__main__":
    main()
