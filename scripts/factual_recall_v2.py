#!/usr/bin/env python3
"""factual_recall_v2.py — improved retrieval, focused rules, better scoring"""

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
SLEEP = 0.15

# ── Load ──
with open(ROOT / "data" / "factual_questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))
texts = [c.get("text", c.get("content", "")) for c in chunks]
bm25 = BM25Okapi([t.lower().split() for t in texts])

entity_a = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        entity_a[row["primary_name"].lower()] = row
entity_b = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        entity_b[row["generic_name"].lower()] = row

import yaml
with open(ROOT / "configs" / "rules.yaml", encoding="utf-8") as f:
    rules_config = yaml.safe_load(f)

# ── Improved context builders ──

def get_entity_context(oph_name, sys_name):
    """Structured entity registry data — the 'graph/lightrag' context."""
    lines = []
    oph = entity_a.get(oph_name.lower(), {})
    if oph:
        flags = oph.get('flags', '')
        lines.append(f"[{oph.get('primary_name','')}] class={oph.get('category','')}")
        lines.append(f"  flags: {flags}")
        lines.append(f"  mechanisms: {oph.get('active_mechanisms','')}")
        # Extract key PK info from flags
        for f in flags.split('|'):
            f = f.strip()
            if 'absorption' in f:
                level = f.replace('systemic_absorption_', '')
                pct = {'high': '>50%', 'medium': '10-50%', 'low': '<10%'}.get(level, 'unknown')
                lines.append(f"  systemic_absorption_from_eye_drops: {level} ({pct} bioavailability)")
    
    sys_ = entity_b.get(sys_name.lower(), {})
    if sys_:
        flags = sys_.get('flags', '')
        lines.append(f"[{sys_.get('generic_name','')}] class={sys_.get('drug_class','')}")
        lines.append(f"  flags: {flags}")
        lines.append(f"  pathways: {sys_.get('metabolic_pathways','')}")
        lines.append(f"  TI tier: {sys_.get('therapeutic_index_tier','')}")
        if 'narrow_therapeutic_index' in flags:
            lines.append(f"  ⚠️ NARROW THERAPEUTIC INDEX drug")
    
    return "\n".join(lines) if lines else ""

def get_focused_rules(oph_name, sys_name):
    """Only rules whose flags ACTUALLY match this drug pair."""
    oph = entity_a.get(oph_name.lower(), {})
    sys_ = entity_b.get(sys_name.lower(), {})
    oph_flags = set((oph.get("flags", "")).split("|"))
    sys_flags = set((sys_.get("flags", "")).split("|"))
    
    matched = []
    for rule in rules_config.get("rules", []):
        a_f = set(rule.get("entity_a_flags", []))
        b_f = set(rule.get("entity_b_flags", []))
        a_overlap = a_f & oph_flags
        b_overlap = b_f & sys_flags
        if a_overlap and b_overlap:
            matched.append(
                f"  [{rule['id']}] {rule['severity']}: {rule.get('rationale','')[:150]}"
            )
    
    if not matched:
        return "No specific interaction rules matched."
    return "Interaction rules triggered:\n" + "\n".join(matched[:5])

def get_smart_literature(oph_name, sys_name, question, top_k=3):
    """Query using drug names + key pharmacological terms, not the whole question."""
    oph = entity_a.get(oph_name.lower(), {})
    sys_ = entity_b.get(sys_name.lower(), {})
    
    # Build query from entity flags (pharmacologically relevant terms)
    terms = [oph_name, sys_name]
    
    # Add key flags as search terms
    oph_flags = (oph.get('flags', '')).replace('|', ' ').replace('_', ' ')
    sys_flags = (sys_.get('flags', '')).replace('|', ' ').replace('_', ' ')
    
    # Categorize question and add relevant terms
    q_lower = question.lower()
    if 'absorption' in q_lower or 'bioavailability' in q_lower:
        terms.extend(['systemic absorption', 'bioavailability', 'ophthalmic', 'plasma'])
    elif 'mechanism' in q_lower or 'interaction' in q_lower:
        terms.extend(['interaction', 'ophthalmic', 'drug interaction'])
    else:
        terms.extend(['ophthalmic', 'interaction'])
    
    # Add entity class terms
    if oph.get('category'):
        terms.append(oph['category'].replace('_', ' '))
    if sys_.get('drug_class'):
        terms.append(sys_['drug_class'].replace('_', ' '))
    
    query = ' '.join(terms)
    scores = bm25.get_scores(query.lower().split())
    top_idx = scores.argsort()[-top_k:][::-1]
    
    snips = []
    for i in top_idx:
        c = chunks[i]
        text = texts[i][:400]
        # Only include if text contains one of the drug names or is clearly relevant
        if oph_name.lower() in text.lower() or sys_name.lower() in text.lower() or 'ophthalmic' in text.lower():
            snips.append(f"[{c.get('doc_id', i)}] {text}")
    
    return "\n\n".join(snips[:top_k]) if snips else "No relevant evidence found."

# ── System prompt ──
SYSTEM = """You are a precise clinical pharmacology reference. Answer factual questions about ophthalmic drugs.

Critical rules:
1. Use EXACT values when available from reference data — state numbers precisely
2. For ophthalmic drugs: distinguish systemic (oral/IV) route from topical (eye drop) route
3. Ophthalmic drug systemic absorption varies dramatically:
   - HIGH (>50%): timolol, atropine, dexamethasone, betaxolol
   - MEDIUM (10-50%): brimonidine, prednisolone, dorzolamide, brinzolamide, ketorolac
   - LOW (<10%): latanoprost, prostaglandin analogs, fluoroquinolones, antihistamines, most antibiotics
4. Cite source when available (DrugBank ID, FDA label, PMID)
5. 1-4 sentences. Be concise. If you don't know, say so — do NOT guess."""

# ── Prompt builder ──
def build_prompt(method, q):
    oph = q.get("ophthalmic", "")
    sys_d = q.get("systemic", "")
    question = q["question"]

    if method == "pure_llm":
        return question

    elif method == "naive_rag":
        lit = get_smart_literature(oph, sys_d, question)
        return f"Evidence snippets:\n{lit}\n\nQ: {question}"

    elif method == "lightrag":
        ent = get_entity_context(oph, sys_d)
        return f"Structured drug data:\n{ent}\n\nQ: {question}"

    elif method == "full_system":
        rules = get_focused_rules(oph, sys_d)
        ent = get_entity_context(oph, sys_d)
        lit = get_smart_literature(oph, sys_d, question)
        return (
            f"Rules triggered:\n{rules}\n\n"
            f"Drug data:\n{ent}\n\n"
            f"Evidence:\n{lit}\n\n"
            f"Q: {question}"
        )
    return question

# ── API ──
def call_llm(prompt, retries=3):
    for a in range(retries):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
                temperature=0, max_tokens=200,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            if a < retries - 1: time.sleep(2**(a+1))
            else: return f"ERROR:{e}"

# ── Scoring (improved) ──
def score_answer(q, answer):
    gold_kw = q.get("gold_keywords", [])
    ans = answer.lower()
    
    # Count keyword matches
    hits = 0
    matched = []
    for kw in gold_kw:
        kw_s = str(kw).lower().replace('_', ' ')
        if kw_s in ans:
            hits += 1
            matched.append(kw)
    
    # Negative case scoring
    if q.get("requires_no_interaction"):
        neg_ok = any(m in ans for m in [
            'no interaction', 'no clinically significant', 'no known',
            'not absorbed', 'negligible', 'no systemic', 'no documented',
            'no pharmacological', 'no evidence', 'cannot confirm',
            'does not apply', 'not applicable'
        ])
        # Check for hallucinated interaction
        false_pos = any(m in ans for m in [
            'significant interaction', 'known to interact', 'risk of interaction',
            'may interact', 'can interact', 'should be monitored'
        ])
        return {
            "score": 1.0 if (neg_ok and not false_pos) else (0.5 if neg_ok else 0.0),
            "hits": hits, "total": len(gold_kw), "matched": matched,
            "correct_negative": neg_ok and not false_pos,
        }
    
    # Factual scoring: keyword match + bonus for specificity
    kw_score = hits / max(len(gold_kw), 1)
    
    # Bonus: answer contains specific numbers or levels (not vague)
    has_specific = bool(re.search(r'\d+[-–]\d+%|\d+%|< \d+%|high|medium|low', ans))
    specificity_bonus = 0.15 if has_specific else 0.0
    
    # Source citation bonus
    has_source = bool(re.search(r'(FDA|DrugBank|PMID|Stockley|BNF|label|doi|DB\d+)', ans, re.I))
    source_bonus = 0.1 if has_source else 0.0
    
    final = min(kw_score + specificity_bonus + source_bonus, 1.0)
    
    return {
        "score": final,
        "kw_score": kw_score,
        "specificity": specificity_bonus,
        "source": source_bonus,
        "hits": hits, "total": len(gold_kw), "matched": matched,
        "correct_negative": None,
    }

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    total = len(QUESTIONS) * len(methods)
    results = []
    
    print(f"Factual Recall v2: {len(QUESTIONS)}q × {len(methods)}m = {total} calls\n")
    
    for i, q in enumerate(QUESTIONS):
        for method in methods:
            prompt = build_prompt(method, q)
            raw = call_llm(prompt)
            sc = score_answer(q, raw)
            
            results.append({
                "qid": q["id"], "cid": q["case_id"], "cat": q["category"],
                "method": method, "question": q["question"][:100],
                "answer": raw, "score": sc["score"],
                "kw_hits": sc["hits"], "kw_total": sc["total"],
                "correct_neg": sc.get("correct_negative"),
            })
            
            if len(results) % 40 == 0:
                print(f"  [{len(results):3d}/{total}] {len(results)/total*100:.0f}%")
            
            time.sleep(SLEEP)
    
    # Save
    out = ROOT / "output" / "factual_recall_v2.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # Summary
    print("\n" + "=" * 75)
    print("  FACTUAL RECALL v2 RESULTS")
    print("=" * 75)
    
    for method in methods:
        mr = [r for r in results if r["method"] == method]
        n = len(mr)
        avg = sum(r["score"] for r in mr) / n
        perfect = sum(1 for r in mr if r["score"] >= 0.95)
        
        pk = [r for r in mr if r["cat"] == "pharmacokinetics"]
        mech = [r for r in mr if r["cat"] == "mechanism"]
        neg = [r for r in mr if r["cat"] == "negative"]
        
        pk_s = sum(r["score"] for r in pk) / len(pk) if pk else 0
        mech_s = sum(r["score"] for r in mech) / len(mech) if mech else 0
        neg_c = sum(1 for r in neg if r.get("correct_neg")) if neg else 0
        
        # Source citation rate
        src = sum(1 for r in mr if bool(re.search(r'(FDA|DrugBank|PMID|Stockley|BNF|DB\d+)', 
                                                  r.get("answer",""), re.I)))
        
        print(f"\n  {method}:")
        print(f"    Score: {avg:.1%}  PK={pk_s:.1%}  Mech={mech_s:.1%}  Neg={neg_c}/{len(neg)}  Cite={src}/{n}")
    
    # Gradient
    pure_avg = sum(r["score"] for r in results if r["method"] == "pure_llm") / 40
    print(f"\n  Δ vs pure_llm ({pure_avg:.3f}):")
    for m in ["naive_rag", "lightrag", "full_system"]:
        s = sum(r["score"] for r in results if r["method"] == m) / 40
        d = s - pure_avg
        bar = "█" * max(0, int(d * 80)) if d > 0 else "░" * max(0, int(-d * 80))
        print(f"    {m:12s}: {s:.3f} (Δ {d:+.3f}) {bar}")
    
    print(f"\n  {out}")

if __name__ == "__main__":
    main()
