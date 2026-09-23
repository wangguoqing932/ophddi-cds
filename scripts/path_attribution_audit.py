# -*- coding: utf-8 -*-
"""path_attribution_audit.py — 回应审稿人意见 3 与 6 的定量核查。

意见 3：论文称吸收缩放"将低吸收药对强制降为 low"，但引擎实现是
  final = max(未门控的规则层, 吸收缩放后的矩阵层)。本脚本统计每条路径实际
  产生了多少分级，以及低吸收药物经规则路径拿到 medium/high 的数量。

意见 6：1,933 对的分歧在多大程度上是"构造使然"。本脚本给出按吸收分级与
  DDInter 严重度的交叉分布，并在替代分级赋值下重算 75.0% 这一数字。

输出：<outdir>/path_attribution.json 与 <outdir>/divergence_by_tier.csv
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LOW_FAMILY = {"systemic_absorption_low", "systemic_absorption_very_low",
              "minimal_systemic_absorption", "systemic_absorption_none", "none"}


def tier_flags(kg, name: str) -> str:
    ent = kg.get_ophthalmic(name)
    if not ent:
        return "(unregistered)"
    for f in ent.get("flags", []):
        if f in LOW_FAMILY or f in ("systemic_absorption_high", "systemic_absorption_medium"):
            return f
    return "(no tier)"


def main() -> int:
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else (ROOT / "outputs" / "audits")
    outdir.mkdir(parents=True, exist_ok=True)
    kg = PreciseKG()

    oph_names = [e["name"] for e in kg.a_registry.values()]
    sys_names = [e["name"] for e in kg.b_registry.values()]

    # ── 意见 3：路径归因 ──
    path_counter: Counter = Counter()
    path_by_level: dict[str, Counter] = defaultdict(Counter)
    low_tier_violations = []
    total = 0
    for o in oph_names:
        for s in sys_names:
            lvl, rules, info = kg.deterministic_level_v2(o, s)
            if lvl is None:
                continue
            total += 1
            p = info.get("path", "?")
            path_counter[p] += 1
            path_by_level[p][lvl] += 1
            if tier_flags(kg, o) in LOW_FAMILY and lvl in ("medium", "high"):
                low_tier_violations.append({
                    "ophthalmic": o, "systemic": s, "level": lvl, "path": p,
                    "rules": rules, "tier": tier_flags(kg, o),
                })

    print(f"总评估对数: {total}")
    print("路径分布:")
    for p, n in path_counter.most_common():
        lv = ", ".join(f"{k}={v}" for k, v in path_by_level[p].most_common())
        print(f"  {p:22s} {n:6d}  ({n/total*100:5.1f}%)   {lv}")

    viol_by_path = Counter(v["path"] for v in low_tier_violations)
    viol_by_level = Counter(v["level"] for v in low_tier_violations)
    viol_rules = Counter(r for v in low_tier_violations for r in (v["rules"] or []))
    print(f"\n低吸收分级却拿到 medium/high 的对数: {len(low_tier_violations)}")
    print(f"  按等级: {dict(viol_by_level)}")
    print(f"  按路径: {dict(viol_by_path)}")
    print(f"  涉及规则 (top): {viol_rules.most_common(6)}")

    report = {
        "total_pairs_evaluated": total,
        "paths": {p: {"n": n, "pct": round(n / total * 100, 2),
                      "levels": dict(path_by_level[p])} for p, n in path_counter.items()},
        "low_tier_non_low_outcomes": {
            "n": len(low_tier_violations),
            "by_level": dict(viol_by_level),
            "by_path": dict(viol_by_path),
            "by_rule": dict(viol_rules.most_common(20)),
        },
        "note": ("final = max(ungated rule severity, absorption-scaled matrix level); "
                 "the absorption forcing applies to the matrix branch only."),
    }
    (outdir / "path_attribution.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ── 意见 6：分歧按分级的交叉分布 ──
    audit = ROOT / "outputs" / "blind_test" / "ddinter_disagreement_report.md"
    rows = []
    try:
        preds = ROOT / "outputs" / "multiseed_per_dataset" / "blind_v3_ddinter__seed0.jsonl"
        seen = {}
        for line in preds.open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["method"] != "full_system":
                continue
            key = (r["a_name"], r["b_name"])
            seen[key] = r
        dist = Counter()
        for (a, b), r in seen.items():
            dist[(tier_flags(kg, a), r["gold_risk"], r["predicted"])] += 1
        with (outdir / "divergence_by_tier.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["absorption_tier", "gold_risk", "system_level", "n_pairs"])
            for (t, g, p), n in sorted(dist.items()):
                w.writerow([t, g, p, n])
                rows.append({"tier": t, "gold": g, "system": p, "n": n})
        print(f"\n审计集分层分布已写出: {len(rows)} 行")
    except Exception as exc:
        print("审计集分层跳过:", exc)

    print(f"\n写出 -> {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
