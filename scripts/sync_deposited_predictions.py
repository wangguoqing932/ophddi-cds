# -*- coding: utf-8 -*-
"""sync_deposited_predictions.py — 让已归档的预测文件与当前因果引擎一致。

背景：flurbiprofen 的吸收分级由 high 更正为 low 之后，full_system 在 6 个用例上的
输出发生变化（blind_l1 的 C04；blind_v3_ddinter 的 D3-002/005/010/011；
external_validation 的 1 例）。聚合指标（multiseed_per_dataset_metrics.json）在读取时
用当前引擎重算 full_system，因此图表与表格本就是对的；但归档的原始预测文件里
full_system 的 predicted 列仍是修正前的值，直接抽查会得到 0.707 而非手稿的 0.674。

本脚本把这 30 行（6 用例 × 5 温度条件）的 predicted 更新为当前引擎输出。
gold_risk 列不动——那是数据集的 gold，不随吸收分级修正而改变。

用法:
    python scripts/sync_deposited_predictions.py [--apply]
不加 --apply 时只报告将要修改的行。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

TARGETS = [
    ROOT / "outputs" / "multiseed_per_dataset",
    ROOT.parent / "ophddi-cds" / "data" / "predictions",
]


def main() -> int:
    apply = "--apply" in sys.argv
    kg = PreciseKG()
    total_files = total_rows = 0

    for d in TARGETS:
        if not d.is_dir():
            print(f"跳过（不存在）: {d}")
            continue
        print(f"\n=== {d} ===")
        for p in sorted(d.glob("*.jsonl")):
            rows = []
            changed = []
            for line in p.open(encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("method") == "full_system":
                    new = kg.deterministic_level_v2(r["a_name"], r["b_name"])[0]
                    if new != r["predicted"]:
                        changed.append(f'{r["case_id"]} {r["a_name"]} x {r["b_name"]}: '
                                       f'{r["predicted"]} -> {new}')
                        r["predicted"] = new
                rows.append(r)
            if not changed:
                continue
            print(f"  {p.name}: {len(changed)} 行")
            for c in changed:
                print(f"      {c}")
            if apply:
                # 原文件是逐行 JSONL，重写保持同格式（ensure_ascii=False 与原文件一致）
                with p.open("w", encoding="utf-8", newline="\n") as fh:
                    for r in rows:
                        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            total_files += 1
            total_rows += len(changed)

    print(f"\n{'已更新' if apply else '待更新'}: {total_rows} 行，涉及 {total_files} 个文件")
    if not apply:
        print("加 --apply 实际写入。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
