#!/usr/bin/env python3
"""ablation_blind.py — 4-method gradient on the two INDEPENDENT blind sets (40 cases).

Blind gold is fully independent of the rule engine / class matrix construction
(pharmacology-labelled, frozen before v2 evaluation, errata logged).
This is the cleanest method-comparison evidence for the paper.
"""
import json
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
client = OpenAI(api_key=__import__("os").getenv("DEEPSEEK_API_KEY"),
                base_url=__import__("os").getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = __import__("os").getenv("LLM_CHAT_MODEL", "deepseek-chat")
kg = PreciseKG()

# True naive RAG: BM25 keyword retrieval over raw evidence chunks (no structure)
_chunks = []
for line in (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8"):
    if line.strip():
        _chunks.append(json.loads(line))
_bm25_texts = [c.get("text", c.get("content", "")) for c in _chunks]
_bm25 = BM25Okapi([t.lower().split() for t in _bm25_texts])


def bm25_ctx(oph, sysd, k=3):
    q = f"{oph} {sysd} ophthalmic interaction"
    scores = _bm25.get_scores(q.lower().split())
    top = scores.argsort()[-k:][::-1]
    return "\n\n".join(f"[{_chunks[i].get('doc_id', i)}] {_bm25_texts[i][:400]}" for i in top) or "No evidence."

CASES = []
for f in ("blind_set_v2.json", "blind_set_v3.json"):
    for c in json.load((ROOT / "outputs" / "blind_test" / f).open(encoding="utf-8")):
        CASES.append(c)

SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""

SYSTEM_FULL = SYSTEM + """

You also have RULE ENGINE + DRUG PROFILES context. CRITICAL CONSTRAINT: If the context says "HARD CONSTRAINT: ... risk MUST be low", output "low". Reply with EXACTLY ONE WORD."""


def call(prompt, method):
    sys_p = SYSTEM_FULL if method == "full_system" else SYSTEM
    for a in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": sys_p},
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
    if "high" in t: return "high"
    if "medium" in t or "moderate" in t: return "medium"
    if "low" in t: return "low"
    return "unparseable"


def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    records = []
    for c in CASES:
        oph, sysd = c["ophthalmic_drug"], c["systemic_drug"]
        pair = f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)\nRisk level:"
        for m in methods:
            if m == "pure_llm":
                prompt = pair
            elif m == "naive_rag":
                prompt = f"Evidence:\n{bm25_ctx(oph, sysd)}\n\n{pair}"
            elif m == "lightrag":
                prompt = f"Drug profiles:\n{kg.full_kg_context(oph, sysd)}\n\n{pair}"
            else:
                lvl, _, _ = kg.deterministic_level_v2(oph, sysd)
                if lvl is not None:
                    records.append({"case_id": c["case_id"], "method": m,
                                    "gold": c["proposed_gold"], "predicted": lvl,
                                    "cascade": "deterministic"})
                    continue
                prompt = f"=== DRUG PROFILES ===\n{kg.full_kg_context(oph, sysd)}\n\n{pair}"
            raw = call(prompt, m)
            records.append({"case_id": c["case_id"], "method": m,
                            "gold": c["proposed_gold"], "predicted": parse(raw), "raw": raw})
            time.sleep(0.15)

    out = ROOT / "output" / "ablation_blind40.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    from collections import Counter
    print(f"{'Method':<12s} {'Acc4':>6s} {'Sens':>6s} {'Spec':>6s}")
    for m in methods:
        rs = [r for r in records if r["method"] == m]
        acc = sum(1 for r in rs if r["gold"] == r["predicted"]) / len(rs)
        hs = [r for r in rs if r["gold"] == "high"]
        sens = sum(1 for r in hs if r["predicted"] == "high") / len(hs) if hs else 0
        ls = [r for r in rs if r["gold"] != "high"]
        spec = sum(1 for r in ls if r["predicted"] != "high") / len(ls) if ls else 0
        print(f"{m:<12s} {acc:6.3f} {sens:6.3f} {spec:6.3f}")
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
