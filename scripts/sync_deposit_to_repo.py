# -*- coding: utf-8 -*-
"""sync_deposit_to_repo.py — 把完整 deposit 同步进公开仓库，保留代码布局。

结构（在现有代码布局基础上增量添加数据与文稿目录）：

    src/ configs/ scripts/ tests/ app/      代码（含修复后的 prompts/naive_rag）
    data/seed curation mock raw             既有：注册表、策展、mock、引用缓存
    data/gold predictions expert_review     新增：四套 gold、9,600 预测、专家评分
    data/ddinter evidence registry          新增：DDInter 表、证据库、逐药分级表
    manuscript/ figures/ tables/            新增：手稿、图、表
    supplementary/ audits/                  新增：补充材料、审计

用法: python scripts/sync_deposit_to_repo.py <deposit_dir> <repo_dir>
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

# deposit 相对路径 -> 仓库相对路径
MAP = [
    ("01_manuscript/manuscript.docx", "manuscript/manuscript.docx"),
    ("01_manuscript/manuscript.pdf", "manuscript/manuscript.pdf"),
    ("01_manuscript/manuscript.md", "manuscript/manuscript.md"),
    ("01_manuscript/manuscript_round2_submitted.md",
     "manuscript/manuscript_round2_submitted.md"),
    ("01_manuscript/manuscript_marked_changes.docx",
     "manuscript/manuscript_marked_changes.docx"),
    ("01_manuscript/manuscript_marked_changes.pdf",
     "manuscript/manuscript_marked_changes.pdf"),
    ("01_manuscript/cover_letter.docx", "manuscript/cover_letter.docx"),
    ("01_manuscript/cover_letter.md", "manuscript/cover_letter.md"),
    ("01_manuscript/response_to_reviewers_round1.pdf", "manuscript/response_to_reviewers_round1.pdf"),
    ("01_manuscript/response_to_reviewers_round1.md", "manuscript/response_to_reviewers_round1.md"),
    ("01_manuscript/response_to_reviewers_round2.pdf", "manuscript/response_to_reviewers_round2.pdf"),
    ("01_manuscript/response_to_reviewers_round2.md", "manuscript/response_to_reviewers_round2.md"),
    ("01_manuscript/response_to_reviewers_round3.pdf", "manuscript/response_to_reviewers_round3.pdf"),
    ("01_manuscript/response_to_reviewers_round3.md", "manuscript/response_to_reviewers_round3.md"),
    ("02_figures", "figures"),
    ("02_figures/figure_legends.md", "figures/figure_legends.md"),
    ("03_tables", "tables"),
    ("04_supplementary", "supplementary"),
    ("05_data/gold", "data/gold"),
    ("05_data/predictions", "data/predictions"),
    # 审计集设计文件（复算 0.370 与分层所需）
    ("05_data/gold/audit_set_design.json", "data/gold/audit_set_design.json"),
    ("05_data/gold/l1_test_process_audit.md", "data/gold/l1_test_process_audit.md"),
    ("05_data/expert_review", "data/expert_review"),
    ("05_data/ddinter", "data/ddinter"),
    ("05_data/registry", "data/registry"),
    # 引擎（kg_layer.py）读的是 data/seed/，不是 data/registry/。两者都放，
    # 否则修正过的吸收分级只到达 data/registry，实跑仍用旧表。
    ("05_data/registry/entities_a.csv", "data/seed/entities_a.csv"),
    ("05_data/registry/entities_b.csv", "data/seed/entities_b.csv"),
    ("05_data/evidence/evidence_chunks.jsonl", "data/evidence/evidence_chunks.jsonl"),
    ("05_data/evidence/interactions_gold.jsonl", "data/evidence/interactions_gold.jsonl"),
    ("05_data/evidence/interactions_layer1_literature.jsonl",
     "data/evidence/interactions_layer1_literature.jsonl"),
    ("05_data/evidence/citation_verification_report.json",
     "data/evidence/citation_verification_report.json"),
    ("07_audits", "audits"),
    # 逐例 provenance 与重导 gold（审稿人 round-4：case-level provenance）
    ("07_audits/recomputed/l1_gold_provenance.csv",
     "data/gold/l1_gold_provenance.csv"),
    ("07_audits/recomputed/audit_gold_rederived.json",
     "data/gold/audit_gold_rederived.json"),
]

# 代码文件：以项目为准覆盖仓库副本
# 原则：凡是审稿人/读者会拿去复现的东西，必须逐字同步。此前只列了 prompts.yaml，
# 导致 configs/class_matrix.yaml 停留在旧版（含畸形单元格），仓库里的配置与手稿
# 描述不符。配置文件一律全量同步，不要挑着列。
CODE = [
    ("configs/rules.yaml", "configs/rules.yaml"),
    ("configs/class_matrix.yaml", "configs/class_matrix.yaml"),
    ("configs/drug_classes.yaml", "configs/drug_classes.yaml"),
    ("configs/flag_catalog.yaml", "configs/flag_catalog.yaml"),
    ("configs/prompts.yaml", "configs/prompts.yaml"),
    ("configs/settings.example.yaml", "configs/settings.example.yaml"),
    ("src/ophthalmic_ddi_cds_agent/naive_rag.py",
     "src/ophthalmic_ddi_cds_agent/naive_rag.py"),
    ("src/ophthalmic_ddi_cds_agent/kg_layer.py",
     "src/ophthalmic_ddi_cds_agent/kg_layer.py"),
    ("src/ophthalmic_ddi_cds_agent/embeddings.py",
     "src/ophthalmic_ddi_cds_agent/embeddings.py"),
    ("scripts/run_baselines.py", "scripts/run_baselines.py"),
    ("scripts/run_multiseed_per_dataset.py", "scripts/run_multiseed_per_dataset.py"),
    ("scripts/materialize_baseline_predictions.py", "scripts/materialize_baseline_predictions.py"),
    ("scripts/path_attribution_audit.py", "scripts/path_attribution_audit.py"),
    ("scripts/audit_ddinter_disagreement.py", "scripts/audit_ddinter_disagreement.py"),
    ("scripts/tier_reassignment_scenarios.py", "scripts/tier_reassignment_scenarios.py"),
    ("scripts/demo_pipeline.py", "scripts/demo_pipeline.py"),
    ("scripts/evaluate.py", "scripts/evaluate.py"),
    ("scripts/generate_cases.py", "scripts/generate_cases.py"),
    ("scripts/verify_rule_citations.py", "scripts/verify_rule_citations.py"),
    # 推理模型重跑与指标重建：手稿 §3.6/Table 3/Abstract 的复现入口。
    # 此前这些脚本只存在于工作副本，审稿人指出"两个被点名的脚本不在任何提交中"。
    ("scripts/rerun_glm53_baselines.py", "scripts/rerun_glm53_baselines.py"),
    ("scripts/rerun_lightrag_flurbiprofen.py", "scripts/rerun_lightrag_flurbiprofen.py"),
    ("scripts/rebuild_metrics_json.py", "scripts/rebuild_metrics_json.py"),
    ("scripts/probe_glm53.py", "scripts/probe_glm53.py"),
    ("scripts/sync_deposited_predictions.py", "scripts/sync_deposited_predictions.py"),
    # 统计实现：手稿报告的全部检验由这个模块产出
    ("scripts/stats_tests.py", "scripts/stats_tests.py"),
    # 复算入口与专项审计（回应审稿人 3、5、6）
    ("scripts/recompute_all_reported_numbers.py", "scripts/recompute_all_reported_numbers.py"),
    ("scripts/expert_review_analysis.py", "scripts/expert_review_analysis.py"),
    ("scripts/naive_rag_leakage_audit.py", "scripts/naive_rag_leakage_audit.py"),
    # 提交前一致性审计与门控实验（审稿人 5、9 的复现入口）
    ("scripts/audit_manuscript.py", "scripts/audit_manuscript.py"),
    ("scripts/rule_gating_experiment.py", "scripts/rule_gating_experiment.py"),
    # 公共路径解析：所有复现脚本在两种布局下都能取到数据
    ("scripts/deposit_paths.py", "scripts/deposit_paths.py"),
    # 依赖声明：缺 rank-bm25 / scipy 时 naive_rag 与统计脚本无法运行
    ("requirements.txt", "requirements.txt"),
    ("RELEASE_NOTES.md", "RELEASE_NOTES.md"),
    ("pyproject.toml", "pyproject.toml"),
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
    ("MANIFEST.sha256", "MANIFEST.sha256"),
    # 金标准重导脚本（§2.3/§3.5 双口径的复现入口）
    ("scripts/rederive_audit_gold.py", "scripts/rederive_audit_gold.py"),
    # 图 1/图 3 生成脚本（matplotlib，非 AI 图像）
    ("scripts/draw_figure1.py", "scripts/draw_figure1.py"),
    ("scripts/draw_figure3.py", "scripts/draw_figure3.py"),
    # 补充材料与交付物构建链
    ("scripts/build_supplementary.py", "scripts/build_supplementary.py"),
    ("scripts/export_deliverables.py", "scripts/export_deliverables.py"),
    ("scripts/finalize_docx2.py", "scripts/finalize_docx2.py"),
    ("scripts/build_marked_docx.py", "scripts/build_marked_docx.py"),
    ("scripts/build_full_deposit.py", "scripts/build_full_deposit.py"),
    ("scripts/sync_deposit_to_repo.py", "scripts/sync_deposit_to_repo.py"),
    ("scripts/assemble_submission_pkg.py", "scripts/assemble_submission_pkg.py"),
    # 专家分析脚本（round-4 修正版）
]


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except PermissionError:
            if _same(dst, src):
                print(f"    （目标被占用但内容一致，跳过）{dst.name}")
                return 1
            raise
        return 1
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            out = dst / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(p, out)
            except PermissionError:
                # Windows 上被 PDF 阅读器等占用的文件无法覆盖；内容一致时跳过即可
                if _same(out, p):
                    n += 1
                    continue
                raise
            n += 1
    return n


def _same(a: Path, b: Path) -> bool:
    import hashlib

    def h(p: Path) -> str:
        d = hashlib.sha256()
        d.update(p.read_bytes())
        return d.hexdigest()

    try:
        return a.exists() and h(a) == h(b)
    except OSError:
        return False


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    deposit, repo = Path(sys.argv[1]), Path(sys.argv[2])
    src_root = Path(__file__).resolve().parents[1]

    total = 0
    for rel_src, rel_dst in MAP:
        s, d = deposit / rel_src, repo / rel_dst
        if not s.exists():
            print(f"  跳过（不存在）: {rel_src}")
            continue
        n = copy_tree(s, d)
        total += n
        print(f"  {rel_src:44s} -> {rel_dst:28s} ({n})")

    print("\n代码文件（以项目版本覆盖）：")
    for rel_src, rel_dst in CODE:
        s, d = src_root / rel_src, repo / rel_dst
        if not s.exists():
            print(f"  跳过（不存在）: {rel_src}")
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        print(f"  {rel_src:44s} -> {rel_dst}")

    print(f"\n共复制 {total} 个数据/文稿文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
