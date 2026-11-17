# -*- coding: utf-8 -*-
"""export_frontiers_fields.py — refresh the plain-text fields used in the Frontiers form."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs/paper/manuscript.en.md"
OUT = ROOT / "outputs/deliverables/frontiers"


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def extract(pattern: str) -> str:
    m = re.search(pattern, SRC.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"missing block: {pattern}")
    return m.group(1).strip()


def plain(text: str) -> str:
    text = strip_md(text)
    return re.sub(r"\s*\[\d+(?:[-,]\d+)*\]", "", text)


def main() -> None:
    source = SRC.read_text(encoding="utf-8")
    abstract = extract(r"## Abstract\s*\n(.*?)\n\n## ")
    abstract = strip_md(abstract)

    methods = extract(r"### 2\.1 .*?\n(.*?)\n\n## 3\. Results")
    # drop subsection headings but keep the prose
    methods = re.sub(r"^### 2\.\d .*$", "", methods, flags=re.M)
    methods = re.sub(r"\n{3,}", "\n\n", methods).strip()
    methods_full = strip_md(methods)
    methods_plain = plain(methods)

    (OUT / "_abstract_plain.txt").write_text(abstract + "\n", encoding="utf-8")
    (OUT / "_methods_full.txt").write_text(methods_full + "\n", encoding="utf-8")
    (OUT / "_methods_plain.txt").write_text(methods_plain + "\n", encoding="utf-8")

    fields_path = OUT / "_form_fields.json"
    fields = json.loads(fields_path.read_text(encoding="utf-8"))
    fields["abstract"] = abstract
    fields_path.write_text(json.dumps(fields, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("abstract words", len(abstract.split()))
    print("methods words", len(methods_full.split()))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
