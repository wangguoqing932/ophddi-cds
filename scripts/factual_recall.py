#!/usr/bin/env python3
"""factual_recall.py — 40 questions × 4 methods: sync-only, no async LightRAG"""

import csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi

load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
SLEEP = 0.2

# ── Load questions ──
with open(ROOT / "data" / "factual_questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# ── Load evidence ──
chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))
texts = [c.get("text", c.get("content", "")) for c in chunks]
bm25 = BM25Okapi([t.lower().split() for t in texts])

# ── Load entity registry (structured knowledge = "graph") ──
entity_a = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        entity_a[row["primary_name"].lower()] = row

entity_b = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        entity_b[row["generic_name"].lower()] = row

# ── Load rules ──
import yaml
with open(ROOT / "configs" / "rules.yaml", encoding="utf-8") as f:
    rules_config = yaml.safe_load(f)

# ── Context builders ──
def get_entity_context(oph_name, sys_name):
    """Structured entity registry data — equivalent to graph/lightrag context."""
    lines = []
    oph = entity_a.get(oph_name.lower(), {})
    if oph:
        lines.append(f"Ophthalmic drug: {oph.get('primary_name','')} ({oph.get('category','')})")
        lines.append(f"  Flags: {oph.get('flags','')}")
        lines.append(f"  Mechanisms: {oph.get('active_mechanisms','')}")
        lines.append(f"  Route: {oph.get('route','')} {oph.get('ophthalmic_administration','')}")
    
    sys_ = entity_b.get(sys_name.lower(), {})
    if sys_:
        lines.append(f"Systemic drug: {sys_.get('generic_name','')} ({sys_.get('drug_class','')})")
        lines.append(f"  Flags: {sys_.get('flags','')}")
        lines.append(f"  Metabolic pathways: {sys_.get('metabolic_pathways','')}")
        lines.append(f"  Therapeutic index tier: {sys_.get('therapeutic_index_tier','')}")
    
    return "\n".join(lines) if lines else "No structured entity data found."

def get_rules_context(oph_name, sys_name):
    """Rules that may apply to this drug pair."""
    oph = entity_a.get(oph_name.lower(), {})
    sys_ = entity_b.get(sys_name.lower(), {})
    oph_flags = set((oph.get("flags", "")).split("|"))
    sys_flags = set((sys_.get("flags", "")).split("|"))
    
    relevant = []
    for rule in rules_config.get("rules", []):
        a_flags = set(rule.get("entity_a_flags", []))
        b_flags = set(rule.get("entity_b_flags", []))
        a_match = a_flags & oph_flags
        b_match = b_flags & sys_flags
        if a_match and b_match:
            relevant.append(
                f"[{rule['id']}] severity={rule['severity']}: {rule.get('rationale','')[:200]}"
            )
    
    if not relevant:
        return "No specific rules matched for this drug pair."
    return "Matched rules:\n" + "\n".join(relevant[:5])

def get_literature(oph, sys_d, q, top_k=3):
    query = f"{oph} {sys_d} " + " ".join(q.split()[:8])
    scores = bm25.get_scores(query.lower().split())
    top_idx = scores.argsort()[-top_k:][::-1]
    snips = []
    for i in top_idx:
        c = chunks[i]
        snips.append(f"[doc_{c.get('doc_id', i)}] {texts[i][:400]}")
    return "\n\n".join(snips) if snips else "No relevant evidence found."

# ── System prompt ──
SYSTEM = """You are a clinical pharmacology knowledge base. Answer factual questions about ophthalmic drug properties and interactions.

Rules:
1. Answer ONLY based on verifiable pharmacological facts
2. If you know a specific value (e.g., bioavailability %), state it precisely
3. If evidence is from a specific source, mention it
4. If uncertain, say "I cannot confirm this" — do NOT guess
5. For interaction questions: distinguish systemic-route vs ophthalmic-route applicability
6. 2-5 sentences. Be concise and factual.
7. NEVER fabricate numbers or citations"""

# ── Prompt builders ──
def build_prompt(method, q):
    oph = q.get("ophthalmic", "")
    sys_d = q.get("systemic", "")
    question = q["question"]

    if method == "pure_llm":
        return question

    elif method == "naive_rag":
        lit = get_literature(oph, sys_d, question)
        return f"Reference evidence:\n{lit}\n\n---\nQuestion: {question}"

    elif method == "lightrag":
        ent = get_entity_context(oph, sys_d)
        return f"Structured drug registry:\n{ent}\n\n---\nQuestion: {question}"

    elif method == "full_system":
        rules = get_rules_context(oph, sys_d)
        ent = get_entity_context(oph, sys_d)
        lit = get_literature(oph, sys_d, question)
        return (
            f"Matched rules:\n{rules}\n\n"
            f"Structured registry:\n{ent}\n\n"
            f"Evidence:\n{lit}\n\n"
            f"---\nQuestion: {question}"
        )
    return question

# ── API call ──
def call_llm(user_prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=250,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
            else:
                return f"ERROR: {e}"

# ── Score answer ──
def score_answer(q, answer):
    gold_keywords = q.get("gold_keywords", [])
    answer_lower = answer.lower()
    hits = 0
    matched = []
    
    for kw in gold_keywords:
        kw_lower = str(kw).lower().replace('_', ' ')
        if kw_lower in answer_lower:
            hits += 1
            matched.append(kw)
        elif any(part in answer_lower for part in kw_lower.split() if len(part) > 2):
            # Partial match for multi-word keywords
            parts = [p for p in kw_lower.split() if len(p) > 2]
            if parts and all(p in answer_lower for p in parts):
                hits += 1
                matched.append(kw)
    
    # Negative case scoring
    if q.get("requires_no_interaction"):
        no_int_markers = ['no interaction', 'no clinically significant', 'no known',
                         'not absorbed', 'negligible', 'no systemic', 'not apply',
                         'no documented', 'no pharmacological', 'cannot confirm',
                         'no evidence']
        correctly_negative = any(m in answer_lower for m in no_int_markers)
        interaction_words = ['interaction occurs', 'significant interaction', 'risk of',
                           'may interact', 'can interact', 'known to interact']
        fabricated_interaction = any(m in answer_lower for m in interaction_words)
        
        return {
            "score": 1.0 if (correctly_negative and not fabricated_interaction) else 0.0,
            "hits": hits,
            "total_keywords": len(gold_keywords),
            "matched": matched,
            "correct_negative": correctly_negative and not fabricated_interaction,
        }
    
    score = hits / max(len(gold_keywords), 1)
    has_source = bool(re.search(r'(FDA|DrugBank|PMID|Stockley|BNF|label|study|doi)', answer, re.I))
    
    return {
        "score": min(score, 1.0),
        "hits": hits,
        "total_keywords": len(gold_keywords),
        "matched": matched,
        "correct_negative": None,
        "has_source_citation": has_source,
    }

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    total = len(QUESTIONS) * len(methods)
    results = []
    count = 0

    print(f"Factual Recall: {len(QUESTIONS)} questions × {len(methods)} methods = {total} calls")
    print(f"Model: {MODEL}")
    print("-" * 60)

    for q in QUESTIONS:
        for method in methods:
            count += 1
            prompt = build_prompt(method, q)
            raw = call_llm(prompt)
            scoring = score_answer(q, raw)

            results.append({
                "question_id": q["id"],
                "case_id": q["case_id"],
                "category": q["category"],
                "method": method,
                "question": q["question"][:120],
                "gold_keywords": q.get("gold_keywords", []),
                "llm_answer": raw,
                "score": scoring["score"],
                "hits": scoring["hits"],
                "total_kw": scoring["total_keywords"],
                "correct_negative": scoring.get("correct_negative"),
                "has_citation": scoring.get("has_source_citation", False),
            })

            if count % 20 == 0 or count == total:
                print(f"  [{count:3d}/{total}] {count/total*100:.0f}%")

            time.sleep(SLEEP)

    # ── Save ──
    out_path = ROOT / "output" / "factual_recall_results.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── Summary ──
    print("\n" + "=" * 75)
    print("  FACTUAL RECALL RESULTS")
    print("=" * 75)

    for method in methods:
        mres = [r for r in results if r["method"] == method]
        n = len(mres)
        mean_score = sum(r["score"] for r in mres) / n
        perfect = sum(1 for r in mres if r["score"] >= 1.0)
        citations = sum(1 for r in mres if r.get("has_citation"))
        
        pk = [r for r in mres if r["category"] == "pharmacokinetics"]
        mech = [r for r in mres if r["category"] == "mechanism"]
        neg = [r for r in mres if r["category"] == "negative"]
        
        pk_score = sum(r["score"] for r in pk) / len(pk) if pk else 0
        mech_score = sum(r["score"] for r in mech) / len(mech) if mech else 0
        neg_correct = sum(1 for r in neg if r.get("correct_negative")) if neg else 0
        
        print(f"\n  {method}:")
        print(f"    Overall score:          {mean_score:.1%} ({perfect}/{n} perfect)")
        print(f"    PK absorption:          {pk_score:.1%}")
        print(f"    Mechanism recall:       {mech_score:.1%}")
        print(f"    Negatives correct:      {neg_correct}/{len(neg)}")
        print(f"    Source citations:       {citations}/{n}")

    # ── Delta ──
    pure_score = sum(r["score"] for r in results if r["method"] == "pure_llm") / 40
    print(f"\n  Gradient (Δ vs pure_llm = {pure_score:.3f}):")
    for method in ["naive_rag", "lightrag", "full_system"]:
        s = sum(r["score"] for r in results if r["method"] == method) / 40
        d = s - pure_score
        bar = "█" * max(0, int(d * 60)) if d > 0 else "░" * max(0, int(-d * 60))
        print(f"    {method:12s}: {s:.3f} (Δ {d:+.3f}) {bar}")

    print(f"\n  Results: {out_path}")

if __name__ == "__main__":
    main()
