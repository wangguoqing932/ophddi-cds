# -*- coding: utf-8 -*-
"""redline.py — word-level redline for the marked-changes docx.

Only text that differs from the submitted (HEAD) manuscript is coloured red;
unchanged words, paragraphs and headings stay black. The matching is
paragraph-level (best match against the old text), then word-level inside the
matched paragraph.
"""
from __future__ import annotations

import difflib
import re

from docx.shared import RGBColor

RED = RGBColor(0xC0, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)


def norm(s: str) -> str:
    s = re.sub(r"^\s*#+\s*", "", s)
    s = re.sub(r"\*\*|\*|`", "", s)
    s = re.sub(r"^\s*[-•]\s+", "", s)
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def strip_md(s: str) -> str:
    s = re.sub(r"^\s*#+\s*", "", s)
    s = re.sub(r"\*\*|\*|`", "", s)
    s = re.sub(r"^\s*[-•]\s+", "", s)
    return s


def norm_token(t: str) -> str:
    return (t.replace("\u201c", '"').replace("\u201d", '"')
             .replace("\u2018", "'").replace("\u2019", "'")
             .replace("\u2013", "-").replace("\u2014", "-"))


def word_diff(old_raw: str, new_raw: str) -> list[tuple[str, bool]]:
    """Return [(text, is_red)] covering new_raw; equal words are black."""
    old_t = re.findall(r"\S+\s*", strip_md(old_raw))
    new_t = re.findall(r"\S+\s*", new_raw)
    a = [norm_token(t) for t in old_t]
    b = [norm_token(t) for t in new_t]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    segs: list[tuple[str, bool]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            segs.append(("".join(new_t[j1:j2]), False))
        elif tag in ("insert", "replace"):
            segs.append(("".join(new_t[j1:j2]), True))
    # merge adjacent runs of the same colour
    out: list[tuple[str, bool]] = []
    for text, red in segs:
        if not text:
            continue
        if out and out[-1][1] == red:
            out[-1] = (out[-1][0] + text, red)
        else:
            out.append((text, red))
    # a single unchanged word trapped between two changed runs reads as a
    # redline artefact; absorb it into the surrounding change
    for i in range(1, len(out) - 1):
        text, red = out[i]
        if not red and out[i - 1][1] and out[i + 1][1] and len(text.split()) <= 1:
            out[i] = (text, True)
    merged: list[tuple[str, bool]] = []
    for text, red in out:
        if merged and merged[-1][1] == red:
            merged[-1] = (merged[-1][0] + text, red)
        else:
            merged.append((text, red))
    return merged


def _bold_ranges(p) -> list[tuple[int, int]]:
    ranges, pos = [], 0
    for r in p.runs:
        if r.bold:
            ranges.append((pos, pos + len(r.text)))
        pos += len(r.text)
    return ranges


def _overlaps(a: int, b: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a < e and b > s for s, e in ranges)


def apply_redline(doc, old_blocks: list[str], threshold: float = 0.55) -> None:
    """Colour only inserted/replaced words red, paragraph by paragraph."""
    old_norms = [norm(b) for b in old_blocks if norm(b)]
    exact = set(old_norms)
    for p in doc.paragraphs:
        raw = p.text
        key = norm(raw)
        if not key or key in exact:
            continue
        best, best_ratio = None, 0.0
        for ob in old_norms:
            # cheap length guard, then ratio
            if min(len(ob), len(key)) / max(len(ob), len(key)) < 0.45:
                continue
            ratio = difflib.SequenceMatcher(None, ob, key, autojunk=False).ratio()
            if ratio > best_ratio:
                best, best_ratio = ob, ratio
        if best_ratio < threshold or best is None:
            segs = [(raw, True)]
        else:
            segs = word_diff(best, raw)
        if not segs:
            continue
        size = p.runs[0].font.size if p.runs and p.runs[0].font.size else None
        bold = _bold_ranges(p)
        is_heading = p.style.name.startswith("Heading")
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        pos = 0
        for text, red in segs:
            if not text:
                continue
            run = p.add_run(text)
            run.font.name = "Times New Roman"
            if size is not None:
                run.font.size = size
            run.bold = True if is_heading else _overlaps(pos, pos + len(text), bold)
            run.font.color.rgb = RED if red else BLACK
            pos += len(text)


def mark_runs_red(paragraph) -> None:
    for run in paragraph.runs:
        run.font.color.rgb = RED
