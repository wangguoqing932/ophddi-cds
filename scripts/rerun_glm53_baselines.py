# -*- coding: utf-8 -*-
"""rerun_glm53_baselines.py — 用推理模型 glm-5.3-flash 重跑 LLM 基线（回应审稿人意见 5）。

审稿人指出原比较"不能支撑其结论"：10-token 上限、单一非推理模型、每个条件只调一次
温度。本脚本按审稿人的要求重跑：

  * 模型：glm-5.3-flash（推理模型，coding plan 端点）
  * 输出预算：3000 tokens（推理链可充分展开）
  * 采样：固定 temperature 0.0，每例重复 5 次，取多数票
  * 解析规则：预先规定（见 parse()），与稿件一并报告
  * prompt：与原始评估逐字一致（configs/prompts.yaml），保证可比性

输出（可续跑）：
  outputs/glm53_baselines/predictions.jsonl   每行一次调用
  outputs/glm53_baselines/metrics.json        汇总指标

用法:
  python scripts/rerun_glm53_baselines.py --pilot 20     # 小规模验证
  python scripts/rerun_glm53_baselines.py               # 全量
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

BASE = "https://open.bigmodel.cn/api/coding/paas/v4"   # coding plan 专属端点
MODEL = "glm-5.3-flash"
MAX_TOKENS = 3000
TEMPERATURE = 0.0
REPS = 5
DATASETS = ["blind_l1", "blind_v3_ddinter"]
METHODS = ["pure_llm", "naive_rag", "lightrag"]
OUT = ROOT / "outputs" / "glm53_baselines"

# 与 scripts/run_multiseed_per_dataset.py 中的 SYSTEM 逐字一致
SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""

LEVELS = ["low", "medium", "high"]
_lock = threading.Lock()


def api_key() -> str:
    k = os.getenv("ZHIPU_API_KEY", "")
    if k:
        return k
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ZHIPU_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("未找到 ZHIPU_API_KEY")


KEY = api_key()


def call(prompt: str, retries: int = 6) -> tuple[str, dict]:
    """单次调用；仅对限流/服务端错误重试。返回 (原始内容, usage)。"""
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                BASE + "/chat/completions", data=body,
                headers={"Authorization": "Bearer " + KEY,
                         "Content-Type": "application/json"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            msg = d["choices"][0]["message"]
            return msg.get("content", "").strip(), {**d.get("usage", {}),
                                                    "elapsed_s": round(time.time() - t0, 2)}
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(min(5 * (attempt + 1), 45))
                continue
            raise
        except Exception as e:                      # 网络抖动
            last = e
            time.sleep(min(3 * (attempt + 1), 30))
    raise last if last else RuntimeError("call failed")


def parse(raw: str) -> str:
    """预先规定的解析规则（与稿件一并报告）。

    1. 归一化（去空白、小写、去句末标点）
    2. 整体等于 low/medium/high -> 该值
    3. 否则按 high > medium/moderate > low 的顺序子串匹配
    4. 均不命中 -> unknown
    """
    t = raw.strip().lower().rstrip(".")
    if t in LEVELS:
        return t
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unknown"


def load_cases(ds: str) -> list[dict]:
    """取该数据集全案例（跨 seed 去重，因为预测与 seed 无关）。"""
    seen = {}
    for seed in range(5):
        f = ROOT / "outputs" / "multiseed_per_dataset" / f"{ds}__seed{seed}.jsonl"
        if not f.exists():
            continue
        for line in f.open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                key = r["case_id"]
                if key not in seen:
                    seen[key] = {"case_id": key, "ophthalmic": r["a_name"],
                                 "systemic": r["b_name"], "gold": r["gold_risk"],
                                 "subset": r.get("subset")}
        break          # 一个 seed 即含全部案例
    return list(seen.values())


def build_prompts(kg: PreciseKG) -> dict:
    """构建三种方法的 prompt 模板（与原始评估一致）。"""
    from rank_bm25 import BM25Okapi
    chunks = [json.loads(l) for l in (ROOT / "data" / "seed" / "evidence_chunks.jsonl")
              .open(encoding="utf-8") if l.strip()]
    texts = [c.get("text", c.get("content", "")) for c in chunks]
    bm25 = BM25Okapi([t.lower().split() for t in texts])

    def naive(oph, sysd, k=3):
        q = f"{oph} {sysd} ophthalmic interaction"
        sc = bm25.get_scores(q.lower().split())
        top = sc.argsort()[-k:][::-1]
        return "\n\n".join(f"[{chunks[i].get('doc_id', i)}] {texts[i][:400]}" for i in top) or "No evidence."

    def make(oph, sysd, method):
        pair = f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)\nRisk level:"
        if method == "pure_llm":
            return pair
        if method == "naive_rag":
            return f"Evidence:\n{naive(oph, sysd)}\n\n{pair}"
        return f"Drug profiles:\n{kg.full_kg_context(oph, sysd)}\n\n{pair}"

    return make


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {}
    acc = sum(1 for r in rows if r["pred"] == r["gold"]) / n
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
    return {"n": n, "acc3": acc, "sens": sens, "spec": spec, "f1": f1,
            "kappa": (acc - pe) / (1 - pe) if pe < 1 else 0.0,
            "unknown": sum(1 for r in rows if r["pred"] == "unknown")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=0, help="仅对前 N 例做小规模验证")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / ("pilot_predictions.jsonl" if args.pilot else "predictions.jsonl")
    done = set()
    if pred_path.exists():                      # 续跑：跳过已完成的调用
        bad = 0
        for line in pred_path.open(encoding="utf-8"):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                done.add((r["dataset"], r["method"], r["case_id"], r["rep"]))
            except json.JSONDecodeError:
                # 进程被强杀时最后一行可能只写了一半；坏行忽略并重新调用
                bad += 1
        msg = f"续跑：已完成 {len(done)} 次调用"
        if bad:
            msg += f"（忽略 {bad} 行未写完的记录，将重新调用）"
        print(msg)

    kg = PreciseKG()
    make = build_prompts(kg)

    tasks = []
    for ds in DATASETS:
        cases = load_cases(ds)
        if args.pilot:
            cases = cases[:args.pilot]
        for c in cases:
            for m in METHODS:
                for rep in range(REPS):
                    if (ds, m, c["case_id"], rep) not in done:
                        tasks.append((ds, m, c, rep))

    print(f"数据集 {DATASETS}，方法 {len(METHODS)}，重复 {REPS} 次")
    print(f"待跑 {len(tasks)} 次调用；并发 {args.workers}")
    if not tasks:
        print("无待跑任务")
    est = len(tasks) * 14 / args.workers / 60
    print(f"预估耗时约 {est:.0f} 分钟\n")

    results = []
    t_start = time.time()
    with pred_path.open("a", encoding="utf-8") as fh, \
            ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {}
        for ds, m, c, rep in tasks:
            prompt = make(c["ophthalmic"], c["systemic"], m)
            futs[pool.submit(call, prompt)] = (ds, m, c, rep)
        n = 0
        for fut in as_completed(futs):
            ds, m, c, rep = futs[fut]
            try:
                raw, usage = fut.result()
                pred = parse(raw)
            except Exception as e:
                raw, usage, pred = f"ERROR: {type(e).__name__}", {}, "error"
            row = {"dataset": ds, "method": m, "case_id": c["case_id"],
                   "ophthalmic": c["ophthalmic"], "systemic": c["systemic"],
                   "gold": c["gold"], "rep": rep, "raw": raw[:200], "pred": pred,
                   "usage": usage, "model": MODEL, "max_tokens": MAX_TOKENS,
                   "temperature": TEMPERATURE}
            with _lock:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()                      # 立即落盘：强杀也不丢已完成的调用
                os.fsync(fh.fileno())
                results.append(row)
            n += 1
            if n % 25 == 0 or n == len(tasks):
                el = time.time() - t_start
                rate = n / el if el else 0
                left = (len(tasks) - n) / rate / 60 if rate else 0
                print(f"  {n}/{len(tasks)}  已用 {el/60:.0f} 分钟  剩余约 {left:.0f} 分钟",
                      flush=True)

    # ── 汇总（含已完成的旧记录）──
    all_rows = []
    for line in pred_path.open(encoding="utf-8"):
        if not line.strip():
            continue
        try:
            all_rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass                                 # 容忍未写完的尾行
    summary = {}
    for ds in DATASETS:
        summary[ds] = {}
        for m in METHODS:
            per_rep = []
            for rep in range(REPS):
                rs = [r for r in all_rows if r["dataset"] == ds and r["method"] == m
                      and r["rep"] == rep and r["pred"] not in ("error",)]
                if rs:
                    per_rep.append(metrics(rs))
            if not per_rep:
                continue
            # 多数票
            by_case = defaultdict(list)
            for r in all_rows:
                if r["dataset"] == ds and r["method"] == m and r["pred"] not in ("error",):
                    by_case[r["case_id"]].append(r)
            maj = []
            for cid, rs in by_case.items():
                votes = Counter(r["pred"] for r in rs if r["pred"] != "unknown")
                top = votes.most_common(1)
                maj.append({"gold": rs[0]["gold"], "pred": top[0][0] if top else "unknown"})
            summary[ds][m] = {
                "n_cases": len(by_case), "n_calls": sum(len(v) for v in by_case.values()),
                "per_rep": {k: (round(st_mean([p[k] for p in per_rep]), 4) if k != "unknown" else None)
                            for k in ["acc3", "sens", "spec", "f1", "kappa"]},
                "per_rep_sd": {k: round(st_pstdev([p[k] for p in per_rep]), 4)
                               for k in ["acc3", "sens", "spec", "f1", "kappa"]},
                "majority_vote": {k: round(v, 4) for k, v in metrics(maj).items()},
            }
    (OUT / ("pilot_metrics.json" if args.pilot else "metrics.json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\n完成 {n} 次调用；总记录 {len(all_rows)}")
    print(f"写出 -> {pred_path}")
    print(f"写出 -> {OUT / ('pilot_metrics.json' if args.pilot else 'metrics.json')}")
    return 0


def st_mean(v):
    return sum(v) / len(v) if v else 0.0


def st_pstdev(v):
    if len(v) < 2:
        return 0.0
    m = st_mean(v)
    return (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5


if __name__ == "__main__":
    raise SystemExit(main())
