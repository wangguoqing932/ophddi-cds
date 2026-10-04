# -*- coding: utf-8 -*-
"""deposit_paths.py — 在"项目布局"与"公开仓库布局"下统一解析数据文件位置。

背景：本仓库有两种目录布局——

    项目布局（作者工作副本）        公开仓库布局（deposit 同步后）
    outputs/paper/manuscript.en.md  manuscript/manuscript.md
    outputs/blind_test/             data/gold/
    outputs/expert_review/          data/expert_review/
    outputs/multiseed_per_dataset/  data/predictions/
    outputs/recomputed/             audits/recomputed/
    outputs/tables/                 tables/
    data/datasets/<ds>/cases.jsonl  data/gold/<ds>/cases.jsonl

复现脚本此前各自硬编码其中一种，导致换到另一种布局就 FileNotFoundError
（审稿人上一轮正是因此无法运行我们点名的脚本）。所有脚本一律通过本模块取路径，
新增数据位置只需在这里登记一次。

用法:
    from deposit_paths import find, find_glob, ROOT
    p = find("multiseed/blind_l1__seed0.jsonl")
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# 逻辑名 -> 候选相对路径（按优先级排列）
_LOCATIONS: dict[str, list[str]] = {
    # 手稿与文稿
    "manuscript": ["outputs/paper/manuscript.en.md", "manuscript/manuscript.md"],
    "supplementary": [
        "outputs/deliverables/supplementary_files/Supplementary_Material.md",
        "supplementary/Supplementary_Material.md",
    ],
    "figure_legends": ["outputs/paper/figure_legends.md",
                       "outputs/deliverables/supplementary_files/figure_legends.md",
                       "figures/figure_legends.md"],
    # 审计集设计（含 DDInter 原始严重度与更正规则）
    "audit_design": ["outputs/blind_test/blind_set_v3_ddinter.json",
                     "data/gold/audit_set_design.json"],
    # 专家评审
    "expert_archive": ["outputs/expert_review/expert_responses_archive.json",
                       "data/expert_review/expert_responses_archive.json"],
    "expert_questionnaire": ["outputs/expert_review/blind_gold_review_CN.csv",
                             "data/expert_review/blind_gold_review_CN.csv"],
    # 复算产物
    "recomputed_dir": ["outputs/recomputed", "audits/recomputed"],
    # Tier 情景
    "tier_override_scenario": ["outputs/audits/tier_override_scenario.json",
                               "audits/tier_override_scenario.json"],
    "tier_reassignment_scenarios": ["outputs/audits/tier_reassignment_scenarios.json",
                                    "audits/tier_reassignment_scenarios.json"],
    # 证据库
    "evidence_chunks": ["data/seed/evidence_chunks.jsonl",
                        "data/evidence/evidence_chunks.jsonl"],
    "entities_a": ["data/seed/entities_a.csv", "data/registry/entities_a.csv"],
    "curation_a": ["data/curation/entity_a_candidates.yaml",
                   "data/registry/entity_a_candidates.yaml"],
    # 规则与配置
    "rules": ["configs/rules.yaml"],
    "class_matrix": ["configs/class_matrix.yaml"],
    # 审计输出
    "divergence_by_tier": ["outputs/audits/divergence_by_tier.csv",
                           "audits/divergence_by_tier.csv"],
    "path_attribution": ["outputs/audits/path_attribution.json",
                         "audits/path_attribution.json"],
    "citation_report": ["outputs/citation_verification_report.json",
                        "data/evidence/citation_verification_report.json"],  # 仓库版在 data/evidence/
    # 预测与指标
    "metrics_majority": ["outputs/glm53_baselines/metrics_majority.json",
                         "data/predictions/glm53_baselines/metrics_majority.json"],
}


def find(key: str) -> pathlib.Path:
    """按逻辑名取第一个存在的路径；都不存在时返回首选路径（便于报错定位）。"""
    for rel in _LOCATIONS.get(key, []):
        p = ROOT / rel
        if p.exists():
            return p
    first = _LOCATIONS.get(key, [key])[0]
    return ROOT / first


def find_pair(key: str) -> tuple[pathlib.Path | None, pathlib.Path | None]:
    """返回 (gold_dir_cases, predictions_prefix) 一类的成对路径，供数据集使用。"""
    raise NotImplementedError


def gold_cases(dataset: str) -> pathlib.Path:
    """数据集 gold 文件：项目内 data/datasets/<ds>/cases.jsonl，仓库内 data/gold/<ds>/。"""
    cands = [ROOT / "data" / "datasets" / dataset / "cases.jsonl",
             ROOT / "data" / "gold" / dataset / "cases.jsonl"]
    for p in cands:
        if p.exists():
            return p
    return cands[0]


def predictions(dataset: str, seed: int = 0) -> pathlib.Path:
    """逐温度条件的预测文件。"""
    name = f"{dataset}__seed{seed}.jsonl"
    cands = [ROOT / "outputs" / "multiseed_per_dataset" / name,
             ROOT / "data" / "predictions" / name]
    for p in cands:
        if p.exists():
            return p
    return cands[0]


def glm53_predictions() -> pathlib.Path:
    cands = [ROOT / "outputs" / "glm53_baselines" / "predictions.jsonl",
             ROOT / "data" / "predictions" / "glm53_baselines" / "predictions.jsonl"]
    for p in cands:
        if p.exists():
            return p
    return cands[0]


def tables_dir() -> pathlib.Path:
    for rel in ("outputs/tables", "tables"):
        p = ROOT / rel
        if p.exists():
            return p
    return ROOT / "outputs" / "tables"


def recomputed(key: str) -> pathlib.Path:
    """复算产物目录下的某个文件。"""
    d = find("recomputed_dir")
    return d / key


if __name__ == "__main__":
    print(f"ROOT = {ROOT}\n")
    for k in _LOCATIONS:
        p = find(k)
        print(f"  {'OK ' if p.exists() else 'MISS'} {k:32s} -> {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}")
