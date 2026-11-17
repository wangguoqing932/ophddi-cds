# -*- coding: utf-8 -*-
"""finalize_docx.py — 生成最终投稿 Word：Times New Roman、1.5 行距、
作者信息、Funding、图片与表格插入相应位置。"""
import csv
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

ROOT = Path(__file__).resolve().parents[1]
SUBM = ROOT / "outputs" / "submission"
FIG = ROOT / "outputs" / "figures"

AUTHORS = [
    "Guoqing Wang, M.M.\u00b9\u00b2; Xianglong Yi, M.D., Ph.D.\u00b9\u00b2*",
    "",
    "\u00b9 Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, China",
    "\u00b2 Xinjiang Medical University, Urumqi, China",
    "",
    "*Corresponding Author: Xianglong Yi, M.D., Ph.D., Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, China",
    "Email: yixianglong1010@163.com  |  Tel: 436-1200",
]
FUNDING = ("This study was supported by the Natural Science Foundation of Xinjiang Uygur "
           "Autonomous Region, China (Key Project No. 2022D01D68).")

# 图片/表格插入点：定位段落文本（首次出现的段落）-> 插入对象
FIGURES = {
    "Figure 1": {"file": FIG / "figure1_architecture.png", "anchor": "The production system (full_system) is a three-layer deterministic cascade"},
    "Figure 2": {"file": FIG / "figure2_performance.png", "anchor": "Table 3 and Figure 2 summarize"},
    "Figure 3": {"file": FIG / "figure3_expert_agreement.png", "anchor": "inter-rater agreement 91.7%"},
    "Figure 4": {"file": FIG / "figure4_demo_case.png", "anchor": "Figure 4 illustrates representative system outputs"},
    "Figure 5": {"file": FIG / "figure5_reasoning_trace.png", "anchor": "Figure 5; supplementary table"},
}
TABLES = {
    "Table 1": {"file": ROOT / "outputs" / "tables" / "table1_registry.md", "anchor": "113 ophthalmic topical agents and 232 systemic medications (Table 1)"},
    "Table 2": {"file": ROOT / "outputs" / "tables" / "table2_rules.md", "anchor": "with mandatory retraction screening (Table 2)"},
    "Table 3": {"file": ROOT / "outputs" / "tables" / "table3_performance.md", "anchor": "Table 3 and Figure 2 summarize"},
    "Table 4": {"file": ROOT / "outputs" / "tables" / "table4_validation.md", "anchor": "58 guideline cases (Table 4)"},
}


def _set_table_borders(table):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:color'), '000000')
        borders.append(el)
    tblPr.append(borders)


def md_table_to_docx(doc, md_path, caption):
    """解析 markdown 表格并插入 docx 表格。"""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    rows = []
    for ln in lines:
        if ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            rows.append(cells)
    if not rows:
        return None
    n_rows, n_cols = len(rows), max(len(r) for r in rows)
    table = doc.add_table(rows=n_rows, cols=n_cols)
    _set_table_borders(table)
    for i, r in enumerate(rows):
        for j in range(n_cols):
            cell = table.cell(i, j)
            cell.text = r[j] if j < len(r) else ""
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(9)
    doc.add_paragraph(caption).runs[0].bold = True if doc.paragraphs[-1].runs else None
    return table


def main():
    src_md = ROOT / "outputs" / "paper" / "manuscript.en.md"
    import subprocess
    pandoc = r"C:\Users\Administrator\AppData\Local\Pandoc\pandoc.exe"
    tmp_docx = SUBM / "manuscript_raw.docx"
    subprocess.run([pandoc, str(src_md), "-o", str(tmp_docx), "--standalone"], check=True)

    doc = Document(tmp_docx)

    # 1) Normal 样式：Times New Roman + 1.5 行距
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(6)
    # 标题样式
    for lvl, size in [(1, 16), (2, 14), (3, 12)]:
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.font.bold = True
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        st.paragraph_format.space_before = Pt(12)
        st.paragraph_format.space_after = Pt(6)

    # 2) 全文档段落应用字体（含已有 run）
    for p in doc.paragraphs:
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        for run in p.runs:
            run.font.name = "Times New Roman"

    # 3) 定位插入点（段落索引）
    paras = doc.paragraphs
    idx_fig = {}
    idx_tab = {}
    for i, p in enumerate(paras):
        txt = p.text.strip()
        for k, spec in FIGURES.items():
            if k not in idx_fig and spec["anchor"] in txt:
                idx_fig[k] = i
        for k, spec in TABLES.items():
            if k not in idx_tab and spec["anchor"] in txt:
                idx_tab[k] = i
    print("图片锚点:", idx_fig)
    print("表格锚点:", idx_tab)

    # 4) 作者块插入（在 Abstract 前）
    abstract_idx = next((i for i, p in enumerate(paras) if p.text.strip() == "Abstract"), None)
    if abstract_idx is not None:
        for k, text in enumerate(AUTHORS):
            p = paras[abstract_idx].insert_paragraph_before(text)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            for run in p.runs:
                run.font.name = "Times New Roman"
        print("作者信息已插入（Abstract 前）")

    # 5) 图片插入（在锚点段落后）
    # 用 XML 方式在段落后插入（python-docx 无直接 after 插入 -> 用 add_picture 后移动）
    # 简单方案：定位锚点段落后插入新段落+图片
    def insert_after(doc, anchor_para_idx, kind, payload):
        anchor = doc.paragraphs[anchor_para_idx]
        new_p = doc.add_paragraph()
        # 移动到 anchor 之后：通过 XML
        anchor._p.addnext(new_p._p)
        if kind == "image":
            run = new_p.add_run()
            run.add_picture(str(payload), width=Inches(5.5))
            new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            # 图题
            cap = doc.add_paragraph()
            anchor._p.addnext(cap._p)
            cap_run = cap.add_run("Figure X")
            cap_run.bold = True
        return new_p

    # 按段落索引降序插入（避免索引漂移）
    for k, i in sorted(idx_fig.items(), key=lambda x: -x[1]):
        anchor = doc.paragraphs[i]
        img_p = doc.add_paragraph()
        anchor._p.addnext(img_p._p)
        run = img_p.add_run()
        run.add_picture(str(FIGURES[k]["file"]), width=Inches(5.5))
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph(k)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p._p.addnext(cap._p)
        for run2 in cap.runs:
            run2.font.name = "Times New Roman"
            run2.font.size = Pt(10)
            run2.bold = True

    # 6) 表格插入（锚点段落后）
    for k, i in sorted(idx_tab.items(), key=lambda x: -x[1]):
        anchor = doc.paragraphs[i]
        tbl_p = doc.add_paragraph()
        anchor._p.addnext(tbl_p._p)
        # 表格插入在锚点后
        table = md_table_to_docx(doc, TABLES[k]["file"], f"{k}: caption")
        if table is not None:
            anchor._p.addnext(table._tbl)

    # 7) Funding 更新（替换占位）
    for p in doc.paragraphs:
        if "[To be completed. If none, state: This research received no specific grant from any funding agency.]" in p.text:
            p.text = FUNDING
            for run in p.runs:
                run.font.name = "Times New Roman"
            print("Funding 已填入")

    out = SUBM / "manuscript.docx"
    doc.save(out)
    print(f"saved: {out} ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
