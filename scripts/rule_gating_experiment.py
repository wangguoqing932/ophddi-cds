# -*- coding: utf-8 -*-
"""rule_gating_experiment.py — 量化"给规则层加吸收门控"对 L1 一致率的影响。

背景（Section 4.2）：级联的最终等级取 max(规则层, 吸收缩放后的矩阵层)，而规则层不做
吸收门控。后果是 202 个低吸收药对经规则路径拿到 medium/high（其中 95 个 high 全部来自
nsaid_antihypertensive_antagonism）。手稿报告了"若给这条规则加门控，L1 一致率从 0.907
降到 0.890；若给四条 NSAID 规则都加，降到 0.847"，但此前没有沉积可复算的脚本，审稿人
无法验证。本脚本把该实验做成可复现的：

对每种门控方案，把被门控规则的 severity 临时改判为 low（即"低吸收时不再触发"），
在 L1 的 118 例上重算一致率。不修改任何配置文件，改动只在内存中生效。

用法:
    python scripts/rule_gating_experiment.py
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from deposit_paths import gold_cases, predictions, recomputed, find  # noqa: E402

import yaml  # noqa: E402
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

# 被考察的规则：手稿点名的单条，以及全部四条 NSAID 规则
TARGET_SINGLE = ["nsaid_antihypertensive_antagonism"]
TARGET_ALL_NSAID = [
    "nsaid_antihypertensive_antagonism",
    "nsaid_acei_arb_antagonism",
    "nsaid_diuretic_antagonism",
    "additive_nsaid_bleeding",
]

LOW_FAMILY = {"systemic_absorption_low", "systemic_absorption_very_low",
              "minimal_systemic_absorption", "systemic_absorption_none", "none"}


def load_gold() -> dict:
    rows = [json.loads(l) for l in gold_cases("blind_l1").open(encoding="utf-8") if l.strip()]
    return {r["case_id"]: (r.get("gold_risk_level") or r.get("gold_risk")) for r in rows}


def load_cases() -> list:
    return [json.loads(l) for l in predictions("blind_l1", 0).open(encoding="utf-8")
            if l.strip() and json.loads(l)["method"] == "full_system"]


def tier_of(kg, name: str) -> str | None:
    ent = kg.get_ophthalmic(name)
    if not ent:
        return None
    for f in ent.get("flags", []):
        if f in LOW_FAMILY or f in ("systemic_absorption_high", "systemic_absorption_medium"):
            return f
    return None


def evaluate(kg, cases: list, gold: dict) -> tuple:
    ok = 0
    for r in cases:
        lvl, _, _ = kg.deterministic_level_v2(r["a_name"], r["b_name"])
        if lvl == gold.get(r["case_id"]):
            ok += 1
    return ok, ok / len(cases)


def gate_rules(kg, rule_ids: list) -> int:
    """把指定规则的 severity 降为 low，模拟"该规则被吸收门控后不再抬高等级"。

    kg.rules 是整个 YAML 文档（顶层键 risk_levels / rules / patient_factor_rules），
    规则列表在 kg.rules["rules"] 里；直接改内存中的 severity，不写回文件。
    """
    n = 0
    doc = kg.rules if isinstance(kg.rules, dict) else {}
    for rule in doc.get("rules", []):
        if rule.get("id") in rule_ids:
            rule["severity"] = "low"
            n += 1
    return n


def main() -> int:
    gold = load_gold()
    cases = load_cases()
    raw_rules = yaml.safe_load(find("rules").read_text(encoding="utf-8"))

    results = {"n_cases": len(cases)}

    # 基线
    kg = PreciseKG()
    ok, acc = evaluate(kg, cases, gold)
    results["baseline"] = {"correct": ok, "accuracy": acc, "n": len(cases)}
    print(f"基线（规则层不加门控）        : {ok}/{len(cases)} = {acc:.4f}")

    # 方案 A：门控单条规则
    kg_a = PreciseKG()
    kg_a.rules = copy.deepcopy(kg_a.rules)
    n_a = gate_rules(kg_a, TARGET_SINGLE)
    ok_a, acc_a = evaluate(kg_a, cases, gold)
    results["gate_single"] = {"rules": TARGET_SINGLE, "n_gated": n_a,
                              "correct": ok_a, "accuracy": acc_a}
    print(f"门控 {TARGET_SINGLE[0]:32s}: {ok_a}/{len(cases)} = {acc_a:.4f}")

    # 方案 B：门控全部四条 NSAID 规则
    kg_b = PreciseKG()
    kg_b.rules = copy.deepcopy(kg_b.rules)
    n_b = gate_rules(kg_b, TARGET_ALL_NSAID)
    ok_b, acc_b = evaluate(kg_b, cases, gold)
    results["gate_all_nsaid"] = {"rules": TARGET_ALL_NSAID, "n_gated": n_b,
                                 "correct": ok_b, "accuracy": acc_b}
    print(f"门控全部 {len(TARGET_ALL_NSAID)} 条 NSAID 规则      : {ok_b}/{len(cases)} = {acc_b:.4f}")

    # 低吸收药对经规则路径拿到 high 的分布（解释门控为何降低一致率）
    dist = {"medium": 0, "high": 0}
    pairs_by_rule: dict = {}
    for r in cases:
        lvl, rules, info = kg.deterministic_level_v2(r["a_name"], r["b_name"])
        if tier_of(kg, r["a_name"]) in LOW_FAMILY and lvl in ("medium", "high"):
            dist[lvl] += 1
            for rid in (rules or []):
                pairs_by_rule[rid] = pairs_by_rule.get(rid, 0) + 1
    results["low_tier_rule_hits"] = {"by_level": dist, "by_rule": pairs_by_rule}
    print(f"\n低吸收药对经规则拿到 medium/high（L1 集）: {dist}")

    out = recomputed("rule_gating_experiment.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已写出 -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
