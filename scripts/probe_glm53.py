# -*- coding: utf-8 -*-
"""probe_glm53.py — 探测 glm-5.3-flash 的可用性与输出稳定性。

用途：确定基线重跑所需的 token 预算与重复采样次数。

用法: python scripts/probe_glm53.py [重复次数]
"""
from __future__ import annotations

import json
import os
import statistics as st
import sys
import time
from collections import Counter
from pathlib import Path

import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

BASE = "https://open.bigmodel.cn/api/coding/paas/v4"   # coding plan 专属端点
MODEL = "glm-5.3-flash"

SYS = ("You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.\n\n"
       "Classify the interaction risk as: low, medium, or high.\n"
       "- low: negligible clinical significance at ophthalmic doses\n"
       "- medium: potential interaction requiring monitoring or dose adjustment\n"
       "- high: clinically significant interaction; may require avoidance or strict monitoring\n\n"
       "Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, "
       "but some drugs like timolol, atropine, dexamethasone reach >50%).\n\n"
       "Reply with EXACTLY ONE WORD: low, medium, or high. No explanation.")


def api_key() -> str:
    """读取智谱 API key（id.secret 形式）。优先环境变量，便于复现。"""
    k = os.getenv("ZHIPU_API_KEY", "")
    if k:
        return k
    env = ROOT / ".env"
    for line in env.read_text(encoding="utf-8").splitlines():
        if line.startswith("ZHIPU_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("未找到 ZHIPU_API_KEY（请写入 .env 或设置环境变量）")


def call(key: str, prompt: str, max_tokens: int, temperature: float) -> tuple[str, dict, float]:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body,
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    last = None
    for attempt in range(6):
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            return (d["choices"][0]["message"].get("content", "").strip().lower(),
                    d.get("usage", {}), time.time() - t0)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503):
                wait = 8 * (attempt + 1)          # 递增退避，缓解限流
                time.sleep(wait)
                continue
            raise
    raise last


def parse(raw: str) -> str:
    t = raw.lower()
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unknown"


PAIRS = [
    ("Timolol", "Atenolol", "high"),
    ("Timolol", "Verapamil", "high"),
    ("Betaxolol", "Verapamil", "medium"),
    ("Dexamethasone", "Rifampicin", "medium"),
    ("Fluorometholone", "Prednisone", "low"),
    ("Levofloxacin", "Sotalol", "low"),
]


def main() -> int:
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    key = api_key()
    print(f"模型 {MODEL} | 重复 {reps} 次 | 温度 0.0 | max_tokens 1500\n")
    hdr = f"{'药对':<40}{'答案分布':<28}{'一致率':>8}{'中位耗时':>10}{'中位推理token':>14}"
    print(hdr)
    print("-" * len(hdr))
    times, rtoks = [], []
    for oph, sysd, gold in PAIRS:
        prompt = (f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)\n"
                  f"Risk level:")
        outs = []
        for i in range(reps):
            try:
                raw, usage, dt = call(key, prompt, 1500, 0.0)
                outs.append(parse(raw))
                times.append(dt)
                rtoks.append(usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0))
            except Exception as e:
                outs.append("error")
                print(f"    调用失败: {str(e)[:80]}")
            time.sleep(2.0)
        c = Counter(outs)
        top, n = c.most_common(1)[0]
        agree = n / len(outs)
        print(f"{f'{oph} x {sysd}':<40}{str(dict(c)):<28}{agree:>8.2f}{st.median(times):>9.1f}s"
              f"{st.median(rtoks):>14.0f}")
    print(f"\n整体：{len(times)} 次调用，中位耗时 {st.median(times):.1f}s，"
          f"中位推理 {st.median(rtoks):.0f} tokens，总时长 {sum(times)/60:.1f} 分钟")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
