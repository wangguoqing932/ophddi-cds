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
    """
    s = re.sub(r"^\s*#+\s*", "", s)      # 行首标题标记
    s = re.sub(r"\*\*|\*|`", "", s)      # 强调与代码标记
    s = re.sub(r"^\s*[-•]\s+", "", s)    # 列表符号
    s = re.sub(r"\s+", " ", s)
    return s.strip()


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


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "17a09a6"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT

    old = git_show(ref)
    new = MD.read_text(encoding="utf-8")
    keys = [normalize(t) for t in changed_paragraphs(old, new)]
    print(f"基线 {ref}：检出 {len(keys)} 处改动段落")

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
            red.append(p.text.strip())
    print(f"校验：标红 {len(red)}/{len(keys)} 处")
    missing = [k for k in keys if not any(r.startswith(k[:60]) or k[:60] in r for r in red)]
    if missing:
        print("未标红:")
        for m in missing:
            print("  -", m[:100])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
