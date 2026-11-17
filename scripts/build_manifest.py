# -*- coding: utf-8 -*-
"""build_manifest.py — 生成仓库根 MANIFEST.sha256（LF 归一化哈希）。

覆盖引擎、配置、注册表、证据库、金标准（含逐例 provenance）、索引构建记录。
哈希口径与正文 §2.7 一致：先把 CRLF 归一化为 LF 再哈希，避免 Windows/Linux
检出差异。索引构建记录中的哈希是构建时的 CRLF 值，LEN 见 REPORT.md。
"""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# (canonical repo path, project-layout source path or None)
TARGETS = [
    ("src/ophthalmic_ddi_cds_agent/kg_layer.py", None),
    ("src/ophthalmic_ddi_cds_agent/risk_rules.py", None),
    ("src/ophthalmic_ddi_cds_agent/safety_agent.py", None),
    ("src/ophthalmic_ddi_cds_agent/schemas.py", None),
    ("configs/rules.yaml", None),
    ("configs/class_matrix.yaml", None),
    ("configs/drug_classes.yaml", None),
    ("configs/flag_catalog.yaml", None),
    ("configs/prompts.yaml", None),
    ("data/seed/entities_a.csv", "data/seed/entities_a.csv"),
    ("data/seed/entities_b.csv", "data/seed/entities_b.csv"),
    ("data/seed/evidence_chunks.jsonl", "data/seed/evidence_chunks.jsonl"),
    ("data/gold/l1_gold_provenance.csv", "outputs/recomputed/l1_gold_provenance.csv"),
    ("data/gold/audit_set_design.json", "outputs/blind_test/blind_set_v3_ddinter.json"),
    ("data/gold/audit_gold_provenance.csv", "outputs/recomputed/audit_gold_provenance.csv"),
    ("data/gold/audit_gold_rederived.json", "outputs/recomputed/audit_gold_rederived.json"),
    ("data/gold/dev_ddinter_gold_provenance.csv",
     "outputs/recomputed/dev_ddinter_gold_provenance.csv"),
    ("data/gold/l1_test_process_audit.md", "outputs/blind_test/l1_test_process_audit.md"),
    ("data/evidence/index_manifest.json", "data/evidence/index_manifest.json"),
    ("data/predictions/REPORT.md", "outputs/multiseed_per_dataset/REPORT.md"),
]


def lf_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    lines = []
    for rel, src in TARGETS:
        p = ROOT / rel
        if not p.exists() and src:
            p = ROOT / src
        if not p.exists():
            print(f"  跳过（不存在）: {rel}")
            continue
        lines.append(f"{lf_hash(p)}  {rel}")
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"written MANIFEST.sha256 ({len(lines)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
