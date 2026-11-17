# -*- coding: utf-8 -*-
"""build_supplementary_marked.py — word-level redline for the supplementary material.

Body paragraphs: only inserted/replaced words are red.
Tables: a row is red when its concatenated cell text is not found in the submitted
supplement; unchanged rows stay black.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.shared import RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from redline import apply_redline, norm  # noqa: E402

RED = RGBColor(0xC0, 0x00, 0x00)


def old_text() -> str:
    return subprocess.run(
        ["git", "show", "HEAD:outputs/deliverables/supplementary_files/Supplementary_Material.md"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def blocks(md: str) -> list[str]:
    out, cur = [], []
    for line in md.splitlines():
        if not line.strip():
            if cur:
                out.append("\n".join(cur)); cur = []
        elif line.strip().startswith("|") or line.strip().startswith("---"):
            continue
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [b for b in out if b.strip()]


def main() -> None:
    src = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material.docx"
    dst = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material_marked_changes.docx"
    shutil.copyfile(src, dst)
    old = old_text()
    doc = Document(dst)
    apply_redline(doc, blocks(old))

    # table rows that do not appear in the submitted supplement are changed/new
    old_flat = norm(re.sub(r"\|", " ", old))
    marked_rows = 0
    for table in doc.tables:
        for row in table.rows:
            row_text = norm(" ".join(cell.text for cell in row.cells))
            if not row_text:
                continue
            if row_text not in old_flat:
                marked_rows += 1
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if not para.runs:
                            para.add_run("")
                        for run in para.runs:
                            run.font.color.rgb = RED
    doc.save(dst)
    subprocess.run([sys.executable, str(ROOT / "scripts/docx_to_pdf.py"), str(dst),
                    str(dst.with_suffix(".pdf"))], check=False)
    print(f"supplementary redline -> {dst}; changed table rows: {marked_rows}")


if __name__ == "__main__":
    main()
