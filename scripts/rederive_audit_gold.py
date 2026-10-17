# -*- coding: utf-8 -*-
"""rederive_audit_gold.py — 按 §2.3 声明的校正规则重导 92 例审计集 gold。

背景（审稿人 round-4 意见 6）：审计设计文件 gold 的实际校正与声明规则有三类偏差：
  (i)   D3-048/049/057/063/078/079/081 被校正为 low，但级联经机制规则命中这些配对
        ——不满足"无规则命中"条件；
  (ii)  两例 aflibercept 对（tier none）保留 DDInter 原值，而声明规则本应校正；
  (iii) 四例 flurbiprofen 对按设计文件里已被替换的 high 层级保留（层级在锁之后才改为 low）。

本脚本用声明规则 + 当前注册表层级重导 gold：tier 为 low 或更低、级联路径非规则、
且矩阵无升级（矩阵给出的级别不高于 low）三者同时满足才校正为 low，否则保留 DDInter 原值。

用法:
    python scripts/rederive_audit_gold.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from deposit_paths import find, predictions  # noqa: E402
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

RANK = {"systemic_absorption_high": 5, "systemic_absorption_medium": 4,
        "systemic_absorption_low": 3, "systemic_absorption_very_low": 2,
        "minimal_systemic_absorption": 1, "systemic_absorption_none": 0, "none": 0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(ROOT / "outputs" / "recomputed" /
                                          "audit_gold_rederived.json"))
    args = ap.parse_args()

    design = json.loads(find("audit_design").read_text(encoding="utf-8"))
    kg = PreciseKG()

    def live_tier(name: str):
        ent = kg.get_ophthalmic(name)
        if not ent:
            return None
        return next((f for f in ent["flags"] if "absorption" in f or f == "none"), None)

    rederived = {}
    per_case = []
    for c in design:
        cid = c["case_id"]
        lvl, _, info = kg.deterministic_level_v2(c["ophthalmic_drug"], c["systemic_drug"])
        path = info.get("path")
        tier = live_tier(c["ophthalmic_drug"]) or c["absorption"]
        matrix_upgrade = (path == "matrix" and lvl in ("medium", "high"))
        correct = (RANK[tier] <= 3) and (path != "rule") and not matrix_upgrade
        rederived[cid] = "low" if correct else c["ddinter_level"]
        per_case.append({"case_id": cid, "ophthalmic": c["ophthalmic_drug"],
                         "systemic": c["systemic_drug"],
                         "gold_as_applied": c["proposed_gold"],
                         "gold_rederived": rederived[cid],
                         "ddinter": c["ddinter_level"], "tier": tier, "path": path})

    changed = [r for r in per_case if r["gold_as_applied"] != r["gold_rederived"]]

    # 两种口径下 full_system 的成绩
    fs = {}
    for seed in range(5):
        p = predictions("blind_v3_ddinter", seed)
        for line in p.open(encoding="utf-8"):
            r = json.loads(line)
            if r["method"] == "full_system":
                fs[r["case_id"]] = r["predicted"]
    def score(gold):
        ok = sum(1 for cid in fs if fs[cid] == gold[cid])
        hr = [cid for cid in fs if gold[cid] == "high"]
        sens = sum(1 for cid in hr if fs[cid] == "high")
        return {"accuracy": ok, "n": len(fs), "acc": round(ok / len(fs), 4),
                "high_risk_sens": f"{sens}/{len(hr)}"}
    gold_now = {r["case_id"]: r["gold_as_applied"] for r in per_case}

    out = {"rule": "correct to low iff tier<=low AND path!=rule AND no matrix upgrade",
           "tier_source": "current registry (data/seed/entities_a.csv)",
           "n_cases": len(per_case),
           "n_changed": len(changed),
           "changed_cases": changed,
           "full_system_as_applied": score(gold_now),
           "full_system_rederived": score(rederived),
           "per_case": per_case}
    p = pathlib.Path(args.json)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"重导 gold：{len(changed)}/{len(per_case)} 例与实际应用的 gold 不同")
    for r in changed:
        print(f"  {r['case_id']} {r['ophthalmic']}x{r['systemic']}: "
              f"{r['gold_as_applied']} -> {r['gold_rederived']} (tier={r['tier']}, path={r['path']})")
    print(f"full_system: 实际 gold {out['full_system_as_applied']['accuracy']}/92 "
          f"({out['full_system_as_applied']['acc']:.3f}), sens {out['full_system_as_applied']['high_risk_sens']} | "
          f"重导 gold {out['full_system_rederived']['accuracy']}/92 "
          f"({out['full_system_rederived']['acc']:.3f}), sens {out['full_system_rederived']['high_risk_sens']}")
    print(f"已写出 -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
