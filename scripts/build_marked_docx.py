# -*- coding: utf-8 -*-
"""build_marked_docx.py — 生成"改动标红"版手稿（投稿系统 related file 用）。

基线：round-1 提交版（git 17a09a6 的 outputs/paper/manuscript.en.md）。
做法：逐段 diff 找出改动过的段落，复用 finalize_docx2.build_docx() 生成完整
docx（含图表、行号、页码、双倍行距），再把对应段落整体标红。

BMC 要求正文用 clean 版（manuscript.docx），标红版单独作为 related file 上传。

用法:
    python scripts/build_marked_docx.py [基线git引用] [输出路径]
"""
from __future__ import annotations

import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
MD = ROOT / "outputs" / "paper" / "manuscript.en.md"
OUT_DEFAULT = ROOT / "outputs" / "deliverables" / "manuscript_marked_changes.docx"


def git_show(ref: str) -> str:
    out = subprocess.run(
        ["git", "show", f"{ref}:outputs/paper/manuscript.en.md"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
    return out.stdout


def normalize(s: str) -> str:
    """去掉 markdown 标记与空白，便于在 docx 文本中定位。

    必须去掉行首的 #：pandoc 把 "### x" 渲染为 Heading，段落文本里不含 #，
    否则标题永远匹配不上。
    必须统一引号：pandoc 会把直引号 " 转成弯引号 “ ”，否则含引号的段落匹配不上。
    """
    s = re.sub(r"^\s*#+\s*", "", s)      # 行首标题标记
    s = re.sub(r"\*\*|\*|`", "", s)      # 强调与代码标记
    s = re.sub(r"^\s*[-•]\s+", "", s)    # 列表符号
    s = s.replace("\u201c", '"').replace("\u201d", '"')   # 弯引号 -> 直引号
    s = s.replace("\u2018", "'").replace("\u2019", "'")   # 弯单引号
    s = s.replace("\u2013", "-").replace("\u2014", "-")   # en/em dash
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm_docx(s: str) -> str:
    """对 docx 中读到的文本做同样的规范化，保证两侧可比。"""
    return normalize(s)


def changed_paragraphs(old: str, new: str) -> list[str]:
    """返回新版中被修改或新增的段落（规范化后）。"""
    ol = [l.strip() for l in old.split("\n")]
    nl = [l.strip() for l in new.split("\n")]
    sm = difflib.SequenceMatcher(None, ol, nl, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert"):
            for line in nl[j1:j2]:
                if line:
                    out.append(normalize(line))
    return out


def row_cells(line: str) -> list[str]:
    """把 "| a | b |" 拆成单元格列表。"""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_sep(line: str) -> bool:
    """markdown 表格的分隔行 |---|---|。"""
    cells = row_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def row_label(cells: list[str]) -> tuple[str, ...]:
    """行的标签键：去掉纯数值与 "10-token"/"3000-token" 这类设置标签。

    表3 在本轮新增了 setting 列，若按整行文本比对，所有行都会因列位移而判为改动。
    这里用标签（如 dataset_id + method）定位同一行，只标注数值确实变了的行。
    """
    return tuple(c.lower() for c in cells
                 if not re.fullmatch(r"[-+0-9.,%() ]+", c)
                 and not re.fullmatch(r"\d+-token", c, re.I))


_NUM = re.compile(r"[-+]?\d*\.?\d+")


def num_payload(cells: list[str]) -> tuple[str, ...]:
    """抽出"数值单元格"里的数字，用于判断一行的数值是否变化。

    只取整格都是数字/括号的单元格：像 blind_l1、10-token 这类标识符里也含数字，
    若按整行提数字，本轮给表3 新增 setting 列会让每行都凭空多出一个 "10"，
    全部误判为改动。
    """
    out = []
    for c in cells:
        if not re.fullmatch(r"[-+0-9.,%()\s]+", c):
            continue
        for m in _NUM.findall(c):
            try:
                out.append(f"{float(m):g}")
            except ValueError:
                pass
    return tuple(out)


def changed_table_rows(ref: str) -> list[str]:
    """返回规范表格中被改动的行（当前版本），供标红使用。

    正文里的六张表由 finalize_docx2 从 outputs/tables/table*.md 注入，不出现在
    manuscript.en.md 中，所以段落 diff 看不到它们，必须单独比对。
    """
    out: list[str] = []
    for p in sorted((ROOT / "outputs" / "tables").glob("table*.md")):
        cur = [l for l in p.read_text(encoding="utf-8").splitlines()
               if l.strip().startswith("|") and not is_sep(l)]
        try:
            old_txt = subprocess.run(
                ["git", "show", f"{ref}:outputs/tables/{p.name}"], cwd=ROOT,
                capture_output=True, text=True, encoding="utf-8", check=True).stdout
        except subprocess.CalledProcessError:
            old_txt = ""
        old = [l for l in old_txt.splitlines()
               if l.strip().startswith("|") and not is_sep(l)]
        if not old:                              # 新增的表：整表标红
            out += [normalize(l) for l in cur]
            continue
        old_by_label: dict[tuple, list[list[str]]] = {}
        for l in old:
            old_by_label.setdefault(row_label(row_cells(l)), []).append(row_cells(l))
        n_old = len(row_cells(old[0]))
        for i, l in enumerate(cur):
            cells = row_cells(l)
            if i == 0 and len(cells) != n_old:   # 表头列数变化 → 表头标红
                out.append(normalize(l))
                continue
            pool = old_by_label.get(row_label(cells))
            if not pool:                         # 新增行
                out.append(normalize(l))
                continue
            # 只比数值载荷：本轮给表3 加了 setting 列，若按整行比对，列位移会让
            # 所有行都判为改动。同一标签下只要有一行的数值与当前行一致即视为未改动。
            vals = num_payload(cells)
            if not any(num_payload(cand) == vals for cand in pool):
                out.append(normalize(l))
    return out


def table_row_keys(keys: list[str]) -> list[tuple[str, ...]]:
    """把 markdown 表格行（"| a | b |"）转成单元格元组，便于与 docx 表格行比对。

    docx 中 markdown 表格是真表格对象，行文本不含 "|"，因此段落匹配永远命不中。
    这里额外产出一组"单元格元组"键，由调用方按行比对。
    """
    rows = []
    for k in keys:
        s = k.strip()
        if s.startswith("|") and s.endswith("|") and s.count("|") >= 3:
            cells = tuple(c.strip() for c in s.strip("|").split("|"))
            if not all(set(c) <= set("-: ") for c in cells):   # 跳过 |---|---| 分隔行
                rows.append(cells)
    return rows


def main() -> int:
    # 默认基线 = 上一轮"已提交给期刊"的手稿版本（tag round2-submitted，提交 418d7a2）。
    # 用 round-1 作基线会把三轮改动混在一起标红，审稿人无法分辨本轮改了什么。
    ref = sys.argv[1] if len(sys.argv) > 1 else "round2-submitted"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT

    # 基线选择：显式传入 git 引用（如 HEAD = Frontiers 已投稿版）时必须用 git 基线；
    # 只有默认的 round2-submitted 才优先用随仓库发布的基线文件（审稿人只能看到
    # 文件，不共享作者本地的 git 历史）。
    baseline_md = None
    if ref == "round2-submitted":
        baseline_md = next(
            (p for p in (ROOT / "outputs" / "deliverables" / "manuscript_round2_submitted.md",
                         ROOT / "manuscript" / "manuscript_round2_submitted.md")
             if p.exists()), None)
    if baseline_md is not None:
        old = baseline_md.read_text(encoding="utf-8")
        print(f"基线：{baseline_md.name}（随仓库发布的 round-2 提交版）")
    else:
        old = git_show(ref)
    new = MD.read_text(encoding="utf-8")
    keys = [normalize(t) for t in changed_paragraphs(old, new)]
    n_para = len(keys)
    # 六张规范表由 outputs/tables/*.md 注入，不在 manuscript.en.md 里，段落 diff 看不到。
    tkeys = changed_table_rows(ref)
    keys += tkeys
    print(f"基线 {ref}：改动段落 {n_para} 处，改动表格行 {len(tkeys)} 处")

    from finalize_docx2 import build_docx  # 复用正式版排版流程
    build_docx(out_path=out_path, marked_keys=keys)

    # ── 校验 ──
    from docx import Document
    d = Document(out_path)
    red = []
    for p in d.paragraphs:
        cols = [str(r.font.color.rgb) for r in p.runs
                if r.text.strip() and r.font.color and r.font.color.rgb]
        if cols and all(c == "C00000" for c in cols):
            red.append(norm_docx(p.text))
    # 表格行同样可能被标红（markdown 表格在 docx 中是表格对象，段落遍历看不到）
    tk = table_row_keys(keys)
    for tbl in d.tables:
        for row in tbl.rows:
            cells = tuple(c.text.strip().lower() for c in row.cells)
            if not any(len(rk) == len(cells) for rk in tk):
                continue
            cols = [str(r.font.color.rgb) for cell in row.cells
                    for p in cell.paragraphs for r in p.runs
                    if r.text.strip() and r.font.color and r.font.color.rgb]
            if cols and all(c == "C00000" for c in cols):
                red.append(" ".join(cells))
                continue
            # 未标红则记入 missing 供诊断
            red.append("__MISSING__ " + " ".join(cells))
    # markdown 表格行在 docx 里是表格对象，行文本不含 "|"，只能走上面的单元格元组
    # 比对路径，因此这里不参与段落文本匹配（否则永远报"未标红"）。
    para_keys = [k for k in keys if k and not k.startswith("|")]
    print(f"校验：标红 {len(red)} 处，目标 {len(keys)} 处（段落 {len(para_keys)}）")
    missing = [k for k in para_keys
               if not any(r.startswith(k[:60]) or k[:60] in r for r in red)]
    if missing:
        print("未标红:")
        for m in missing:
            print("  -", m[:100])
    else:
        print("全部改动段落均已标红")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
