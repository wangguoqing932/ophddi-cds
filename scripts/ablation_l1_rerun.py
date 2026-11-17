#!/usr/bin/env python3
"""ablation_l1_rerun.py — Unified 4-method evaluation on ALL 118 L1 cases.

Single script, single prompt version, same run — removes cross-script prompt drift
that affected the earlier merged L1 table (T1 rows came from a v1-era prompt).
full_system = deterministic v2 cascade (0 LLM calls). Others = 1 LLM call each, temperature 0.
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
kg = PreciseKG()

SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""

_chunks = []
for line in (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8"):
    if line.strip():
        _chunks.append(json.loads(line))
_texts = [c.get("text", c.get("content", "")) for c in _chunks]
_bm25 = BM25Okapi([t.lower().split() for t in _texts])


def bm25_ctx(oph, sysd, k=3):
    q = f"{oph} {sysd} ophthalmic interaction"
    scores = _bm25.get_scores(q.lower().split())
    top = scores.argsort()[-k:][::-1]
    return "\n\n".join(f"[{_chunks[i].get('doc_id', i)}] {_texts[i][:400]}" for i in top) or "No evidence."


def call(prompt):
    for a in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}],
                temperature=0, max_tokens=10)
            return r.choices[0].message.content.strip().lower()
        except Exception:
            if a < 2:
                time.sleep(2 ** (a + 1))
            else:
                return "error"


def parse(raw):
    t = raw.lower()
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unparseable"


def main():
    cases = json.load((ROOT / "outputs" / "blind_test" / "l1_independent.json").open(encoding="utf-8"))
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    records = []

    for c in cases:
        oph, sysd = c["ophthalmic_drug"], c["systemic_drug"]
        pair = f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)\nRisk level:"
        for m in methods:
            if m == "full_system":
                lvl, _, info = kg.deterministic_level_v2(oph, sysd)
                records.append({"case_id": c["case_id"], "method": m, "gold": c["gold"],
                                "predicted": lvl, "source": c["source"], "cascade": "deterministic"})
                continue
            if m == "pure_llm":
                prompt = pair
            elif m == "naive_rag":
                prompt = f"Evidence:\n{bm25_ctx(oph, sysd)}\n\n{pair}"
            else:
                prompt = f"Drug profiles:\n{kg.full_kg_context(oph, sysd)}\n\n{pair}"
            raw = call(prompt)
            records.append({"case_id": c["case_id"], "method": m, "gold": c["gold"],
                            "predicted": parse(raw), "source": c["source"], "raw": raw})
            time.sleep(0.15)

    out = ROOT / "output" / "ablation_l1_rerun.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"{'Method':<12s} {'Acc4':>6s} {'Sens':>6s} {'Spec':>6s}  n_correct/n")
    for m in methods:
        rs = [r for r in records if r["method"] == m and r["predicted"] not in (None, "unparseable")]
        tp = sum(1 for r in rs if r["gold"] == "high" and r["predicted"] == "high")
        fp = sum(1 for r in rs if r["gold"] != "high" and r["predicted"] == "high")
        fn = sum(1 for r in rs if r["gold"] == "high" and r["predicted"] != "high")
        tn = sum(1 for r in rs if r["gold"] != "high" and r["predicted"] != "high")
        acc = (tp + tn) / len(rs)
        sens = tp / (tp + fn) if tp + fn else 0
        spec = tn / (tn + fp) if tn + fp else 0
        print(f"{m:<12s} {acc:6.3f} {sens:6.3f} {spec:6.3f}  {tp + tn}/{len(rs)}")
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
