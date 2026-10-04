# -*- coding: utf-8 -*-
"""rebuild_metrics_json.py — 依据修正后的预测文件重建 multiseed_per_dataset_metrics.json。

背景：flurbiprofen 的吸收分级由 high 更正为 low 后，full_system 输出与 lightrag 的
prompt 都发生变化（lightrag 已用 scripts/rerun_lightrag_flurbiprofen.py 定向重跑）。
本脚本重算聚合指标，使下游图表（draw_figure2/3 等）与表格反映修正后的结果。

保持与原文件相同的键结构，便于下游脚本直接读取。
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LEVELS = ["low", "medium", "high"]
METHODS = ["pure_llm", "naive_rag", "lightrag", "full_system"]
DATASETS = ["blind_l1", "blind_v3_ddinter", "dev-ddinter", "external_validation"]
TEMPERATURE = {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.9, 4: 1.2}

kg = PreciseKG()


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    acc4 = sum(1 for r in rows if r["pred"] == r["gold"]) / n
    tp = sum(1 for r in rows if r["gold"] == "high" and r["pred"] == "high")
    fp = sum(1 for r in rows if r["gold"] != "high" and r["pred"] == "high")
    fn = sum(1 for r in rows if r["gold"] == "high" and r["pred"] != "high")
    tn = sum(1 for r in rows if r["gold"] != "high" and r["pred"] != "high")
    sens = tp / (tp + fn) if tp + fn else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * prec * sens / (prec + sens) if prec + sens else 0.0
    pe = sum((sum(1 for r in rows if r["gold"] == L) / n) *
             (sum(1 for r in rows if r["pred"] == L) / n) for L in LEVELS)
    kappa = (acc4 - pe) / (1 - pe) if pe < 1 else 0.0
    return {"n": n, "acc4": acc4, "sens": sens, "spec": spec, "f1": f1, "kappa": kappa}


def main() -> int:
    per_dataset: dict = {}
    per_subset: dict = {}

    for ds in DATASETS:
        d: dict = defaultdict(lambda: defaultdict(list))
        for seed in range(5):
            f = ROOT / "outputs" / "multiseed_per_dataset" / f"{ds}__seed{seed}.jsonl"
            for line in f.open(encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                # full_system 用当前引擎重算（确定性，且吸收了 flurbiprofen 修正）
                pred = (kg.deterministic_level_v2(r["a_name"], r["b_name"])[0]
                        if r["method"] == "full_system" else r["predicted"])
                d[r["method"]][seed].append({
                    "gold": r["gold_risk"], "pred": pred,
                    "subset": r.get("subset"), "role": r.get("dataset_role"),
                })

        per_dataset[ds] = {}
        for m in METHODS:
            per_seed = [metrics(d[m][s]) for s in range(5)]
            entry = {"n": per_seed[0]["n"]}
            for key in ["acc4", "sens", "spec", "f1", "kappa"]:
                vals = [p[key] for p in per_seed]
                entry[key] = {"mean": st.mean(vals), "std": st.pstdev(vals), "values": vals}
            per_dataset[ds][m] = entry

        if ds == "blind_l1":
            subs = sorted({r["subset"] for s in range(5) for r in d["full_system"][s]
                           if r.get("subset")})
            for sub in subs:
                per_subset[sub] = {}
                for m in METHODS:
                    per_seed = []
                    for s in range(5):
                        rows = [r for r in d[m][s] if r.get("subset") == sub]
                        if rows:
                            per_seed.append(metrics(rows))
                    if per_seed:
                        per_subset[sub][m] = {
                            k: {"mean": st.mean(p[k] for p in per_seed),
                                "std": st.pstdev(p[k] for p in per_seed),
                                "values": [p[k] for p in per_seed]}
                            for k in ["acc4", "sens", "spec", "f1", "kappa"]}

    out = {
        "mode": "real_llm",
        "seeds": [0, 1, 2, 3, 4],
        "temperature_schedule": TEMPERATURE,
        "methods": METHODS,
        "datasets": DATASETS,
        "n_predictions": 9600,
        "n_api_failures": 0,
        "api_failures": [],
        "per_dataset": per_dataset,
        "per_subset_l1": per_subset,
        "generalization_gap": {},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": ("Rebuilt after correcting the flurbiprofen absorption tier (high -> low). "
                 "full_system predictions recomputed with the current deterministic engine; "
                 "lightrag predictions for flurbiprofen cases re-run via the API."),
    }
    dest = ROOT / "outputs" / "multiseed_per_dataset" / "multiseed_per_dataset_metrics.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"rebuilt -> {dest}")
    for ds in DATASETS:
        for m in METHODS:
            e = per_dataset[ds][m]
            print(f"  {ds:22s} {m:12s} acc4={e['acc4']['mean']:.4f} "
                  f"sens={e['sens']['mean']:.3f} kappa={e['kappa']['mean']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
