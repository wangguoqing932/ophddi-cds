# -*- coding: utf-8 -*-
"""build_redline_docx.py — build the marked-changes docx with word-level redlining."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from finalize_docx2 import build_docx  # noqa: E402


def git_show(path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout


def blocks(md: str) -> list[str]:
    out, cur = [], []
    for line in md.splitlines():
        if not line.strip():
            if cur:
                out.append("\n".join(cur))
                cur = []
        elif line.strip().startswith("|") or line.strip().startswith("---"):
            continue
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [b for b in out if b.strip()]


def changed_table_keys() -> set[str]:
    red = set()
    for key, name in [("Table 1", "table1_registry.md"), ("Table 2", "table2_rules.md"),
                      ("Table 3", "table3_performance.md"), ("Table 4", "table4_validation.md"),
                      ("Table 5", "table5_audit_strata.md"), ("Table 6", "table6_grade_definitions.md"),
                      ("Table 7", "table7_route_aware.md")]:
        path = ROOT / "outputs" / "tables" / name
        try:
            old = git_show(f"outputs/tables/{name}")
        except subprocess.CalledProcessError:
            red.add(key)
            continue
        if path.read_text(encoding="utf-8").strip() != old.strip():
            red.add(key)
    return red


def main() -> None:
    old = git_show("outputs/paper/manuscript.en.md")
    old_blocks = blocks(old)
    out = ROOT / "outputs" / "deliverables" / "manuscript_marked_changes.docx"
    build_docx(out_path=out, redline_old_blocks=old_blocks,
               red_tables=changed_table_keys(),
               red_figures={"Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 6"})
    # Table 7's explanatory note is injected from outputs/tables, so the
    # paragraph diff never sees it. It is new in this revision; mark that note.
    from docx import Document
    from docx.shared import RGBColor
    d = Document(out)
    for p in d.paragraphs:
        if p.text.strip().startswith(("Note: Restricted to the 42 L1 cases",
                                      "Note: Exact agreement: 14/30")):
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xC0, 0, 0)
    d.save(out)
    print(f"redline docx -> {out}")


if __name__ == "__main__":
    main()
