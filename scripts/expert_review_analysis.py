# -*- coding: utf-8 -*-
"""expert_review_analysis.py — 12 例专家评审的完整统计，按问卷实际记录计算。

回应审稿人意见 3（专家实验）。三处修正：

1. **R03 的专家评分按表单实际记录。** 原表把两位专家都记为 medium；扫描件、
   答卷存档与中文汇总均为 low。本脚本一律读取 expert_responses_archive.json
   （由扫描件转录）中的值，不沿用旧表。
2. **与系统的比较用专家实际看到的评级。** 问卷上印的 system_v2 才是专家作判断
   的依据；R10/R11 展示的是 medium，而当前引擎返回 low。用引擎值计算会高估
   一致性，因此本脚本用 shown（system_v2）。
3. **勘误案例单列。** R01–R03 的 gold 在专家评审前刚从 DDInter 原值改为系统评级，
   问卷只展示了更正后的标签。本脚本报告这些案例的更正前后值。

用法:
    python scripts/expert_review_analysis.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from stats_tests import (bootstrap_kappa, cohens_kappa,  # noqa: E402
                         max_kappa)

ARCHIVE = ROOT / "outputs" / "expert_review" / "expert_responses_archive.json"
CN = {"低": "low", "中": "medium", "高": "high"}
ORDER = ["low", "medium", "high"]

# R01–R03：问卷展示的 gold 是刚由 DDInter 原值更正而来的（见 blind_gold_review_CN.csv
# 的 "gold来源" 列："勘误后(原high)" 等）。
ERRATA = {
    "R01": {"ddinter_original": "high", "shown_gold": "medium"},
    "R02": {"ddinter_original": "medium", "shown_gold": "high"},
    "R03": {"ddinter_original": "low", "shown_gold": "medium"},
}

# 问卷上印给专家的"系统判定"值。
#
# 不能沿用 archive 的 system_v2 字段：该字段后来被更新为当前引擎输出。扫描件是
# 权威来源（专家看到什么就以它为准）。逐例核对 expert1_page1/2.png 后确认：
#   R01 中风险  R02 高风险  R03 中风险  R04 高风险  R05 高风险  R06 高风险
#   R07 低风险  R08 中风险  R09 中风险  R10 中风险  R11 中风险  R12 中风险
# 其中 R10、R11 与当前引擎（low）不同；R03 的专家评分在原表中被误记为 medium。
SHOWN_SYSTEM = {
    "R01": "medium", "R02": "high", "R03": "medium", "R04": "high",
    "R05": "high", "R06": "high", "R07": "low", "R08": "medium",
    "R09": "medium", "R10": "medium", "R11": "medium", "R12": "medium",
}

# 专家评分（扫描件转录）。R03 两位专家均勾选"低"，原表误记为 medium。
EXPERT_1 = {"R01": "low", "R02": "medium", "R03": "low", "R04": "medium",
            "R05": "medium", "R06": "medium", "R07": "low", "R08": "medium",
            "R09": "low", "R10": "low", "R11": "low", "R12": "low"}
# 专家 2 的答卷未提供扫描件；存档记录其答案与专家 1 全同，仅 R08 不同。
EXPERT_2 = dict(EXPERT_1, R08="high")


def build(archive: dict) -> dict:
    """按扫描件转录的值构建分析序列（不使用 archive 中可能被更新的 system_v2）。"""
    rows = archive["responses"]
    ids = [r["case_id"] for r in rows]
    e1 = [EXPERT_1[c] for c in ids]
    e2 = [EXPERT_2[c] for c in ids]
    shown = [SHOWN_SYSTEM[c] for c in ids]           # 专家看到的系统评级
    gold_shown = [r["gold_proposed"] for r in rows]  # 专家看到的 gold
    return {"rows": rows, "e1": e1, "e2": e2, "shown": shown, "gold": gold_shown}


def output(archive: dict) -> dict:
    d = build(archive)
    rows, e1, e2, shown, gold = d["rows"], d["e1"], d["e2"], d["shown"], d["gold"]
    n = len(rows)

    def pair(a, b):
        agree = sum(1 for x, y in zip(a, b) if x == y)
        return {"n": n, "agreement_count": agree, "agreement": agree / n,
                "kappa": cohens_kappa(a, b),
                "kappa_weighted_quadratic": cohens_kappa(a, b, weights="quadratic"),
                "kappa_weighted_linear": cohens_kappa(a, b, weights="linear"),
                "max_kappa": max_kappa(a, b),
                "bootstrap": bootstrap_kappa(a, b, n_resamples=2000, seed=20260803)}

    res = {
        "n_cases": n,
        "comparator": ("system grade shown to the experts (questionnaire system_v2); "
                       "not the current engine, which differs for R10 and R11"),
        "inter_rater": pair(e1, e2),
        "e1_vs_system_shown": pair(e1, shown),
        "e2_vs_system_shown": pair(e2, shown),
        "e1_vs_gold_shown": pair(e1, gold),
        "e2_vs_gold_shown": pair(e2, gold),
        "graded_lower_than_shown": {
            "expert_1": sum(1 for x, y in zip(e1, shown) if ORDER.index(x) < ORDER.index(y)),
            "expert_2": sum(1 for x, y in zip(e2, shown) if ORDER.index(x) < ORDER.index(y)),
            "expert_1_higher": sum(1 for x, y in zip(e1, shown) if ORDER.index(x) > ORDER.index(y)),
            "expert_2_higher": sum(1 for x, y in zip(e2, shown) if ORDER.index(x) > ORDER.index(y)),
        },
        "fully_concordant_cases": [
            {"case_id": r["case_id"], "ophthalmic": r["ophthalmic"], "systemic": r["systemic"]}
            for i, r in enumerate(rows)
            if e1[i] == e2[i] == shown[i] == gold[i]
        ],
        "system_high_rated_high_by_experts": {
            "n_system_high": sum(1 for x in shown if x == "high"),
            "e1": sum(1 for i in range(n) if shown[i] == "high" and e1[i] == "high"),
            "e2": sum(1 for i in range(n) if shown[i] == "high" and e2[i] == "high"),
        },
        "errata_cases": [
            {"case_id": r["case_id"],
             "ddinter_original": ERRATA[r["case_id"]]["ddinter_original"],
             "shown_gold": ERRATA[r["case_id"]]["shown_gold"],
             "expert_1": e1[i], "expert_2": e2[i],
             "current_gold": gold[i], "shown_system": shown[i]}
            for i, r in enumerate(rows)
            if r["case_id"] in ERRATA
        ],
        "per_case": [
            {"case_id": r["case_id"], "ophthalmic": r["ophthalmic"], "systemic": r["systemic"],
             "gold_shown": gold[i], "system_shown": shown[i],
             "expert_1": e1[i], "expert_2": e2[i]}
            for i, r in enumerate(rows)
        ],
    }
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(ROOT / "outputs" / "recomputed" /
                                          "expert_review_recomputed.json"))
    args = ap.parse_args()

    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    res = output(archive)

    print("=== 12 例专家评审（按问卷实际记录重算）===")
    for key, label in [("inter_rater", "专家间 (E1 vs E2)"),
                       ("e1_vs_system_shown", "E1 vs 系统(展示值)"),
                       ("e2_vs_system_shown", "E2 vs 系统(展示值)"),
                       ("e1_vs_gold_shown", "E1 vs gold(展示值)"),
                       ("e2_vs_gold_shown", "E2 vs gold(展示值)")]:
        v = res[key]
        print(f"  {label:22s} {v['agreement_count']:2d}/{v['n']} "
              f"({v['agreement']:.3f})  kappa={v['kappa']:+.3f} "
              f"[{v['bootstrap']['ci_low']:+.3f},{v['bootstrap']['ci_high']:+.3f}] "
              f"max={v['max_kappa']:.3f} wq={v['kappa_weighted_quadratic']:+.3f}")
    g = res["graded_lower_than_shown"]
    print(f"\n  判低于所见系统值: E1 {g['expert_1']}/12, E2 {g['expert_2']}/12")
    print(f"  判高于所见系统值: E1 {g['expert_1_higher']}/12, E2 {g['expert_2_higher']}/12")
    print(f"  四者完全一致的案例: {[c['case_id'] for c in res['fully_concordant_cases']]}")
    print(f"  系统判 high 的案例中，专家判 high 的: "
          f"E1 {res['system_high_rated_high_by_experts']['e1']}/"
          f"{res['system_high_rated_high_by_experts']['n_system_high']}, "
          f"E2 {res['system_high_rated_high_by_experts']['e2']}/"
          f"{res['system_high_rated_high_by_experts']['n_system_high']}")
    print("\n  勘误案例（gold 在评审前刚被更正）:")
    for e in res["errata_cases"]:
        print(f"    {e['case_id']}: DDInter 原值={e['ddinter_original']} "
              f"→ 问卷展示={e['shown_gold']}; 专家判 {e['expert_1']}/{e['expert_2']}")

    p = pathlib.Path(args.json)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已写出 -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
