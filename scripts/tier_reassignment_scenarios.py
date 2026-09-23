# -*- coding: utf-8 -*-
"""tier_reassignment_scenarios.py — 量化吸收分级修正对 §3.4 数字的影响。

审稿人意见 4 指出两处分级问题：
  (a) flurbiprofen 在注册表中为 high，而候选策展文件为 low（证据来源完全相同）
  (b) 113 个"眼科局部"药物中有 9 个并非局部给药

本脚本在内存中修正分级后重跑同一审计，报告 75.0% 等数字如何变化，
供作者在"是否重新赋值"上做决定。不修改任何数据文件。

用法: python scripts/tier_reassignment_scenarios.py
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low", "unknown": None}
SEV = {"high": 3, "medium": 2, "low": 1}
LOW_FAMILY = {"systemic_absorption_low", "systemic_absorption_very_low",
              "minimal_systemic_absorption", "systemic_absorption_none"}

# 审稿人意见 4c：9 个非局部给药药物
NON_TOPICAL = {
    "Ranibizumab": "intravitreal", "Aflibercept": "intravitreal",
    "Bevacizumab": "intravitreal", "Brolucizumab": "intravitreal",
    "Faricimab": "intravitreal", "Conbercept": "intravitreal",
    "Acetylcholine intraocular": "intraocular",
    "Carboxymethylcellulose": "intraocular",
    "Hydroxypropyl methylcellulose": "intraocular",
}


def load_ddinter() -> dict:
    dd = {}
    for code in ["A", "B", "C", "N", "S"]:
        f = ROOT / "data" / "raw" / "ddinter" / f"ddinter_code_{code}.csv"
        for row in csv.DictReader(f.open(encoding="utf-8-sig")):
            a, b = row["Drug_A"].strip().lower(), row["Drug_B"].strip().lower()
            dd[(a, b)] = row["Level"]
            dd[(b, a)] = row["Level"]
    return dd


def set_tier(kg: PreciseKG, name: str, tier: str) -> bool:
    """在内存中替换某药的分级标志。"""
    ent = kg.a_registry.get(name.lower())
    if not ent:
        return False
    flags = [f for f in ent["flags"]
             if not (f.startswith("systemic_absorption_") or f == "minimal_systemic_absorption")]
    if tier:
        flags.append(tier)
    ent["flags"] = flags
    return True


def tier_of(kg: PreciseKG, name: str) -> str:
    ent = kg.a_registry.get(name.lower())
    if not ent:
        return "(absent)"
    for f in ent["flags"]:
        if f.startswith("systemic_absorption_") or f == "minimal_systemic_absorption":
            return f
    return "(no tier)"


def run_audit(kg: PreciseKG, dd: dict, exclude: set[str] | None = None) -> dict:
    exclude = exclude or set()
    stats = Counter()
    diffs = []
    for an, ae in kg.a_registry.items():
        if ae["name"] in exclude:
            continue
        for bn in kg.b_registry:
            di = dd.get((an.lower(), bn.lower()))
            dl = LEVEL_MAP.get(di.lower()) if di else None
            if dl is None:
                continue
            lvl, _, _ = kg.deterministic_level_v2(an, bn)
            stats["recorded"] += 1
            if lvl == dl:
                stats["agree"] += 1
            elif SEV[lvl] < SEV[dl]:
                stats["downgrade"] += 1
                diffs.append({"ophthalmic": ae["name"], "systemic": bn, "kind": "downgrade",
                              "a_absorption": tier_of(kg, ae["name"])})
            else:
                stats["upgrade"] += 1
                diffs.append({"ophthalmic": ae["name"], "systemic": bn, "kind": "upgrade",
                              "a_absorption": tier_of(kg, ae["name"])})
    n = stats["recorded"]
    low_down = sum(1 for d in diffs if d["kind"] == "downgrade"
                   and d["a_absorption"] in LOW_FAMILY)
    return {
        "pairs": n,
        "downgrade": stats["downgrade"],
        "downgrade_share": round(stats["downgrade"] / n, 4) if n else 0,
        "upgrade": stats["upgrade"],
        "low_absorption_downgrades": low_down,
        "share_of_downgrades": round(low_down / max(stats["downgrade"], 1), 4),
        "agree": stats["agree"],
    }


def show(tag: str, r: dict) -> None:
    print(f"  {tag:34s} n={r['pairs']:5d}  降级={r['downgrade']:5d} ({r['downgrade_share']*100:5.1f}%)  "
          f"低吸收归因={r['low_absorption_downgrades']:5d} ({r['share_of_downgrades']*100:4.1f}%)  "
          f"升级={r['upgrade']:4d}")


def main() -> int:
    dd = load_ddinter()
    kg = PreciseKG()

    print("=" * 108)
    print("吸收分级修正的情景分析（相同审计，仅分级不同）")
    print("=" * 108)

    baseline = run_audit(kg, dd)
    show("① 基线（现行注册表）", baseline)

    # 核对 flurbiprofen 当前分级与涉及对数
    print(f"\n  flurbiprofen 当前分级: {tier_of(kg, 'Flurbiprofen')}")
    fp_pairs = [b for (a, b) in dd if a == "flurbiprofen"] + \
               [a for (a, b) in dd if b == "flurbiprofen"]
    print(f"  注册表内 flurbiprofen 涉及 DDInter 记录的对数: {len(set(p.lower() for p in fp_pairs))}")
    print(f"\n  9 个非局部给药药物的当前分级:")
    for nm in NON_TOPICAL:
        print(f"    {nm:32s} {tier_of(kg, nm):32s} ({NON_TOPICAL[nm]})")

    # 场景 A：flurbiprofen high -> low
    kg2 = PreciseKG()
    set_tier(kg2, "Flurbiprofen", "systemic_absorption_low")
    a = run_audit(kg2, dd)
    print()
    show("② flurbiprofen high→low", a)

    # 场景 B：排除 9 个非局部给药药物
    kg3 = PreciseKG()
    b = run_audit(kg3, dd, exclude=set(NON_TOPICAL))
    show("③ 排除 9 个非局部给药药物", b)

    # 场景 C：两者同时
    kg4 = PreciseKG()
    set_tier(kg4, "Flurbiprofen", "systemic_absorption_low")
    c = run_audit(kg4, dd, exclude=set(NON_TOPICAL))
    show("④ 两者同时修正", c)

    out = ROOT / "outputs" / "audits" / "tier_reassignment_scenarios.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "baseline": baseline, "A_flurbiprofen_low": a,
        "B_exclude_non_topical": b, "C_both": c,
        "flurbiprofen_current_tier": tier_of(kg, "Flurbiprofen"),
        "non_topical_agents": {k: tier_of(kg, k) for k in NON_TOPICAL},
        "note": "同一次审计在不同分级下的结果；不修改任何数据文件。",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n写出 -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
