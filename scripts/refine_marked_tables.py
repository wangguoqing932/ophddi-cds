# -*- coding: utf-8 -*-
"""refine_marked_tables.py — reduce over-marking in the redline DOCX files.

The generic redline builders mark a whole table red when any row changes, so
Table 2 and Supplementary Tables S5/S6 become fully red even though only one
rule or a handful of tiers changed. This pass recolours unchanged rows black
and leaves only substantively changed rows red. It is presentation-only and
does not alter text.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from docx import Document
from docx.shared import RGBColor

ROOT = Path(__file__).resolve().parents[1]
RED = {"C00000", "FF0000"}


def set_row_color(row, red: bool) -> None:
    color = RGBColor(0xC0, 0, 0) if red else RGBColor(0, 0, 0)
    for cell in row.cells:
        for para in cell.paragraphs:
            if not para.runs:
                para.add_run("")
            for run in para.runs:
                run.font.color.rgb = color


def refine_rule_tables(path: Path, table_indices: list[int], keep_rule: str) -> int:
    doc = Document(path)
    changed = 0
    for idx in table_indices:
        table = doc.tables[idx]
        for row in table.rows[1:]:
            first = row.cells[0].text.strip().lower()
            is_changed = keep_rule in first
            set_row_color(row, is_changed)
            changed += int(is_changed)
    doc.save(path)
    return changed


def old_s5_tiers() -> dict[str, str]:
    old = subprocess.run(
        ["git", "show", "HEAD:outputs/deliverables/supplementary_files/Supplementary_Material.md"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    tiers = {}
    for line in old.splitlines():
        if line.startswith("| topical_ophthalmic_"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4:
                tiers[cells[1].lower()] = cells[3].replace("systemic_absorption_", "").replace("minimal_systemic_absorption", "minimal").replace("very_low", "very low")
    return tiers


def refine_s5(path: Path, table_index: int) -> int:
    old = old_s5_tiers()
    doc = Document(path)
    table = doc.tables[table_index]
    changed = 0
    for row in table.rows[1:]:
        cells = [c.text.strip() for c in row.cells]
        if len(cells) < 4:
            continue
        agent, tier = cells[1].lower(), cells[3]
        is_changed = old.get(agent) != tier
        set_row_color(row, is_changed)
        changed += int(is_changed)
    doc.save(path)
    return changed


def main() -> None:
    ms = ROOT / "outputs/deliverables/manuscript_marked_changes.docx"
    sup = ROOT / "outputs/deliverables/supplementary_files/Supplementary_Material_marked_changes.docx"
    n_ms = refine_rule_tables(ms, [1, 2], "dexamethasone")
    n_sup_rules = refine_rule_tables(sup, [9, 10], "dexamethasone")
    n_s5 = refine_s5(sup, 7)
    print(f"manuscript rule rows red: {n_ms}; supplement rule rows red: {n_sup_rules}; S5 tier rows red: {n_s5}")


if __name__ == "__main__":
    main()
