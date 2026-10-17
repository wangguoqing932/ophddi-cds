# -*- coding: utf-8 -*-
"""finalize_docx2.py — 按行文顺序插入图/表 + 图注在图下、表注在表上。"""
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
SUBM = ROOT / "outputs" / "deliverables"
FIG = ROOT / "outputs" / "figures"

AUTHORS = [
    "Wang Guoqing, M.D.\u00b9; Hu Lumei, M.D.\u00b9; Wang Shaocheng, M.D.\u00b3; Yi Xianglong, M.D., Ph.D.\u00b9\u00b2*",
    "",
    "\u00b9 Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China",
    "\u00b2 Xinjiang Medical University, Urumqi, Xinjiang, China",
    "\u00b3 Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital, Xinjiang, China",
    "",
    "*Correspondence: Yi Xianglong, M.D., Ph.D., Professor of Ophthalmology, Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University, Urumqi, Xinjiang, China",
    "E-mail: yixianglong1010@163.com",
    "Wang Guoqing, M.D., Resident Physician; E-mail: 17690924120@163.com",
    "Hu Lumei, M.D., Department of Ophthalmology, The First Affiliated Hospital of Xinjiang Medical University; E-mail: 1301161825@qq.com",
    "Wang Shaocheng, M.D., Department of Gastroenterology, Xinjiang Production and Construction Corps Third Division General Hospital; E-mail: 13150407698@163.com",
]
FUNDING = ("This study was supported by the Natural Science Foundation of Xinjiang Uygur "
           "Autonomous Region, China (Key Project No. 2022D01D68).")

FIGURES = {
    "Figure 1": FIG / "figure1_architecture.png",
    "Figure 2": FIG / "figure2_performance.png",
    "Figure 3": FIG / "figure3_expert_agreement.png",
    "Figure 4": FIG / "figure4_demo_case.png",
    "Figure 5": FIG / "figure5_reasoning_trace.png",
}
TABLES = {
    "Table 1": (ROOT / "outputs" / "tables" / "table1_registry.md",
                "Table 1. Registry summary of the knowledge base (113 ophthalmic agents, 232 systemic agents)."),
    "Table 2": (ROOT / "outputs" / "tables" / "table2_rules.md",
                "Table 2. Rule inventory: 40 mechanism rules plus 3 patient-factor policies (43 policy entries) with severity, risk type, flags, and match semantics."),
    "Table 3": (ROOT / "outputs" / "tables" / "table3_performance.md",
                "Table 3. Four-method performance on the two validation sets (mean over five temperature conditions)."),
    "Table 4": (ROOT / "outputs" / "tables" / "table4_validation.md",
                "Table 4. Gold-level distribution of the validation sets."),
    "Table 5": (ROOT / "outputs" / "tables" / "table5_audit_strata.md",
                "Table 5. DDInter audit strata and disagreement composition (92 cases)."),
    "Table 6": (ROOT / "outputs" / "tables" / "table6_expert_cases.md",
                "Table 6. Expert assessment: per-case ratings (gold, system, expert 1, expert 2)."),
}


def load_legends():
    text = (ROOT / "outputs" / "paper" / "figure_legends.md").read_text(encoding="utf-8")
    blocks = re.split(r"\*\*Figure (\d+)\.", text)
    legends = {}
    for i in range(1, len(blocks), 2):
        num = int(blocks[i])
        body = blocks[i + 1].split("\n\n")[0].strip()
        # 源文件写作 "**Figure 1. …**"，按 "**Figure N." 切分后首部标记已被吃掉，
        # 但结尾的 ** 会留在 caption 里（PDF 上显示为 "…system.**"）。
        body = re.sub(r"\*\*\s*$", "", body).strip()
        legends[f"Figure {num}"] = body
    return legends


LEGENDS = load_legends()


def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)


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


def strip_md_inline(s):
    """去掉单元格里的 markdown 标记。

    pandoc 不处理 docx 表格单元格文本，若不剥离，"**total disagreements**" 会原样
    显示在表里。
    """
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s


def md_table_to_docx(doc, md_path):
    """构造 markdown 中的全部表格，按顺序返回它们的 XML 元素。

    返回列表而非单张表：调用方用 addprevious 把元素搬到文末图表区，若只返回首张，
    同一文件里的后续表格会留在文档末尾。
    """
    out = []
    for gi, rows in enumerate(parse_md_tables(md_path)):
        if gi:                                # 同一文件内的后续表格另起一张
            out.append(doc.add_paragraph()._p)
        n_rows, n_cols = len(rows), max(len(r) for r in rows)
        table = doc.add_table(rows=n_rows, cols=n_cols)
        set_table_borders(table)
        for i, r in enumerate(rows):
            for j in range(n_cols):
                cell = table.cell(i, j)
                cell.text = strip_md_inline(r[j]) if j < len(r) else ""
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(9)
                        if i == 0:
                            run.bold = True
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


def make_caption(doc, text, size=11, center=False):
    """图注/表注：标签（Figure N./Table N.）加粗，正文常规。"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    for run in p.runs:
        run.font.name = "Times New Roman"
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


def build_docx(out_path=None, marked_keys=None):
    """生成 docx。

    out_path     输出路径，默认为 outputs/deliverables/manuscript.docx
    marked_keys  非空时，段落文本匹配其中任一条的整段标红（用于标红修订版）
    """
    pandoc = r"C:\Users\Administrator\AppData\Local\Pandoc\pandoc.exe"
    src_md = ROOT / "outputs" / "paper" / "manuscript.en.md"
    author_paras = []      # 构建时注入的作者块，标红时需单独处理
    tmpdir = tempfile.TemporaryDirectory()
    tmp = Path(tmpdir.name) / "manuscript_raw.docx"
    subprocess.run([pandoc, str(src_md), "-o", str(tmp), "--standalone"], check=True)
    doc = Document(tmp)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
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
    if abstract_idx is not None:
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

    # 文末集中插入：References 前，先表格（表注+表）后图片（图+图注）
    refs_idx = next((i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "References"), None)
    anchor = doc.paragraphs[refs_idx]._p if refs_idx else doc.paragraphs[-1]._p
    # 目标顺序：Table 1..6（表注+表）→ Figure 1..5（图+图注）
    # addprevious 会倒序，所以先处理图片（Figure 5->1），再表格（Table 6->1）。
    for key in ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6"]:
        md_path, caption_text = TABLES[key]
        cap = make_caption(doc, caption_text)
        anchor.addprevious(cap._p)            # 先表注，再依序放该文件内的所有表格
        for el in md_table_to_docx(doc, md_path):
            anchor.addprevious(el)
        note = md_table_note(md_path)
        if note:
            anchor.addprevious(make_para(doc, strip_md_inline(note), size=9)._p)
    for key in ["Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 5"]:
        img_p = doc.add_paragraph()
        run = img_p.add_run()
        run.add_picture(str(FIGURES[key]), width=Inches(6.8))
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = make_caption(doc, f"{key}. {LEGENDS.get(key, '')}")
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

    out = Path(out_path) if out_path else (SUBM / "manuscript.docx")
    doc.save(out)
    tmpdir.cleanup()
    print(f"saved: {out} ({out.stat().st_size / 1024:.0f} KB)")


def main():
    build_docx()


if __name__ == "__main__":
    main()
