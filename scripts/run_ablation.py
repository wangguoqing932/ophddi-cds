#!/usr/bin/env python3
"""run_ablation.py — 4 methods × 100 cases int-pubmed = 400 LLM calls"""

import asyncio, csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi

load_dotenv(ROOT / ".env")

# ── CONFIG ──
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
TEMPERATURE = 0
MAX_TOKENS = 10
SLEEP = 0.5
MAX_RETRIES = 3
SMOKE_N = 100
TOP_K = 3

# ── PATHS ──
CASES_PATH      = ROOT / "data" / "datasets" / "int-pubmed" / "cases.jsonl"
EVIDENCE_PATH   = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
RULE_RESULTS    = ROOT / "phase5_audit" / "phase5_v2_int_results.csv"
OUTPUT_PATH     = ROOT / "output" / "ablation_int_400.jsonl"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── CLIENT ──
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

# ── SYSTEM PROMPT ──
SYSTEM_PROMPT = """You are a clinical pharmacologist specializing in ophthalmic drug-drug interactions.

Assess the interaction risk level when an OPHTHALMIC drug (eye drops/ointment) is co-administered with a SYSTEMIC drug (oral/IV).

Key considerations:
- Ophthalmic drugs have lower systemic exposure than oral/IV, but some (dexamethasone, atropine, timolol) reach 30-100% systemic bioavailability
- Consider: interaction mechanism, ophthalmic drug bioavailability, systemic drug therapeutic index

Reply with EXACTLY ONE WORD: low, medium, or high
Do NOT explain. One word only."""

# ── LOADERS ──
def load_cases(n: int = 5):
    cases = []
    with open(CASES_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = json.loads(line)
                # Get drug names from entity CSV if not in case
                cases.append(c)
    return cases[:n]

def load_evidence():
    chunks = []
    with open(EVIDENCE_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    texts = [c.get("text", c.get("content", "")) for c in chunks]
    bm25 = BM25Okapi([t.lower().split() for t in texts])
    return chunks, texts, bm25

def load_rules():
    rules = {}
    with open(RULE_RESULTS, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rules[row["case_id"]] = row
    return rules

def load_entity_names():
    """Map entity_id → drug_name for both A and B"""
    names = {}
    for fname, id_col, name_col in [
        ("entities_a.csv", "topical_ophthalmic_medications_id", "primary_name"),
        ("entities_b.csv", "entity_b_id", "generic_name"),
    ]:
        with open(ROOT / "data" / "seed" / fname, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                names[row[id_col]] = row[name_col]
    return names

# ── CONTEXT BUILDERS ──
def get_literature_context(case, bm25, chunks, texts, top_k=TOP_K):
    drug_a = case.get("ophthalmic_drug", "") or entity_names.get(case["entity_a_id"], "")
    drug_b = case.get("systemic_drug", "") or entity_names.get(case["entity_b_id"], "")
    query = f"{drug_a} {drug_b} interaction ophthalmic"
    scores = bm25.get_scores(query.lower().split())
    top_idx = scores.argsort()[-top_k:][::-1]
    snippets = []
    for i in top_idx:
        c = chunks[i]
        snippets.append(f"[{c.get('doc_id', i)}] {texts[i][:400]}")
    return "\n".join(snippets) if snippets else "No relevant literature found."

def get_lightrag_context(case):
    """Query LightRAG index synchronously via asyncio.run."""
    drug_a = case.get("ophthalmic_drug", "") or entity_names.get(case["entity_a_id"], "")
    drug_b = case.get("systemic_drug", "") or entity_names.get(case["entity_b_id"], "")
    query = f"Is there a clinically significant drug interaction between ophthalmic {drug_a} eye drops and systemic {drug_b}? Consider ophthalmic systemic absorption and mechanism."
    try:
        from ophthalmic_ddi_cds_agent.lightrag_adapter import LightRAGAdapter
        async def _q():
            adapter = LightRAGAdapter()
            return await adapter.query(query, mode="hybrid")
        return asyncio.run(_q())
    except Exception as e:
        return f"[LightRAG unavailable: {e}]"

# ── PROMPT BUILDER ──
def build_prompt(method, case, bm25, chunks, texts, rules):
    drug_a = case.get("ophthalmic_drug", "") or entity_names.get(case["entity_a_id"], "")
    drug_b = case.get("systemic_drug", "") or entity_names.get(case["entity_b_id"], "")
    pair_line = f"Drug pair:\n- Ophthalmic: {drug_a} (eye drops)\n- Systemic: {drug_b} (oral/IV)\n\nRisk level:"

    if method == "pure_llm":
        return pair_line

    elif method == "naive_rag":
        lit = get_literature_context(case, bm25, chunks, texts)
        return f"Relevant literature:\n{lit}\n\n---\n\n{pair_line}"

    elif method == "lightrag":
        lrag = get_lightrag_context(case)
        return f"Knowledge graph context:\n{lrag}\n\n---\n\n{pair_line}"

    elif method == "full_system":
        rule = rules.get(case["case_id"], {})
        lrag = get_lightrag_context(case)
        lit = get_literature_context(case, bm25, chunks, texts)
        return (
            f"Reference rule engine output: {rule.get('system_level', 'N/A')} "
            f"(rule: {rule.get('matched_rules', 'N/A')}). "
            f"You may override if evidence strongly supports a different level.\n\n"
            f"Knowledge graph context:\n{lrag}\n\n"
            f"Relevant literature:\n{lit}\n\n"
            f"---\n\n{pair_line}"
        )
    return pair_line

# ── API CALL ──
def call_llm(user_prompt):
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Retry {attempt+1} in {wait}s: {e}")
                time.sleep(wait)
            else:
                return f"ERROR: {e}"

# ── PARSE ──
def parse_level(text):
    t = text.lower().strip()
    if t.startswith("error"): return "error"
    if re.search(r"\bhigh\b", t): return "high"
    if re.search(r"\bmedium\b|\bmoderate\b", t): return "medium"
    if re.search(r"\blow\b|\bminimal\b|\bnegligible\b|\bnone\b", t): return "low"
    return "unparseable"

# ── MAIN ──
def main():
    global entity_names
    entity_names = load_entity_names()

    cases = load_cases(SMOKE_N)
    chunks, texts, bm25 = load_evidence()
    rules = load_rules()
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]

    total = len(cases) * len(methods)
    results = []
    count = 0

    print(f"Ablation run: {len(cases)} cases × {len(methods)} methods = {total} calls")
    print(f"Model: {MODEL}, Temp: {TEMPERATURE}, Sleep: {SLEEP}s")
    print("-" * 50)

    for case in cases:
        # Resolve drug names
        case["ophthalmic_drug"] = entity_names.get(case["entity_a_id"], case["entity_a_id"])
        case["systemic_drug"]   = entity_names.get(case["entity_b_id"], case["entity_b_id"])

        for method in methods:
            count += 1
            prompt = build_prompt(method, case, bm25, chunks, texts, rules)
            raw = call_llm(prompt)
            parsed = parse_level(raw)

            results.append({
                "case_id": case["case_id"],
                "method": method,
                "ophthalmic_drug": case["ophthalmic_drug"],
                "systemic_drug": case["systemic_drug"],
                "raw_output": raw,
                "parsed_level": parsed,
            })

            marker = ""
            if parsed == "unparseable": marker = " ⚠️"
            elif parsed == "error": marker = " ❌"
            if count % 20 == 0 or count == total or parsed in ("unparseable","error"):
                print(f"  [{count}/{total}] {case['case_id']} | {method:12s} → {parsed}{marker}")

            time.sleep(SLEEP)

    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary
    print("\n" + "=" * 50)
    print("  SMOKE TEST SUMMARY" if SMOKE_N <= 5 else "  FULL RUN SUMMARY")
    print("=" * 50)
    for method in methods:
        sub = [r for r in results if r["method"] == method]
        levels = [r["parsed_level"] for r in sub]
        ok = sum(1 for l in levels if l in ("low", "medium", "high"))
        unparsed = sum(1 for l in levels if l not in ("low", "medium", "high"))
        print(f"  {method:12s}: {ok}/{len(sub)} parsed  "
              f"L={levels.count('low')} M={levels.count('medium')} H={levels.count('high')}"
              + (f"  ⚠️{unparsed} unparseable" if unparsed else ""))

    print(f"\nSaved: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
