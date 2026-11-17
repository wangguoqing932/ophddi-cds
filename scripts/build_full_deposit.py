# -*- coding: utf-8 -*-
"""build_full_deposit.py — 组装完整的可复现性包（回应审稿人对 deposit 的批评）。

把原始数据、图片、表格、手稿、补充材料与代码合并到单一目录树，每份文件只出现
一次（去重），并生成带 SHA-256 的 MANIFEST.md。

用法:
    python scripts/build_full_deposit.py [输出目录]
默认输出到 <workspace>/ophddi-cds-deposit。
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT.parent / "ophddi-cds-deposit"

# 需要排除的大体积/非交付目录
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache",
                "_archive_legacy", "lightrag_index", "lightrag_index.__previous__20260729"}
EXCLUDE_SUFFIX = {".tiff", ".bak", ".pyc"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file(src: Path, dst: Path, copied: dict) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    # 去重：同一内容（哈希）只保留第一次出现的位置
    digest = sha256(src)
    if digest in copied:
        return
    # 目标已存在且内容相同则跳过：重建 deposit 时个别文件（如伦审 PDF）可能被
    # Word/阅读器占用而无法覆盖，内容一致时无需重写。
    if dst.exists() and sha256(dst) == digest:
        copied[digest] = dst
        return
    shutil.copy2(src, dst)
    copied[digest] = dst


def build_tier_table(outdir: Path) -> Path:
    """生成 per-agent 吸收分级表（含来源列）——审稿人指出补充材料中缺失此表。"""
    src = ROOT / "data" / "seed" / "entities_a.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
    tier_keys = ["systemic_absorption_high", "systemic_absorption_medium",
                 "systemic_absorption_low", "systemic_absorption_very_low",
                 "minimal_systemic_absorption", "systemic_absorption_none"]
    out = outdir / "05_data" / "registry" / "per_agent_absorption_tier.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ophthalmic_id", "primary_name", "category", "absorption_tier",
                    "ophthalmic_administration", "dosage_form", "evidence_sources",
                    "curation_status"])
        for r in rows:
            flags = [f.strip() for f in (r.get("flags") or "").split("|") if f.strip()]
            tier = next((f for f in flags if f in tier_keys), "")
            w.writerow([r.get("topical_ophthalmic_medications_id", ""),
                        r.get("primary_name", ""), r.get("category", ""),
                        tier or "(no tier flag)", r.get("ophthalmic_administration", ""),
                        r.get("dosage_form", ""), r.get("evidence_sources", ""),
                        r.get("curation_status", "")])
    return out


def main() -> int:
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    if outdir.exists():
        # 容错删除：Windows 上被 PDF 阅读器占用的文件会拒绝删除，逐项忽略
        for p in sorted(outdir.rglob("*"), key=lambda q: -len(q.parts)):
            try:
                p.unlink() if p.is_file() else p.rmdir()
            except OSError:
                pass
    outdir.mkdir(parents=True, exist_ok=True)

    copied: dict[str, Path] = {}
    n_before = 0

    def grab(rel_src: str, rel_dst: str) -> None:
        nonlocal n_before
        n_before += 1
        copy_file(ROOT / rel_src, outdir / rel_dst, copied)

    # ── 01 手稿 ──
    for f, d in [("outputs/deliverables/manuscript.docx", "01_manuscript/manuscript.docx"),
                 ("outputs/deliverables/manuscript.pdf", "01_manuscript/manuscript.pdf"),
                 ("outputs/deliverables/manuscript.md", "01_manuscript/manuscript.md"),
                 # 标红版所对比的 round-2 提交版（审稿人据此核验本轮改动）
                 ("outputs/deliverables/manuscript_round2_submitted.md",
                  "01_manuscript/manuscript_round2_submitted.md"),
                 # 改动标红版：审稿人要求逐处可见修改位置
                 ("outputs/deliverables/manuscript_marked_changes.docx",
                  "01_manuscript/manuscript_marked_changes.docx"),
                 ("outputs/deliverables/manuscript_marked_changes.pdf",
                  "01_manuscript/manuscript_marked_changes.pdf"),
                 ("outputs/deliverables/cover_letter.docx", "01_manuscript/cover_letter.docx"),
                 ("outputs/deliverables/cover_letter.md", "01_manuscript/cover_letter.md"),
                 ("outputs/submission/response_to_reviewers.pdf", "01_manuscript/response_to_reviewers_round1.pdf"),
                 ("outputs/submission/response_to_reviewers.md", "01_manuscript/response_to_reviewers_round1.md"),
                 ("outputs/submission/response_to_reviewers_round2.pdf", "01_manuscript/response_to_reviewers_round2.pdf"),
                 ("outputs/submission/response_to_reviewers_round2.md", "01_manuscript/response_to_reviewers_round2.md"),
                 ("outputs/submission/response_to_reviewers_round3.pdf", "01_manuscript/response_to_reviewers_round3.pdf"),
                 ("outputs/submission/response_to_reviewers_round3.md", "01_manuscript/response_to_reviewers_round3.md")]:
        grab(f, d)

    # ── 02 图片（含 source data）──
    for fig in ["figure1_architecture", "figure2_performance", "figure3_expert_agreement",
                "figure4_demo_case", "figure5_reasoning_trace"]:
        for ext in ("png", "pdf"):
            grab(f"outputs/figures/{fig}.{ext}", f"02_figures/{fig}.{ext}")
    for sd in sorted((ROOT / "outputs" / "figures" / "source_data").glob("*.csv")):
        grab(f"outputs/figures/source_data/{sd.name}", f"02_figures/source_data/{sd.name}")
    grab("outputs/deliverables/supplementary_files/figure_legends.md", "02_figures/figure_legends.md")

    # ── 03 表格 ──
    for tbl in sorted((ROOT / "outputs" / "tables").glob("table*.md")):
        grab(f"outputs/tables/{tbl.name}", f"03_tables/{tbl.name}")
    for extra in ["performance_matrix.csv", "performance_by_dataset.csv",
                  "dataset_summary.csv", "registry_summary.csv", "rule_list.csv",
                  # 1,933 对登记的机读结果（表5 与手稿 75.3%/352/80.5% 的来源）
                  "ddinter_disagreement_audit.json",
                  "ddinter_disagreement_cases.jsonl"]:
        if (ROOT / "outputs" / "tables" / extra).exists():
            grab(f"outputs/tables/{extra}", f"03_tables/{extra}")

    # ── 04 补充材料 ──
    grab("outputs/deliverables/supplementary_files/Supplementary_Material.docx",
         "04_supplementary/Supplementary_Material.docx")
    grab("outputs/deliverables/supplementary_files/Supplementary_Material.md",
         "04_supplementary/Supplementary_Material.md")
    grab("outputs/submission/ethics/Ethics_Approval_K202509-29.pdf",
         "04_supplementary/ethics/Ethics_Approval_K202509-29.pdf")
    grab("outputs/submission/highlights.md", "04_supplementary/highlights.md")

    # ── 05 原始数据 ──
    # 5.1 四套评估 gold（含 case-level provenance）
    for ds in ["blind_l1", "blind_v3_ddinter", "dev-ddinter", "external_validation"]:
        for f in ["cases.jsonl", "dataset.meta.json", "source_references.json"]:
            if (ROOT / "data" / "datasets" / ds / f).exists():
                grab(f"data/datasets/{ds}/{f}", f"05_data/gold/{ds}/{f}")
    # 开发门禁用到的另两套（论文中报告过）
    for ds in ["internal_validation", "external_pubmed"]:
        for f in ["cases.jsonl", "dataset.meta.json"]:
            if (ROOT / "data" / "datasets" / ds / f).exists():
                grab(f"data/datasets/{ds}/{f}", f"05_data/gold/{ds}/{f}")

    # 5.2 预测行（9,600）与指标
    for f in sorted((ROOT / "outputs" / "multiseed_per_dataset").glob("*__seed*.jsonl")):
        grab(f"outputs/multiseed_per_dataset/{f.name}", f"05_data/predictions/{f.name}")
    # 5.2a 审计集设计文件：记录每例的 DDInter 原始严重度与更正规则，
    # 是复算"对未更正 DDInter 一致率 0.370"与分层的必要输入。
    grab("outputs/blind_test/blind_set_v3_ddinter.json",
         "05_data/gold/audit_set_design.json")
    grab("outputs/blind_test/l1_test_process_audit.md",
         "05_data/gold/l1_test_process_audit.md")

    # 5.2b 推理模型重跑（审稿人 2 要求）：原始响应、解析标签、指标、运行日志
    for f in ["predictions.jsonl", "pilot_predictions.jsonl", "metrics.json",
              "metrics_majority.json", "run.log", "COMPARISON_REPORT.md"]:
        if (ROOT / "outputs" / "glm53_baselines" / f).exists():
            grab(f"outputs/glm53_baselines/{f}", f"05_data/predictions/glm53_baselines/{f}")
    # 5.2c 复算产物（全部报告数字的可复核中间结果；json + 逐例 provenance csv）
    for f in sorted((ROOT / "outputs" / "recomputed").glob("*.json")):
        grab(f"outputs/recomputed/{f.name}", f"07_audits/recomputed/{f.name}")
    for f in sorted((ROOT / "outputs" / "recomputed").glob("*.csv")):
        grab(f"outputs/recomputed/{f.name}", f"07_audits/recomputed/{f.name}")
    # 引擎/配置/gold 的 LF 归一化指纹清单（与正文 §2.7 的指纹口径一致）
    if (ROOT / "MANIFEST.sha256").exists():
        grab("MANIFEST.sha256", "MANIFEST.sha256")
    # LightRAG 索引构建记录（输入指纹、rules/evidence 哈希、文档计数）
    idx = ROOT / "data" / "evidence" / "index_manifest.json"
    if idx.exists():
        grab("data/evidence/index_manifest.json", "05_data/evidence/index_manifest.json")
    for f in ["multiseed_per_dataset_metrics.json", "REPORT.md", "run_log.txt"]:
        if (ROOT / "outputs" / "multiseed_per_dataset" / f).exists():
            grab(f"outputs/multiseed_per_dataset/{f}",
                 f"05_data/predictions/{f}")

    # 5.3 专家评分（12 例）
    for f in ["expert_review_results.json", "expert_review_results.md",
              "expert_responses_archive.json", "blind_gold_review.pdf",
              "blind_gold_review_CN.csv", "expert1_page1.png", "expert1_page2.png",
              "phase4_expert_answer_CN.csv", "phase4_expert_review.pdf"]:
        if (ROOT / "outputs" / "expert_review" / f).exists():
            grab(f"outputs/expert_review/{f}", f"05_data/expert_review/{f}")

    # 5.4 证据库
    grab("data/seed/evidence_chunks.jsonl", "05_data/evidence/evidence_chunks.jsonl")
    grab("data/seed/interactions_gold.jsonl", "05_data/evidence/interactions_gold.jsonl")
    grab("data/seed/interactions_layer1_literature.jsonl",
         "05_data/evidence/interactions_layer1_literature.jsonl")
    grab("outputs/citation_verification_report.json",
         "05_data/evidence/citation_verification_report.json")
    # 引用核验缓存（离线重放）
    for f in sorted((ROOT / "data/raw/evidence/citations").rglob("*")):
        if f.is_file():
            grab(str(f.relative_to(ROOT)),
                 f"05_data/evidence/citation_cache/{f.relative_to(ROOT / 'data/raw/evidence/citations')}")

    # 5.5 DDInter 严重度表
    for f in sorted((ROOT / "data" / "raw" / "ddinter").glob("*.csv")):
        grab(f"data/raw/ddinter/{f.name}", f"05_data/ddinter/{f.name}")

    # 5.6 注册表 + 每药分级表
    grab("data/seed/entities_a.csv", "05_data/registry/entities_a.csv")
    grab("data/seed/entities_b.csv", "05_data/registry/entities_b.csv")
    grab("data/curation/entity_a_candidates.yaml", "05_data/registry/entity_a_candidates.yaml")
    grab("data/curation/entity_b_candidates.yaml", "05_data/registry/entity_b_candidates.yaml")
    grab("data/curation/rule_citations.yaml", "05_data/registry/rule_citations.yaml")
    grab("data/curation/rule_evidence_map.yaml", "05_data/registry/rule_evidence_map.yaml")
    tier_csv = build_tier_table(outdir)
    copied[sha256(tier_csv)] = tier_csv

    # ── 06 代码 ──
    for f in sorted((ROOT / "src" / "ophthalmic_ddi_cds_agent").glob("*.py")):
        grab(f"src/ophthalmic_ddi_cds_agent/{f.name}", f"06_code/src/ophthalmic_ddi_cds_agent/{f.name}")
    for f in ["rules.yaml", "class_matrix.yaml", "drug_classes.yaml",
              "flag_catalog.yaml", "prompts.yaml", "settings.example.yaml"]:
        if (ROOT / "configs" / f).exists():
            grab(f"configs/{f}", f"06_code/configs/{f}")
    # 评估与统计相关脚本（审稿人点名要求）
    key_scripts = ["run_multiseed_per_dataset.py", "evaluate.py", "generate_cases.py",
                   "materialize_baseline_predictions.py", "run_baselines.py",
                   "run_multiseed.py", "verify_rule_citations.py", "demo_pipeline.py",
                   "assemble_submission_pkg.py", "export_deliverables.py",
                   "finalize_docx2.py", "build_docx.py", "docx_to_pdf.py",
                   # 1,933 对审计与路径归因：手稿 75.3%/80.5%/352 与 68.7%/12.2%/12.0%/7.1%
                   # 由这两个脚本直接产生，必须随仓库发布以便复核。
                   "audit_ddinter_disagreement.py", "path_attribution_audit.py",
                   "audit_manuscript.py", "rule_gating_experiment.py",
                   "deposit_paths.py",
                   "tier_reassignment_scenarios.py"]
    for f in key_scripts:
        if (ROOT / "scripts" / f).exists():
            grab(f"scripts/{f}", f"06_code/scripts/{f}")
    for f in sorted((ROOT / "tests").glob("*.py")):
        grab(f"tests/{f.name}", f"06_code/tests/{f.name}")
    for f in ["pyproject.toml", "requirements.txt", "RELEASE_NOTES.md", ".env.example"]:
        if (ROOT / f).exists():
            grab(f, f"06_code/{f}")
    # mock 数据（上一轮加的演示集）
    mock_dir = ROOT / "data" / "mock"
    if mock_dir.exists():
        for f in sorted(mock_dir.glob("*")):
            grab(f"data/mock/{f.name}", f"06_code/data/mock/{f.name}")

    # ── 07 审计（回应审稿人意见 3 与 6）──
    audit_dir = ROOT / "outputs" / "audits"
    if audit_dir.exists():
        for f in sorted(audit_dir.glob("*")):
            if f.is_file() and f.name != "lexicomp_route_aware_raw.json":
                grab(f"outputs/audits/{f.name}", f"07_audits/{f.name}")

    # ── MANIFEST ──
    files = sorted(p for p in outdir.rglob("*") if p.is_file())
    lines = [
        "# Deposit manifest",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Files: {len(files)}",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---|---|",
    ]
    for p in files:
        lines.append(f"| `{p.relative_to(outdir).as_posix()}` | {p.stat().st_size} | `{sha256(p)[:16]}` |")
    (outdir / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    total = sum(p.stat().st_size for p in files)
    print(f"assembled -> {outdir}")
    print(f"  source candidates: {n_before}, unique files written: {len(files)} "
          f"(deduplicated {n_before - len(files)})")
    print(f"  total size: {total/1024/1024:.1f} MB")
    for d in sorted(outdir.iterdir()):
        if d.is_dir():
            n = sum(1 for _ in d.rglob("*") if _.is_file())
            print(f"    {d.name}/  ({n} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
