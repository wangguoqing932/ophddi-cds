# -*- coding: utf-8 -*-
"""finalize_docx2.py — 按行文顺序插入图/表 + 图注在图下、表注在表上。"""
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.table import Table

from redline import apply_redline, mark_runs_red
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
SUBM = ROOT / "outputs" / "deliverables"
FIG = ROOT / "outputs" / "figures"

AUTHORS = [
    "Wang Guoqing, M.D.¹; Hu Lumei, M.M.¹; Wang Shaocheng, B.M.²; Yi Xianglong, M.D., Ph.D.¹³*",
    "",
    "¹ Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China",
    "² Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital, Xinjiang, China",
    "³ Xinjiang Medical University, Urumqi, Xinjiang, China",
    "",
    "*Correspondence: Yi Xianglong, M.D., Ph.D., Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China",
    "E-mail: yixianglong1010@163.com",
    "Wang Guoqing, M.D., Resident Physician; E-mail: 17690924120@163.com",
    "Hu Lumei, M.M., Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University; E-mail: 1301161825@qq.com",
]
FUNDING = ("This study was supported by the Natural Science Foundation of Xinjiang Uygur "
           "Autonomous Region, China (Key Project No. 2022D01D68).")

FIGURES = {
    "Figure 1": FIG / "figure1_architecture.png",
    "Figure 2": FIG / "figure2_performance.png",
    "Figure 3": FIG / "figure3_expert_agreement.png",
    "Figure 4": FIG / "figure4_demo_case.png",
    "Figure 5": FIG / "figure5_reasoning_trace.png",
    "Figure 6": FIG / "figure6_workflow.png",
}
TABLES = {
    "Table 1": (ROOT / "outputs" / "tables" / "table1_registry.md",
                "Table 1. Registry summary of the knowledge base (113 ophthalmic agents, 232 systemic agents)."),
    "Table 2": (ROOT / "outputs" / "tables" / "table2_rules.md",
                "Table 2. Rule inventory: 40 mechanism rules plus 3 patient-factor policies (43 policy entries) with severity, risk type, flags, and match semantics."),
    "Table 3": (ROOT / "outputs" / "tables" / "table3_performance.md",
                "Table 3. Method performance. L1 rows use the author-derived reference set with frozen labels (primary) and corrected labels (sensitivity); audit rows use the applied and re-derived labels. 10-token rows are means over five temperature conditions; configuration 2 rows use the majority vote over five repeats."),
    "Table 4": (ROOT / "outputs" / "tables" / "table4_validation.md",
                "Table 4. Reference-level distribution of the validation sets."),
    "Table 5": (ROOT / "outputs" / "tables" / "table5_audit_strata.md",
                "Table 5. DDInter audit (92 cases): applied and re-derived reference labels, the label-independent subset, the retrieval-overlap exclusion, and the classification of the 30 disagreements."),
    "Table 6": (ROOT / "outputs" / "tables" / "table6_grade_definitions.md",
                "Table 6. Operational definitions of the three screening grades and the unassessed category, with clinical significance, expected management and an illustrative pair."),
    "Table 7": (ROOT / "outputs" / "tables" / "table7_route_aware.md",
                "Table 7. Comparison with a route-aware DDInter filter (RA-DDInter) on the 42 L1 cases with a DDInter record."),
}


def load_legends():
    """Return {"Figure N": "<title>. <body>"} parsed line by line from figure_legends.md.

    Each caption is a line beginning with "**Figure N." (title, possibly bold),
    followed by a blank line and one body paragraph. Parsing by line avoids the
    delimiter collisions that a single regex over the whole file produces.
    """
    text = (ROOT / "outputs" / "paper" / "figure_legends.md").read_text(encoding="utf-8")
    legends: dict[str, str] = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"^\*{0,2}Figure (\d+)\.\s*(.*)$", line)
        if m:
            num = m.group(1)
            title = m.group(2).strip().strip("*").strip()
            legends[f"Figure {num}"] = title
            current = f"Figure {num}"
            continue
        if current and line and not line.startswith("---") and not line.startswith("#"):
            legends[current] = (legends[current] + " " + line).strip()
    return legends


LEGENDS = load_legends()


def set_table_borders(table, header_rows: int = 1):
    """Three-line table: top rule, one rule under the header, bottom rule.

    No vertical rules and no interior rules between data rows, which is the
    standard form for journal tables. The header row is also repeated if the
    table breaks across pages.
    """
    tblPr = table._tbl.tblPr

    # table-level: only top and bottom
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", "12"), ("bottom", "12"),
                     ("left", "0"), ("right", "0"),
                     ("insideH", "0"), ("insideV", "0")):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil" if sz == "0" else "single")
        if sz != "0":
            el.set(qn("w:sz"), sz)
            el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)

    # middle rule: bottom border of the last header row
    for r in range(min(header_rows, len(table.rows))):
        for cell in table.rows[r].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = tcPr.find(qn("w:tcBorders"))
            if tcBorders is None:
                tcBorders = OxmlElement("w:tcBorders")
                tcPr.append(tcBorders)
            el = OxmlElement("w:bottom")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "6")
            el.set(qn("w:color"), "000000")
            tcBorders.append(el)

    # repeat the header row on the next page if the table splits
    for r in range(min(header_rows, len(table.rows))):
        trPr = table.rows[r]._tr.get_or_add_trPr()
        hdr = OxmlElement("w:tblHeader")
        hdr.set(qn("w:val"), "true")
        trPr.append(hdr)


def set_cell_margins(table, left_right_twips=90) -> None:
    """Add a visible gutter between columns so adjacent cells do not read as one token."""
    tblPr = table._tbl.tblPr
    if tblPr.find(qn("w:tblCellMar")) is not None:
        return
    mar = OxmlElement("w:tblCellMar")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(left_right_twips if side in ("left", "right") else 0))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def fit_table_width(table, rows):
    """Give the table a fixed total width equal to the text column.

    Word's auto layout lets wide tables run past the right margin, which is what
    produced the clipped columns in Table 2. Column width is proportional to the
    longest cell in that column, with a floor so that short headers stay legible.
    """
    usable_in = 6.4                      # A4 text width at 1 in margins, minus a hair
    n_cols = len(table.columns)

    # weight by the longest *word* rather than the whole cell, so long identifiers
    # with underscores do not steal all the width from short categorical columns
    longest = [1] * n_cols
    for r in rows:
        for j, cell in enumerate(r[:n_cols]):
            words = str(cell).replace(";", " ").split()
            w = max((len(x) for x in words), default=1)
            longest[j] = max(longest[j], min(w, 34))
    total = sum(longest)
    widths = [max(0.72, usable_in * L / total) for L in longest]
    scale = usable_in / sum(widths)
    widths = [w * scale for w in widths]

    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)

    for col, w in zip(table.columns, widths):
        col.width = Inches(w)
    for row in table.rows:
        for cell, w in zip(row.cells, widths):
            cell.width = Inches(w)


def parse_md_tables(md_path):
    """把 markdown 文件里的表格解析成若干独立表格。

    一个文件可能含多张表（如 table5 的分层表与分歧方向表），中间用空行分隔。
    早期实现把所有 "|" 行塞进同一张 docx 表格，导致第二张表的表头变成表体中段，
    且短行被填充成空单元格——版面上能直接看出来。
    """
    groups, cur = [], []
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        if ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue                      # 跳过分隔行 |---|---|
            cur.append(cells)
        elif cur:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def md_table_note(md_path):
    """取表格文件末尾的 "Note:" 说明段。

    表3 的说明定义了 10-token / 3000-token 两种预算，表5 的说明交代了更正后的
    吸收分级——都是读者理解表格所需的信息，需要随表一起排进 docx。
    """
    lines = md_path.read_text(encoding="utf-8").splitlines()
    idx = next((i for i, l in enumerate(lines) if l.strip().startswith("Note:")), None)
    if idx is None:
        return ""
    return " ".join(l.strip() for l in lines[idx:] if l.strip())


def add_break_hints(s: str) -> str:
    """Insert zero-width spaces after underscores/slashes so long identifiers wrap at separators."""
    return s


def strip_md_inline(s):
    """去掉单元格里的 markdown 标记。

    pandoc 不处理 docx 表格单元格文本，若不剥离，"**total disagreements**" 会原样
    显示在表里。
    """
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s


def table_subcaptions(md_path) -> list[str | None]:
    """Return the text preceding each table group; the first is covered by TABLES.

    Table 2 and Table 5 contain several stacked tables with their own bold
    subheadings. Pandoc drops those lines, so recover them here and print them
    between the docx tables.
    """
    caps: list[str | None] = []
    last_text: str | None = None
    in_table = False
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if s.startswith("|"):
            if not in_table:
                caps.append(last_text if caps else None)
                in_table = True
        elif s:
            in_table = False
            last_text = s
    return caps


def md_table_to_docx(doc, md_path):
    """构造 markdown 中的全部表格，按顺序返回它们的 XML 元素。

    返回列表而非单张表：调用方用 addprevious 把元素搬到文末图表区，若只返回首张，
    同一文件里的后续表格会留在文档末尾。
    """
    out = []
    subcaptions = table_subcaptions(md_path)
    for gi, rows in enumerate(parse_md_tables(md_path)):
        if gi:                                # 同一文件内的后续表格另起一张
            cap_text = subcaptions[gi] if gi < len(subcaptions) else None
            if cap_text and md_path.name.startswith("table5") and not cap_text.startswith("**Table"):
                cap_text = f"Table 5 (continued). {cap_text}"
            if cap_text:
                cap = make_caption(doc, cap_text, size=10, keep_next=True)
                out.append(cap._p)
            else:
                out.append(doc.add_paragraph()._p)
        n_rows, n_cols = len(rows), max(len(r) for r in rows)
        table = doc.add_table(rows=n_rows, cols=n_cols)
        set_table_borders(table)
        fit_table_width(table, rows)
        if n_cols == 6 and rows[0] and rows[0][0].strip().lower() == "policy":
            widths = [0.95, 0.55, 1.55, 0.55, 1.45, 1.45]
            table.autofit = False
            grid = table._tbl.tblGrid
            for col, w in zip(grid.gridCol_lst, widths):
                col.set(qn("w:w"), str(int(w * 1440)))
            for j, w in enumerate(widths):
                table.columns[j].width = Inches(w)
            for row in table.rows:
                for cell, w in zip(row.cells, widths):
                    cell.width = Inches(w)
        set_cell_margins(table)
        for i, r in enumerate(rows):
            for j in range(n_cols):
                cell = table.cell(i, j)
                cell.text = add_break_hints(strip_md_inline(r[j])) if j < len(r) else ""
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(8.5)
                        if i == 0:
                            run.bold = True
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            if trPr.find(qn("w:cantSplit")) is None:
                trPr.append(OxmlElement("w:cantSplit"))
        # Closing rule only on the final row; a table continuing on the next page
        # must not look finished at the page break.
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
        if n_rows <= 8:
            for row in table.rows[:-1]:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        para.paragraph_format.keep_with_next = True
        out.append(table._tbl)
    return out


def make_para(doc, text, size=10, bold=False, center=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def make_caption(doc, text, size=10, center=False, keep_next=False):
    """图注/表注：标签（Figure N./Table N.）加粗，正文常规。

    传入的文本可能带有 markdown 的 **粗体** 与 `代码` 标记（图注源文件就是这样
    写的）。这里把它们解析成 run 级格式，否则星号和反引号会原样印在 PDF 上。
    """
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = keep_next
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    # split on **bold** and `code` spans, keeping the delimiters out of the text
    tokens = re.split(r"(\*\*.+?\*\*|`[^`]+`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            run = p.add_run(tok[2:-2]); run.bold = True
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            run = p.add_run(tok[1:-1]); run.font.name = "Courier New"
        else:
            run = p.add_run(tok)
        run.font.name = run.font.name or "Times New Roman"
        run.font.size = Pt(size)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def add_line_numbers(doc):
    """BMC 投稿要求行号（连续编号）。"""
    for section in doc.sections:
        ln = OxmlElement("w:lnNumType")
        ln.set(qn("w:countBy"), "1")
        ln.set(qn("w:restart"), "continuous")
        ln.set(qn("w:distance"), "360")
        section._sectPr.append(ln)


def add_page_numbers(doc):
    """BMC 投稿要求页码，居中置于页脚。"""
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), " PAGE ")
        run = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.text = "1"
        run.append(t)
        fld.append(run)
        p._p.append(fld)


def build_docx(out_path=None, marked_keys=None, redline_old_blocks=None, red_tables=None, red_figures=None):
    """生成 docx。

    out_path     输出路径，默认为 outputs/deliverables/manuscript.docx
    marked_keys  旧接口：整段标红（保留兼容）
    redline_old_blocks  旧版本文本块；给定时按词级 diff 只标红改动词
    red_tables   需要整表标红的表键集合（表被重建/新增时）
    red_figures  需要标红图注的图键集合
    """
    pandoc = r"C:\Users\Administrator\AppData\Local\Pandoc\pandoc.exe"
    src_md = ROOT / "outputs" / "paper" / "manuscript.en.md"
    author_paras = []      # 构建时注入的作者块，标红时需单独处理
    tmpdir = tempfile.TemporaryDirectory()
    tmp = Path(tmpdir.name) / "manuscript_raw.docx"
    subprocess.run([pandoc, str(src_md), "-o", str(tmp), "--standalone"], check=True)
    doc = Document(tmp)

    # 字号层级（统一规范）：标题 16 / 一级节 14 / 二级节 12 / 正文 11 /
    # 图表注 10 / 表注脚注 9 / 表格 8.5。相邻层级严格区分，全文只用 Times New Roman。
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    normal.paragraph_format.space_after = Pt(6)
    for lvl, size in [(1, 16), (2, 14), (3, 12)]:
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    for p in doc.paragraphs:
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        for run in p.runs:
            run.font.name = "Times New Roman"
        if p.style.name.startswith("Heading"):
            for run in p.runs:
                run.bold = True

    paras = doc.paragraphs
    abstract_idx = next((i for i, p in enumerate(paras) if p.text.strip() == "Abstract"), None)
    already = any(AUTHORS[0] in p.text for p in doc.paragraphs)
    if abstract_idx is not None and not already:
        for text in AUTHORS:
            p = paras[abstract_idx].insert_paragraph_before(text)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            for run in p.runs:
                run.font.name = "Times New Roman"
            # 作者块是构建时注入的，不在 markdown 源里，因此段落 diff 看不到它；
            # 标红版需要显式标记（审稿编辑曾指出"新增作者未在标红版中体现"）。
            author_paras.append(p)

    for p in doc.paragraphs:
        if "[To be completed. If none, state: This research received no specific grant" in p.text:
            p.text = FUNDING
            for run in p.runs:
                run.font.name = "Times New Roman"

    if redline_old_blocks:
        apply_redline(doc, redline_old_blocks)

    # 文末集中插入：References 前，先表格（表注+表）后图片（图+图注）
    refs_idx = next((i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "References"), None)
    anchor = doc.paragraphs[refs_idx]._p if refs_idx else doc.paragraphs[-1]._p
    # 目标顺序：Table 1..6（表注+表）→ Figure 1..5（图+图注）
    # addprevious 会倒序，所以先处理图片（Figure 5->1），再表格（Table 6->1）。
    for key in ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6", "Table 7"]:
        md_path, caption_text = TABLES[key]
        cap = make_caption(doc, caption_text, keep_next=True)
        if red_tables and key in red_tables:
            mark_runs_red(cap)
        anchor.addprevious(cap._p)            # 先表注，再依序放该文件内的所有表格
        for el in md_table_to_docx(doc, md_path):
            if red_tables and key in red_tables and el.tag.endswith("}tbl"):
                tbl = Table(el, doc._body)
                for row in tbl.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            mark_runs_red(para)
            anchor.addprevious(el)
        note = md_table_note(md_path)
        if note:
            anchor.addprevious(make_para(doc, strip_md_inline(note), size=9)._p)
    for key in ["Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 5", "Figure 6"]:
        img_p = doc.add_paragraph()
        img_p.paragraph_format.keep_with_next = True   # image stays on the same page as its caption
        img_p.paragraph_format.keep_together = True
        img_p.paragraph_format.space_before = Pt(6)
        img_p.paragraph_format.space_after = Pt(2)
        run = img_p.add_run()
        width_in = 5.2 if key == "Figure 6" else 6.4
        run.add_picture(str(FIGURES[key]), width=Inches(width_in))
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = make_caption(doc, f"**{key}.** {LEGENDS.get(key, '')}")
        if red_figures and key in red_figures:
            mark_runs_red(cap)
        cap.paragraph_format.keep_together = True
        cap.paragraph_format.keep_with_next = False
        cap.paragraph_format.space_before = Pt(2)
        anchor.addprevious(img_p._p)
        anchor.addprevious(cap._p)
    print("图表已集中插入文末（先表格后图片）")

    # ── 标红改动段落（标红版专用，正文与图表均已就位后再执行）──
    if marked_keys:
        # 与 build_marked_docx.normalize 保持一致的规范化，否则含弯引号的段落匹配不上。
        def _norm(s: str) -> str:
            s = re.sub(r"\s+", " ", s).strip()
            for a, b in (("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"),
                         ("\u2019", "'"), ("\u2013", "-"), ("\u2014", "-")):
                s = s.replace(a, b)
            return s

        keys = [_norm(k) for k in marked_keys if k]
        marked = 0
        # 作者块由构建时注入，段落 diff 看不到它；本轮作者名单有增补，
        # 必须标红，否则"标红版"与"作者已变更"自相矛盾（编辑曾指出）。
        for p in author_paras:
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
            marked += 1
        for p in doc.paragraphs:
            flat = _norm(p.text)
            if not flat:
                continue
            if any(flat.startswith(k[:80]) or k[:80] in flat for k in keys):
                for r in p.runs:
                    r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
                marked += 1
        # 正文中的 markdown 表格会被 pandoc 转成 docx 表格对象，段落遍历看不到它们。
        # docx 行文本不含 "|"，因此需把传入的 markdown 表格行解析成单元格元组后按行比对。
        row_keys = []
        for k in keys:
            if k.startswith("|") and k.endswith("|") and k.count("|") >= 3:
                cells = tuple(c.strip().lower() for c in k.strip("|").split("|"))
                if not all(set(c) <= set("-: ") for c in cells):
                    row_keys.append(cells)
        for tbl in doc.tables:
            for row in tbl.rows:
                cells = tuple(c.text.strip().lower() for c in row.cells)
                if any(len(rk) == len(cells) and all(a == b for a, b in zip(rk, cells))
                       for rk in row_keys):
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            for r in p.runs:
                                r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
                    marked += 1
        # 表注与图注同样可能被改动
        print(f"标红行/段: {marked}")

    add_line_numbers(doc)
    add_page_numbers(doc)

    cp = doc.core_properties
    cp.title = ("OphDDI-CDS: An Absorption-First Deterministic Cascade for "
                "Ophthalmic Drug-Drug Interaction Screening")
    cp.author = "Guoqing Wang; Lumei Hu; Shaocheng Wang; Xianglong Yi"
    cp.subject = "Ophthalmic drug-drug interaction clinical decision support"
    cp.keywords = ("drug-drug interaction; ophthalmic; systemic absorption; "
                   "clinical decision support; deterministic rules")
    cp.last_modified_by = "Xianglong Yi"

    out = Path(out_path) if out_path else (SUBM / "manuscript.docx")
    doc.save(out)
    tmpdir.cleanup()
    print(f"saved: {out} ({out.stat().st_size / 1024:.0f} KB)")


def main():
    build_docx()


if __name__ == "__main__":
    main()
