# -*- coding: utf-8 -*-
"""naive_rag_leakage_audit.py — 量化 naive_rag 在审计集上的金标准泄漏。

背景（审稿人 2 的发现）：1,307 个证据块中有 500 个是 DDInter 2.0 的严重度陈述。
审计集的 gold 有 62 例保留 DDInter 原值，因此 BM25 若把该配对自身的 DDInter 陈述
检索进 top-3，naive_rag 相当于读到了答案。这直接影响"某基线在审计集上超过本系统"
这一比较的可信度。

做法：用与沉积实现完全相同的 BM25 参数（k1=1.5, b=0.75, top-3）与相同的查询串
（"<眼科药> <全身药> ophthalmic interaction"），判断 top-3 中是否存在**该配对自身**
的 DDInter 块（按 entities_a / entities_b 的注册表 ID 精确匹配，而非仅凭药名字符串）。

用法:
    python scripts/naive_rag_leakage_audit.py [--k 3]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

K1, B = 1.5, 0.75


def load_chunks() -> list:
    for c in (ROOT / "data" / "seed" / "evidence_chunks.jsonl",
              ROOT / "data" / "evidence" / "evidence_chunks.jsonl"):
        if c.exists():
            return [json.loads(l) for l in c.open(encoding="utf-8") if l.strip()]
    raise FileNotFoundError("evidence_chunks.jsonl")


def load_design() -> list:
    for c in (ROOT / "outputs" / "blind_test" / "blind_set_v3_ddinter.json",
              ROOT / "data" / "gold" / "audit_set_design.json"):
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    raise FileNotFoundError("blind_set_v3_ddinter.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3, help="检索返回的块数（默认 3）")
    args = ap.parse_args()

    kg = PreciseKG()
    chunks = load_chunks()
    design = load_design()
    ddi_idx = [i for i, c in enumerate(chunks) if c.get("source") == "DDInter 2.0"]
    print(f"证据块总数        : {len(chunks)}")
    print(f"其中 DDInter 2.0  : {len(ddi_idx)}")
    print(f"审计集案例        : {len(design)}")

    docs = [(c.get("text") or c.get("claim_text") or "").lower().split() for c in chunks]
    n = len(docs)
    avgdl = sum(len(d) for d in docs) / n
    df: collections.Counter = collections.Counter()
    for d in docs:
        for w in set(d):
            df[w] += 1
    tfs = [collections.Counter(d) for d in docs]
    dls = [len(d) for d in docs]

    # 只算查询词涉及的列：全量 1,307 块 × 每查询几十个 idf 是主要开销来源，
    # 这里预先把每个词的后验权重做成增量，避免逐块重复 Counter 构造。
    def scores(query: list) -> list:
        out = [0.0] * n
        for w in set(query):
            if w not in df:
                continue
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            for i, tf in enumerate(tfs):
                f = tf.get(w)
                if not f:
                    continue
                out[i] += idf * f * (K1 + 1) / (f + K1 * (1 - B + B * dls[i] / avgdl))
        return out

    def ent_ids(name: str, side: str) -> str | None:
        e = kg.get_ophthalmic(name) if side == "a" else kg.get_systemic(name)
        return e.get("id") if e else None

    kept = [d for d in design if d["ddinter_level"] == d["proposed_gold"]]
    corrected = [d for d in design if d["ddinter_level"] != d["proposed_gold"]]

    def audit(subset: list, label: str) -> dict:
        hits = []
        for d in subset:
            a, b = d["ophthalmic_drug"], d["systemic_drug"]
            ea, eb = ent_ids(a, "a"), ent_ids(b, "b")
            q = f"{a} {b} ophthalmic interaction".lower().split()
            top = sorted(range(n), key=lambda i: -scores(q)[i])[:args.k]
            for i in top:
                c = chunks[i]
                if c.get("source") != "DDInter 2.0":
                    continue
                if ea in (c.get("entities_a") or []) and eb in (c.get("entities_b") or []):
                    hits.append(d["case_id"])
                    break
        r = {"subset": label, "n": len(subset), "leaked": len(hits),
             "rate": len(hits) / len(subset) if subset else 0, "cases": hits}
        print(f"  {label:34s} {len(hits):3d}/{len(subset):3d} "
              f"({r['rate']*100:.1f}%)")
        return r

    print(f"\n=== BM25 top-{args.k} 检索到该配对自身 DDInter 陈述的比例 ===")
    res = {"k": args.k, "n_chunks": len(chunks), "n_ddinter_chunks": len(ddi_idx),
           "k1": K1, "b": B,
           "subsets": [audit(kept, "kept at DDInter severity (gold source)"),
                       audit(corrected, "absorption-corrected (gold is low)"),
                       audit(design, "all audit cases")]}
    print(f"\n  解读：kept 子集的 gold 就是 DDInter 原值；凡命中者，naive_rag 的检索内容")
    print(f"  直接包含该配对的答案，因此其在 kept 子集上的表现不能作为独立证据。")

    out = ROOT / "outputs" / "recomputed" / "naive_rag_leakage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已写出 -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
