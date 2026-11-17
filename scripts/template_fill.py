#!/usr/bin/env python3
"""template_fill.py — each method fills a structured template; score completeness vs gold"""

import csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
SLEEP = 0.15

# ── Load gold mechanisms (20 cases with ground truth) ──
with open(ROOT / "data" / "gold_mechanisms.json", encoding="utf-8") as f:
    GOLD = json.load(f)

# ── Load evidence base ──
chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))
texts = [c.get("text", c.get("content", "")) for c in chunks]
bm25 = BM25Okapi([t.lower().split() for t in texts])

# ── Load entity registry ──
a_by_name = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        a_by_name[row["primary_name"].lower()] = row
b_by_name = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        b_by_name[row["generic_name"].lower()] = row

# ── Load rules ──
import yaml
with open(ROOT / "configs" / "rules.yaml", encoding="utf-8") as f:
    rules_config = yaml.safe_load(f)

# ── Template ──
TEMPLATE = """Fill in this structured profile for the drug pair. Use ONLY the provided context. If context lacks information, write "UNKNOWN".

DRUG PROFILE:
  ophthalmic_systemic_absorption: [high/medium/low/UNKNOWN]
  ophthalmic_key_flags: [list relevant flags from context]
  systemic_drug_class: [class name]
  systemic_key_flags: [list relevant flags from context]

INTERACTION ASSESSMENT:
  mechanism_names: [list specific mechanism names, or "NONE" if no interaction]
  mechanism_description: [1-2 sentence description, or "No interaction" with reason]
  evidence_sources: [list specific sources cited in context]
  ophthalmic_applicability: [yes/no/partial — does the interaction apply at ophthalmic doses?]

Reply with ONLY the filled template, no extra text."""

# ── Context builders ──
def entity_context(oph, sys_d):
    o = a_by_name.get(oph.lower(), {})
    s = b_by_name.get(sys_d.lower(), {})
    lines = []
    if o:
        lines.append(f"ENTITY A (ophthalmic): {o.get('primary_name','')} | class={o.get('category','')} | flags={o.get('flags','')} | mechanisms={o.get('active_mechanisms','')}")
    if s:
        lines.append(f"ENTITY B (systemic): {s.get('generic_name','')} | class={s.get('drug_class','')} | flags={s.get('flags','')} | pathways={s.get('metabolic_pathways','')} | TI={s.get('therapeutic_index_tier','')}")
    return "\n".join(lines)

def rule_context(oph, sys_d):
    o = a_by_name.get(oph.lower(), {})
    s = b_by_name.get(sys_d.lower(), {})
    of = set((o.get("flags","")).split("|"))
    sf = set((s.get("flags","")).split("|"))
    matched = []
    for rule in rules_config.get("rules", []):
        if (set(rule.get("entity_a_flags",[])) & of) and (set(rule.get("entity_b_flags",[])) & sf):
            matched.append(f"[{rule['id']}] {rule['severity']}: {rule.get('rationale','')[:200]}")
    return "\n".join(matched[:6]) if matched else "No matching rules."

def lit_context(oph, sys_d):
    query = f"{oph} {sys_d} ophthalmic interaction"
    scores = bm25.get_scores(query.lower().split())
    top = scores.argsort()[-3:][::-1]
    snips = []
    for i in top:
        c = chunks[i]
        snips.append(f"[{c.get('doc_id',i)}] {texts[i][:400]}")
    return "\n\n".join(snips) if snips else "No evidence."

# ── Prompt ──
SYSTEM_PROMPT = "You fill structured drug interaction templates. Use ONLY provided context. If missing, write UNKNOWN. No extra text."

def build_prompt(method, case):
    oph, sys_d = case["ophthalmic"], case["systemic"]
    ctx = ""
    if method == "pure_llm":
        ctx = "No context provided. Use your pharmacological knowledge."
    elif method == "naive_rag":
        ctx = "CONTEXT (literature):\n" + lit_context(oph, sys_d)
    elif method == "lightrag":
        ctx = "CONTEXT (drug registry):\n" + entity_context(oph, sys_d)
    elif method == "full_system":
        ctx = ("CONTEXT:\n=== Rules ===\n" + rule_context(oph, sys_d) + 
               "\n\n=== Registry ===\n" + entity_context(oph, sys_d) +
               "\n\n=== Literature ===\n" + lit_context(oph, sys_d))
    
    return (f"{ctx}\n\nTASK: Fill template for: ophthalmic {oph} + systemic {sys_d}\n\n{TEMPLATE}")

# ── API ──
def call(prompt):
    for a in range(3):
        try:
            r = client.chat.completions.create(model=MODEL,
                messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
                temperature=0, max_tokens=300)
            return r.choices[0].message.content.strip()
        except Exception as e:
            if a < 2: time.sleep(2**(a+1))
            else: return f"ERROR:{e}"

# ── Score template fill ──
def score_template(case, response):
    """Score how well the filled template matches gold."""
    ans = response.lower()
    gold = case
    score = 0.0
    details = []
    
    # 1. Absorption level match (weight: 0.25)
    bioavail = gold.get("ophthalmic_bioavailability", "").lower()
    if "60-80%" in bioavail or ">50%" in bioavail or "high" in bioavail:
        expected_abs = "high"
    elif "30-" in bioavail or "40-" in bioavail or "moderate" in bioavail.lower():
        expected_abs = "medium"
    elif "<" in bioavail and ("3%" in bioavail or "5%" in bioavail or "negligible" in bioavail or "undetectable" in bioavail or "low" in bioavail):
        expected_abs = "low"
    else:
        expected_abs = "medium"  # default
    
    # Check response for absorption level
    abs_match = re.search(r'ophthalmic_systemic_absorption:\s*(\w+)', ans)
    if abs_match:
        found = abs_match.group(1).lower()
        if found == expected_abs:
            score += 0.25
            details.append(f"abs:{found}=gold:{expected_abs} ✓")
        elif found != "unknown":
            score += 0.10  # partial credit for attempting
            details.append(f"abs:{found}≠gold:{expected_abs} △")
        else:
            details.append(f"abs:unknown ✗")
    else:
        details.append("abs:not_found ✗")
    
    # 2. Mechanism names match (weight: 0.40)
    gold_mechs = set(gold.get("true_mechanisms", []))
    if gold_mechs:
        # Extract mechanism names from response
        mech_section = re.search(r'mechanism_names:\s*\[?(.+?)\]?(?:\n|$)', ans)
        if mech_section:
            found_mechs_text = mech_section.group(1)
            found_mechs = set()
            for m in gold_mechs:
                m_lower = m.lower().replace('_', ' ')
                if m_lower in found_mechs_text.lower() or m.lower() in found_mechs_text.lower().replace(' ', '_'):
                    found_mechs.add(m)
            recall = len(found_mechs) / len(gold_mechs)
            score += 0.40 * recall
            details.append(f"mechs:{len(found_mechs)}/{len(gold_mechs)} recall={recall:.0%}")
        else:
            # Check if mechanism keywords appear anywhere in response
            found = 0
            for m in gold_mechs:
                m_lower = m.lower().replace('_', ' ')
                if m_lower in ans or m.lower() in ans:
                    found += 1
            recall = found / len(gold_mechs)
            score += 0.40 * recall
            details.append(f"mechs(scattered):{found}/{len(gold_mechs)}")
    else:
        # Gold says no interaction — check if response says NONE
        if re.search(r'mechanism_names:\s*(?:NONE|none|\[\])', ans) or 'no interaction' in ans:
            score += 0.40
            details.append("mechs:NONE ✓")
        else:
            # Penalize for fabricating mechanisms
            details.append("mechs:false_positive ✗")
    
    # 3. Ophthalmic applicability (weight: 0.20)
    gold_has_interaction = len(gold.get("true_mechanisms", [])) > 0
    app_match = re.search(r'ophthalmic_applicability:\s*(\w+)', ans)
    if app_match:
        found_app = app_match.group(1).lower()
        if gold_has_interaction and found_app in ("yes", "partial"):
            score += 0.20
            details.append(f"app:{found_app}=yes ✓")
        elif not gold_has_interaction and found_app in ("no",):
            score += 0.20
            details.append(f"app:{found_app}=no ✓")
        elif found_app == "unknown":
            score += 0.05
            details.append(f"app:unknown △")
        else:
            details.append(f"app:{found_app} wrong ✗")
    else:
        details.append("app:not_found ✗")
    
    # 4. Evidence sources (weight: 0.15)
    src_match = re.search(r'evidence_sources:\s*\[?(.+?)\]?(?:\n|$)', ans)
    has_real_source = False
    if src_match:
        src_text = src_match.group(1).lower()
        if any(s in src_text for s in ['fda', 'drugbank', 'pmid', 'stockley', 'bnf', 'label', 'db0']):
            score += 0.15
            has_real_source = True
            details.append("src:real ✓")
        elif src_text.strip() and src_text.strip() not in ('none', 'unknown', 'n/a', ''):
            score += 0.05
            details.append("src:generic △")
        else:
            details.append("src:none ✗")
    else:
        details.append("src:not_found ✗")
    
    return score, details

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    total = len(GOLD) * len(methods)
    results = []
    
    print(f"Template Fill: {len(GOLD)} cases × {len(methods)} methods = {total} calls\n")
    
    for case in GOLD:
        for method in methods:
            prompt = build_prompt(method, case)
            raw = call(prompt)
            sc, details = score_template(case, raw)
            
            results.append({
                "case_id": case["case_id"],
                "method": method,
                "ophthalmic": case["ophthalmic"],
                "systemic": case["systemic"],
                "gold_mechs": case["true_mechanisms"],
                "response": raw,
                "score": sc,
                "details": "; ".join(details),
            })
            
            if len(results) % 20 == 0:
                avg = sum(r["score"] for r in results[-20:]) / 20
                print(f"  [{len(results):3d}/{total}] recent avg: {avg:.2f}")
            
            time.sleep(SLEEP)
    
    # Save
    out = ROOT / "output" / "template_fill_results.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEMPLATE FILL RESULTS (20 cases)")
    print("=" * 70)
    
    for method in methods:
        mr = [r for r in results if r["method"] == method]
        avg = sum(r["score"] for r in mr) / len(mr)
        pos = [r for r in mr if len(r["gold_mechs"]) > 0]  # has real mechanisms
        neg = [r for r in mr if len(r["gold_mechs"]) == 0]  # no interaction
        pos_avg = sum(r["score"] for r in pos) / len(pos) if pos else 0
        neg_avg = sum(r["score"] for r in neg) / len(neg) if neg else 0
        
        print(f"\n  {method}:")
        print(f"    Overall:   {avg:.2%}")
        print(f"    Pos cases: {pos_avg:.2%} (n={len(pos)})")
        print(f"    Neg cases: {neg_avg:.2%} (n={len(neg)})")
    
    # Gradient
    pure_avg = sum(r["score"] for r in results if r["method"]=="pure_llm") / 20
    print(f"\n  Δ vs pure_llm ({pure_avg:.3f}):")
    for m in ["naive_rag", "lightrag", "full_system"]:
        s = sum(r["score"] for r in results if r["method"]==m) / 20
        d = s - pure_avg
        bar = "█" * max(0,int(d*100)) if d>0 else ("░" * max(0,int(-d*100)))
        print(f"    {m:12s}: {s:.3f} ({d:+.3f}) {bar}")
    
    print(f"\n  {out}")

if __name__ == "__main__":
    main()
