# -*- coding: utf-8 -*-
"""rerun_lightrag_flurbiprofen.py — 定向重跑受 flurbiprofen 分级修正影响的 lightrag 预测。

背景：flurbiprofen 的吸收分级由 high 修正为 low（数据录入错误）。四种方法中：
  pure_llm   prompt 只含药名                     -> 不受影响
  naive_rag  检索语料与查询串未变                 -> 不受影响
  lightrag   prompt 含注册表 flags（已变）        -> 受影响，需重跑
  full_system 确定性引擎                          -> 逻辑重算，无需 API

本脚本仅重跑 lightrag 在含 flurbiprofen 案例上的预测，用与原始评估完全相同的
system prompt、温度表、max_tokens 与解析规则（见 configs/prompts.yaml）。
原文件就地备份为 *.preflurb.bak。

用法: python scripts/rerun_lightrag_flurbiprofen.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI  # noqa: E402
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
MAX_TOKENS = 600 if "flash" in MODEL else 10
TEMPERATURE = {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.9, 4: 1.2}
DATASETS = ["blind_l1", "blind_v3_ddinter", "dev-ddinter", "external_validation"]

# 与 scripts/run_multiseed_per_dataset.py 中的 SYSTEM 逐字一致
SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""

kg = PreciseKG()


def call(prompt: str, temperature: float) -> str:
    for a in range(5):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}],
                temperature=temperature, max_tokens=MAX_TOKENS)
            return r.choices[0].message.content.strip().lower()
        except Exception:
            if a < 4:
                time.sleep(2 ** (a + 1))
            else:
                return "error"


def parse(raw: str) -> str:
    t = raw.lower()
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    grand = 0
    for ds in DATASETS:
        for seed in range(5):
            f = ROOT / "outputs" / "multiseed_per_dataset" / f"{ds}__seed{seed}.jsonl"
            if not f.exists():
                print(f"  跳过（不存在）: {f.name}")
                continue
            rows = [json.loads(l) for l in f.open(encoding="utf-8") if l.strip()]
            hits = [i for i, r in enumerate(rows)
                    if r["method"] == "lightrag"
                    and "flurbiprofen" in (r["a_name"] + r["b_name"]).lower()]
            if not hits:
                continue
            grand += len(hits)
            if args.dry_run:
                print(f"  {f.name}: {len(hits)} 行待重跑")
                continue

            backup = f.with_suffix(".jsonl.preflurb.bak")
            if not backup.exists():
                shutil.copy2(f, backup)

            temp = TEMPERATURE[seed]
            for i in hits:
                r = rows[i]
                prompt = f"Drug profiles:\n{kg.full_kg_context(r['a_name'], r['b_name'])}\n\nDrug pair: ophthalmic {r['a_name']} (eye drops) + systemic {r['b_name']} (oral/IV)\nRisk level:"
                raw = call(prompt, temp)
                old = r["predicted"]
                r["predicted"] = parse(raw)
                r["raw"] = raw
                print(f"    {ds} seed{seed} {r['case_id']} {r['a_name']}×{r['b_name']}: {old} -> {r['predicted']}")
                time.sleep(0.15)

            f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")

    print(f"\n{'待重跑' if args.dry_run else '已重跑'} {grand} 行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
