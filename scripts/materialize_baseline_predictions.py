# -*- coding: utf-8 -*-
"""materialize_baseline_predictions.py — 从真实多种子评估物化 outputs/baseline_predictions.jsonl。

执行 skill 的 executor→writer 交接契约要求的验证产物。数据来源是实际的
4 方法 × 5 温度 × 4 数据集运行结果（outputs/multiseed_per_dataset/*__seed*.jsonl），
不生成任何替代性或合成数据：若源数据中出现 synthetic=true 会直接拒绝运行。

同时写出 outputs/baseline_predictions.metadata.json 记录溯源（源文件清单、行数分布、
rules.yaml 哈希、口径说明），使该文件可追溯到具体运行而不是一个无名产物。
"""
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_GLOB = ROOT / "outputs" / "multiseed_per_dataset"
OUT = ROOT / "outputs" / "baseline_predictions.jsonl"
META = ROOT / "outputs" / "baseline_predictions.metadata.json"
RULES = ROOT / "configs" / "rules.yaml"

REQUIRED = {"case_id", "dataset_id", "dataset_role", "method", "gold_risk", "predicted", "seed", "temperature"}
BAD_PRED = {None, "", "error", "unparseable"}


def main():
    files = sorted(SRC_GLOB.glob("*__seed*.jsonl"))
    if not files:
        sys.exit(f"no source predictions under {SRC_GLOB}")

    rows, per_ds_seed, per_method, unusable = [], Counter(), Counter(), 0
    for f in files:
        for line in f.open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            missing = REQUIRED - r.keys()
            if missing:
                sys.exit(f"{f.name}: row {r.get('case_id')} missing fields {sorted(missing)}")
            if r.get("synthetic"):
                sys.exit(f"{f.name}: synthetic row found — refusing to materialize")
            if r.get("predicted") in BAD_PRED:
                unusable += 1
            rows.append(r)
            per_ds_seed[(r["dataset_id"], r["seed"])] += 1
            per_method[r["method"]] += 1

    OUT.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
                   encoding="utf-8")

    meta = {
        "description": ("Consolidated predictions from the real 4-method x 5-temperature x 4-dataset "
                        "evaluation. Materialized to satisfy the medical-agent executor->writer handoff "
                        "contract; contains no synthetic or surrogate rows."),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": [f.name for f in files],
        "source_dir": str(SRC_GLOB.relative_to(ROOT)),
        "rows": len(rows),
        "rows_per_dataset_seed": {f"{d}|seed{s}": n for (d, s), n in sorted(per_ds_seed.items())},
        "rows_per_method": dict(sorted(per_method.items())),
        "unusable_predictions": unusable,
        "methods": sorted(per_method),
        "datasets": sorted({d for d, _ in per_ds_seed}),
        "seeds": sorted({s for _, s in per_ds_seed}),
        "rules_yaml_sha256": hashlib.sha256(RULES.read_bytes()).hexdigest(),
        "all_synthetic_false": True,
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}  rows={len(rows)}  unusable={unusable}")
    print(f"wrote {META.relative_to(ROOT)}")
    print(f"  datasets: {meta['datasets']}")
    print(f"  seeds   : {meta['seeds']}")
    print(f"  methods : {meta['methods']}")


if __name__ == "__main__":
    main()
