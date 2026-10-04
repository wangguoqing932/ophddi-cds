#!/usr/bin/env python3
"""audit_ddinter_disagreement.py — Full-pair disagreement audit: system v2 vs DDInter raw data.

Enumerates all 113x232 pairs, compares system v2 output with the DDInter 2.0
record where one exists, and attributes disagreements to absorption tiers.
Reproducible; outputs a machine-readable JSON + human summary.
"""
import csv
import pathlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low", "unknown": None}
SEV = {"high": 3, "medium": 2, "low": 1}


def load_ddinter(root: Path) -> dict:
    ddinter = {}
    for code in ["A", "B", "C", "N", "S"]:
        # 项目内为 data/raw/ddinter/，公开仓库为 data/ddinter/；两处都找，
        # 使脚本在两种布局下均可直接运行。
        cands = [root / f"data/raw/ddinter/ddinter_code_{code}.csv",
                 root / f"data/ddinter/ddinter_code_{code}.csv"]
        path = next((p for p in cands if p.exists()), None)
        if path is None:
            raise FileNotFoundError(f"ddinter_code_{code}.csv 未找到，已尝试: {cands}")
        with path.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                a = row["Drug_A"].strip().lower()
                b = row["Drug_B"].strip().lower()
                ddinter[(a, b)] = row["Level"]
                ddinter[(b, a)] = row["Level"]
    return ddinter


def load_tier_override(path: pathlib.Path | None) -> dict:
    """从 curation YAML 读取分级覆盖表。

    用于回答"若以 curation 文件为准，registry 结论会怎样变化"：引擎的分级来自
    data/seed/entities_a.csv，这里在内存中把 flags 里的系统吸收分级替换为 curation
    文件的值，不修改任何数据文件。
    """
    if path is None:
        return {}
    import yaml
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = {}
    for e in d.get("entities", []):
        for f in e.get("flags", []):
            if "absorption" in f:
                out[e["primary_name"].lower()] = f
                break
    return out


def apply_tier_override(kg: PreciseKG, override: dict) -> int:
    """把覆盖写进已载入的分级表，返回被改动的实体数。"""
    changed = 0
    for key, ent in kg.a_registry.items():
        new = override.get(key)
        if not new:
            continue
        flags = [f for f in ent.get("flags", []) if "absorption" not in f]
        if new != next((f for f in ent.get("flags", []) if "absorption" in f), None):
            changed += 1
        ent["flags"] = flags + [new]
    return changed


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier-override", default=None,
                    help="用该 YAML 文件的吸收分级替代 registry（情景分析用）")
    args = ap.parse_args()

    kg = PreciseKG()
    override = load_tier_override(pathlib.Path(args.tier_override)
                                  if args.tier_override else None)
    if override:
        n = apply_tier_override(kg, override)
        print(f"[情景分析] 已用 {args.tier_override} 覆盖 {n} 个实体的吸收分级")
    ddinter = load_ddinter(ROOT)

    stats = Counter()
    diff_detail = Counter()
    diffs = []
    agree_by_level = Counter()

    for an, ae in kg.a_registry.items():
        for bn, be in kg.b_registry.items():
            di = ddinter.get((an.lower(), bn.lower()))
            dl = LEVEL_MAP.get(di.lower()) if di else None
            if dl is None:
                continue
            lvl, _, info = kg.deterministic_level_v2(an, bn)
            stats["recorded"] += 1
            if lvl == dl:
                stats["agree"] += 1
                agree_by_level[dl] += 1
            elif SEV[lvl] < SEV[dl]:
                stats["downgrade"] += 1
                diff_detail[f"{dl}->{lvl}"] += 1
                diffs.append({"ophthalmic": an, "systemic": bn, "ddinter": dl,
                              "system": lvl, "kind": "downgrade",
                              "a_absorption": next((f for f in ae["flags"]
                                                    if "systemic_absorption_" in f), "none")})
            else:
                stats["upgrade"] += 1
                diff_detail[f"{dl}->{lvl}"] += 1
                diffs.append({"ophthalmic": an, "systemic": bn, "ddinter": dl,
                              "system": lvl, "kind": "upgrade",
                              "a_absorption": next((f for f in ae["flags"]
                                                    if "systemic_absorption_" in f), "none")})

    n = stats["recorded"]
    low_abs_down = sum(1 for d in diffs if d["kind"] == "downgrade"
                       and d["a_absorption"] in ("systemic_absorption_low",
                                                 "systemic_absorption_very_low",
                                                 "minimal_systemic_absorption"))
    high_abs_up = sum(1 for d in diffs if d["kind"] == "upgrade"
                      and d["a_absorption"] == "systemic_absorption_high")

    report = {
        "schema_version": 2,
        "pairs_with_ddinter": n,
        "agree": {"n": stats["agree"], "share": round(stats["agree"] / n, 4),
                  "by_level": dict(agree_by_level)},
        "downgrade": {"n": stats["downgrade"],
                      "share": round(stats["downgrade"] / n, 4),
                      "attributable_to_low_absorption": low_abs_down,
                      "share_of_downgrades": round(low_abs_down / max(stats["downgrade"], 1), 4),
                      "detail": dict(diff_detail)},
        "upgrade": {"n": stats["upgrade"], "share": round(stats["upgrade"] / n, 4),
                    "attributable_to_high_absorption": high_abs_up},
        "generated_by": "scripts/audit_ddinter_disagreement.py",
    }
    # 项目内写到 outputs/tables/；公开仓库没有 outputs/tables/，改写到 tables/，
    # 使同一脚本在两种布局下都能把结果落在随仓库发布的目录里。
    outdir = (ROOT / "outputs" / "tables" if (ROOT / "outputs" / "tables").is_dir()
              else ROOT / "tables")
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "ddinter_disagreement_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "ddinter_disagreement_cases.jsonl").write_text(
        "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in diffs), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"\ncase-level detail -> {outdir / 'ddinter_disagreement_cases.jsonl'} ({len(diffs)} rows)")


if __name__ == "__main__":
    main()
