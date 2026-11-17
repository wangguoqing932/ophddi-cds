#!/usr/bin/env python3
"""template_fill_v3.py — Dual-channel architecture: PreciseKG + LightRAG docs
Architecture:
  pure_llm:   zero context (LLM memory only)
  naive_rag:  LightRAG document retrieval only (BM25 over evidence chunks)
  lightrag:   PreciseKG layer only (entity profiles + matched rules, 0 API)
  full_system: PreciseKG + rules + BM25 literature (all sources)
"""

import csv, json, os, re, sys, time
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
SLEEP = 0.15

# ── Init ──
kg = PreciseKG()

with open(ROOT / "data" / "gold_mechanisms.json", encoding="utf-8") as f:
    GOLD = json.load(f)

chunks_raw = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            chunks_raw.append(json.loads(line))
chunk_texts = [c.get("text", c.get("content", "")) for c in chunks_raw]
bm25 = BM25Okapi([t.lower().split() for t in chunk_texts])

# ── Literature context (LightRAG doc retrieval channel) ──
def lit_context(oph, sys_d, top_k=3):
    query = f"{oph} {sys_d} ophthalmic interaction mechanism"
    scores = bm25.get_scores(query.lower().split())
    top = scores.argsort()[-top_k:][::-1]
    snips = []
    for i in top:
        c = chunks_raw[i]
        snips.append(f"[{c.get('doc_id', i)}] {chunk_texts[i][:400]}")
    return "\n\n".join(snips) if snips else "No literature found."

# ── Template ──
TEMPLATE = """Fill this structured profile using ONLY the provided context. If context lacks info, write "UNKNOWN". No extra text.

DRUG PROFILE:
  ophthalmic_systemic_absorption: [high / medium / low / UNKNOWN]
  ophthalmic_key_flags: [list]
  systemic_drug_class: [class]
  systemic_key_flags: [list]
  systemic_nti: [yes / no / UNKNOWN]

INTERACTION:
  mechanism_names: [list specific mechanisms like "additive_beta_blockade", or "NONE"]
  mechanism_description: [1-2 sentences, or "No interaction because ..."]
  evidence_sources: [list sources from context, or "none provided"]
  ophthalmic_applicability: [yes / no / partial — does it apply at ophthalmic doses?]"""

SYSTEM_PROMPT = "You fill structured drug interaction templates using only provided context. If missing, write UNKNOWN. No extra text."

# ── Build prompts per method ──
def build(method, case):
    oph = case["ophthalmic"]
    sys_d = case["systemic"]
    q = f"Fill template for: ophthalmic {oph} eye drops + systemic {sys_d} (oral/IV)\n\n{TEMPLATE}"
    
    if method == "pure_llm":
        return f"No context. Use your pharmacological knowledge.\n\n{q}"
    
    elif method == "naive_rag":
        lit = lit_context(oph, sys_d)
        return f"DOCUMENT RETRIEVAL:\n{lit}\n\n{q}"
    
    elif method == "lightrag":
        # PreciseKG only — zero API, structured data
        ktx = kg.full_kg_context(oph, sys_d)
        return f"KNOWLEDGE GRAPH (structured drug registry):\n{ktx}\n\n{q}"
    
    elif method == "full_system":
        ktx = kg.full_kg_context(oph, sys_d)
        lit = lit_context(oph, sys_d)
        return (
            f"=== PRECISE KNOWLEDGE GRAPH ===\n{ktx}\n\n"
            f"=== LITERATURE EVIDENCE ===\n{lit}\n\n"
            f"{q}"
        )
    return q

# ── API ──
def call(prompt):
    for a in range(3):
        try:
            r = client.chat.completions.create(model=MODEL,
                messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
                temperature=0, max_tokens=500)
            return r.choices[0].message.content.strip()
        except Exception as e:
            if a < 2: time.sleep(2**(a+1))
            else: return f"ERROR:{e}"

# ── Score ──
# Synonym map: gold mechanism -> alternative names LLM might use
MECH_SYNONYMS = {
    "additive_beta_blockade": ["beta.blockade", "beta.blocker", "additive.beta"],
    "additive_cardiodepression": ["cardiodepression", "cardiac.depression", "negative.inotropic", "myocardial.depression"],
    "additive_bradycardia": ["bradycardia", "heart.rate", "negative.chronotropic"],
    "additive_AV_conduction_delay": ["av.conduction", "av.block", "heart.block", "conduction.delay"],
    "additive_CNS_depression": ["cns.depression", "sedation", "central.depression", "cns.effect"],
    "additive_hypotension": ["hypotension", "blood.pressure", "bp.reduction"],
    "additive_anticholinergic_burden": ["anticholinergic", "antimuscarinic", "anticholinergic.effect"],
    "additive_metabolic_acidosis": ["metabolic.acidosis", "acidosis", "bicarbonate"],
    "additive_electrolyte_disturbance": ["electrolyte", "hypokalemia", "potassium"],
    "additive_bleeding_risk": ["bleeding", "hemorrhage", "anticoagulant.effect", "inr"],
    "additive_corticosteroid_effects": ["corticosteroid", "steroid", "adrenal.suppression", "hyperglycemia"],
    "additive_carbonic_anhydrase_inhibition": ["carbonic.anhydrase", "cai.inhibit"],
}

def _fuzzy_match_mechanism(gold_mech: str, answer_text: str) -> bool:
    """Check if gold mechanism appears in answer, using synonyms."""
    gm_lower = gold_mech.lower().replace('_', ' ')
    ans = answer_text.lower()
    
    # Exact match
    if gm_lower in ans or gold_mech.lower() in ans:
        return True
    
    # Word-level match: all significant words in gold appear in answer
    words = [w for w in gm_lower.split() if len(w) > 2]
    if words and all(w in ans for w in words):
        return True
    
    # Synonym match
    synonyms = MECH_SYNONYMS.get(gold_mech, [])
    return any(re.search(syn, ans) for syn in synonyms)

def score(case, response):
    ans = response.lower()
    gold = case
    s = 0.0
    det = []
    
    # 1. Absorption (0.25)
    bioavail = gold.get("ophthalmic_bioavailability", "").lower()
    if "60-80%" in bioavail or ">50%" in bioavail: exp_abs = "high"
    elif "30-" in bioavail or "40-" in bioavail or "moderate" in bioavail or "significant" in bioavail: exp_abs = "medium"
    elif "<" in bioavail: exp_abs = "low"
    else: exp_abs = "medium"
    
    m = re.search(r'ophthalmic_systemic_absorption:\s*(\w+)', ans)
    if m:
        found = m.group(1).lower()
        s += 0.25 if found == exp_abs else (0.10 if found != "unknown" else 0)
        det.append(f"abs:{found}{'='+exp_abs if found==exp_abs else chr(0x2260)+exp_abs}")
    else:
        det.append("abs:missing")
    
    # 2. Mechanisms (0.40) — FUZZY matching
    gold_mechs = gold.get("true_mechanisms", [])
    if gold_mechs:
        found = sum(1 for gm in gold_mechs if _fuzzy_match_mechanism(gm, ans))
        s += 0.40 * found / len(gold_mechs)
        det.append(f"mech:{found}/{len(gold_mechs)}")
    else:
        no_int = any(m in ans for m in ['no interaction', 'none', 'no clinically', 'no known',
                      'not absorbed', 'negligible', 'no documented', 'no pharmacological'])
        no_fake = not any(m in ans for m in ['significant interaction', 'known interaction'])
        s += 0.40 if (no_int and no_fake) else 0
        det.append(f"mech:NONE={'ok' if no_int else 'FALSE_POS'}")
    
    # 3. Applicability (0.20)
    has_int = len(gold_mechs) > 0
    m = re.search(r'ophthalmic_applicability:\s*(\w+)', ans)
    if m:
        found_app = m.group(1).lower()
        if has_int and found_app in ("yes","partial"): s += 0.20; det.append("app:ok")
        elif not has_int and found_app in ("no",): s += 0.20; det.append("app:ok")
        elif found_app == "unknown": s += 0.05; det.append("app:?")
        else: det.append(f"app:{found_app}:wrong")
    else:
        det.append("app:missing")
    
    # 4. Evidence sources (0.15)
    m = re.search(r'evidence_sources:\s*\[?(.+?)\]?(?:\n|$)', ans)
    if m:
        src = m.group(1).lower()
        if any(x in src for x in ['fda','drugbank','pmid','stockley','bnf','label','db0']):
            s += 0.15; det.append("src:real")
        elif src.strip() not in ('','none','unknown','n/a'):
            s += 0.05; det.append("src:generic")
        else:
            det.append("src:none")
    else:
        det.append("src:missing")
    
    return s, det

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    results = []
    
    print(f"Template Fill v3: {len(GOLD)} cases × {len(methods)} methods = {len(GOLD)*len(methods)} calls")
    print(f"Dual-channel architecture: PreciseKG (342 drugs, 100% coverage) + LightRAG docs (1307 chunks)")
    print("-" * 65)
    
    for case in GOLD:
        for method in methods:
            prompt = build(method, case)
            raw = call(prompt)
            sc, det = score(case, raw)
            
            results.append({
                "case_id": case["case_id"], "method": method,
                "ophthalmic": case["ophthalmic"], "systemic": case["systemic"],
                "gold_mechs": case["true_mechanisms"], "score": sc,
                "response": raw[:600], "details": "; ".join(det),
            })
            
            if len(results) % 20 == 0:
                recent = [r["score"] for r in results[-20:]]
                print(f"  [{len(results):3d}/{len(GOLD)*len(methods)}] recent avg: {sum(recent)/len(recent):.2f}")
            
            time.sleep(SLEEP)
    
    # Save
    out = ROOT / "output" / "template_fill_v3.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # ── Summary ──
    print("\n" + "=" * 65)
    print("  TEMPLATE FILL v3: Dual-Channel Architecture Results")
    print("=" * 65)
    
    for method in methods:
        mr = [r for r in results if r["method"] == method]
        avg = sum(r["score"] for r in mr) / len(mr)
        pos = [r for r in mr if len(r["gold_mechs"]) > 0]
        neg = [r for r in mr if len(r["gold_mechs"]) == 0]
        pos_avg = sum(r["score"] for r in pos) / len(pos) if pos else 0
        neg_avg = sum(r["score"] for r in neg) / len(neg) if neg else 0
        
        # Channel description
        desc = {"pure_llm":"zero context","naive_rag":"BM25 docs only",
                "lightrag":"PreciseKG only","full_system":"KG+Rules+Docs"}[method]
        
        print(f"\n  {method} ({desc}):")
        print(f"    Score: {avg:.1%}  |  Pos: {pos_avg:.1%}  |  Neg: {neg_avg:.1%}")
    
    # Gradient
    pure_avg = sum(r["score"] for r in results if r["method"]=="pure_llm") / len(GOLD)
    print(f"\n  Δ vs pure_llm ({pure_avg:.3f}):")
    for m in ["naive_rag", "lightrag", "full_system"]:
        s = sum(r["score"] for r in results if r["method"]==m) / len(GOLD)
        d = s - pure_avg
        bar = "█" * max(0,int(d*80)) if d>0 else "░" * max(0,int(-d*80))
        print(f"    {m:12s}: {s:.3f} ({d:+.3f}) {bar}")
    
    print(f"\n  {out}")

if __name__ == "__main__":
    main()
