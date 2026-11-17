#!/usr/bin/env python3
"""ablation_classify.py — Direct risk level classification, 4 methods, skill metrics

Retrieval channels:
  - naive_rag : BM25 keyword retrieval over raw evidence chunks (1307)
  - full_system: LightRAG dense retrieval over vectorized chunks (513, 2048-dim)
                 with both-drug co-mention filter
"""

import asyncio, base64, csv, json, os, re, sys, time, zlib
from pathlib import Path
from collections import Counter

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from ophthalmic_ddi_cds_agent.embeddings import EmbeddingSettings, doubao_embed
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
SLEEP = 0.15

kg = PreciseKG()

# Load consensus validation (tiered gold)
val_path = ROOT / "data" / "datasets" / "consensus_validation" / "cases.jsonl"
GOLD = []
with open(val_path, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            g = json.loads(line)
            g.setdefault("ophthalmic", g.get("ophthalmic_drug", ""))
            g.setdefault("systemic", g.get("systemic_drug", ""))
            g.setdefault("ddinter_level", g.get("gold_risk_level", "unknown"))
            GOLD.append(g)
seen = set(); unique = []
for g in GOLD:
    p = (g["ophthalmic"].lower(), g["systemic"].lower())
    if p not in seen: seen.add(p); unique.append(g)
GOLD = unique
print(f"Loaded {len(GOLD)} external validation cases (PubMed/Cochrane/ClinicalTrials)")

chunks_raw = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip(): chunks_raw.append(json.loads(line))
chunk_texts = [c.get("text", c.get("content", "")) for c in chunks_raw]
bm25 = BM25Okapi([t.lower().split() for t in chunk_texts])

# ── Context builders ──
def bm25_lit_ctx(oph, sys_d, k=3):
    """BM25 retrieval with both-drug filter: only chunks mentioning BOTH drugs."""
    q = f"{oph} {sys_d} ophthalmic interaction"
    scores = bm25.get_scores(q.lower().split())
    # Search wider, then filter for chunks mentioning both drugs
    top = scores.argsort()[-30:][::-1]
    filtered = [i for i in top 
                if oph.lower() in chunk_texts[i].lower() 
                and sys_d.lower() in chunk_texts[i].lower()]
    selected = filtered[:k] if filtered else top[:k]
    return "\n\n".join([f"[{chunks_raw[i].get('doc_id',i)}] {chunk_texts[i][:400]}" for i in selected]) or "No evidence."

class DenseRetriever:
    """LightRAG dense retrieval over vdb_chunks.json (513 chunks, 2048-dim matrix)."""
    def __init__(self, vdb_path=None):
        vdb_path = vdb_path or ROOT / "data" / "processed" / "lightrag_index" / "vdb_chunks.json"
        with open(vdb_path, encoding="utf-8") as f:
            vdb = json.load(f)
        self.chunks = vdb["data"]
        raw = vdb["matrix"]
        raw = zlib.decompress(base64.b64decode(raw)) if raw.startswith("eJ") else base64.b64decode(raw)
        self.V = np.frombuffer(raw, dtype=np.float32).reshape(len(self.chunks), -1)
        self.norms = np.linalg.norm(self.V, axis=1)
        self._settings = None

    def _embed(self, texts):
        if self._settings is None:
            self._settings = EmbeddingSettings.from_env()
        return asyncio.run(doubao_embed(texts, self._settings))

    def search(self, query, k=3, both_drugs=None):
        """Cosine top-k with both-drug co-mention filter.

        Honest-evidence mode: if no chunk co-mentions BOTH drugs, we do NOT
        fall back to unrelated single-drug chunks (that would inject noise
        and let the LLM hallucinate an interaction). Instead we explicitly
        report the evidence gap — itself a verifiable finding (ophthalmic
        DDI literature is sparse).
        """
        qvec = np.asarray(self._embed([query]), dtype=np.float32).reshape(1, -1)
        sims = (self.V @ qvec.T).flatten() / (self.norms * np.linalg.norm(qvec) + 1e-9)
        top = np.argsort(sims)[::-1][:30]
        selected = top[:k]
        if both_drugs:
            oph, sys_d = both_drugs
            filtered = [i for i in top
                        if oph.lower() in self.chunks[i]["content"].lower()
                        and sys_d.lower() in self.chunks[i]["content"].lower()]
            if filtered:
                selected = filtered[:k]
            else:
                return ("No direct literature evidence co-mentioning both drugs "
                        f"({oph}, {sys_d}) was found in the evidence base — "
                        "consistent with the known scarcity of ophthalmic DDI literature.")
        return "\n\n".join(
            f"[{self.chunks[i].get('full_doc_id', i)}] {self.chunks[i]['content'][:400]}"
            for i in selected) or "No evidence."

dense = DenseRetriever()

def lit_ctx(oph, sys_d, k=3, method="naive_rag"):
    if method == "full_system":
        return dense.search(f"{oph} {sys_d} ophthalmic interaction", k=k, both_drugs=(oph, sys_d))
    return bm25_lit_ctx(oph, sys_d, k=k)

# ── System prompts ──
SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.

Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high.
No explanation. One word only."""

# Full_system-specific prompt with rule calibration
SYSTEM_FULL = """You are a clinical pharmacologist completing a structured drug interaction assessment. You have access to:

1. A RULE ENGINE that has already incorporated ophthalmic pharmacokinetic data. When a rule is triggered under "MATCHED RULES", the interaction mechanism is clinically plausible AT OPHTHALMIC DOSES. Do not dismiss a triggered rule based solely on the generic assumption that "ophthalmic drugs have low systemic absorption" — that factor has already been accounted for.

2. A structured ENTITY REGISTRY with drug-specific flags (absorption class, CYP substrates, NTI status, etc.).

3. Relevant LITERATURE excerpts. NOTE: for most ophthalmic drug pairs no direct co-mention literature exists — if the LITERATURE section says no direct evidence was found, do NOT interpret that as "no interaction" (it reflects a documented evidence gap). Base your judgment on the RULE ENGINE and DRUG PROFILES; use literature only when it provides direct evidence for THIS pair.

CRITICAL CONSTRAINT: If the context says "HARD CONSTRAINT: ... risk MUST be low", you MUST output "low". This overrides all other considerations.

You may adjust the severity level if you have SPECIFIC pharmacokinetic evidence (e.g., a particular drug's measured plasma level contradicting the rule's default assumption), but you MUST cite that evidence explicitly.

Classify the interaction risk as: low, medium, or high.

Reply with EXACTLY ONE WORD: low, medium, or high.
No explanation. One word only."""

# ── Prompt builder ──
def build(method, case):
    oph, sys_d = case["ophthalmic"], case["systemic"]
    pair = f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sys_d} (oral/IV)\nRisk level:"
    
    if method == "pure_llm":
        return pair
    
    elif method == "naive_rag":
        return f"Evidence:\n{lit_ctx(oph, sys_d, method='naive_rag')}\n\n{pair}"
    
    elif method == "lightrag":
        return f"Drug profiles:\n{kg.full_kg_context(oph, sys_d)}\n\n{pair}"
    
    elif method == "full_system":
        # Cascade v2: deterministic rule + class-matrix layer first (MAX-MATCH +
        # absorption-scaled class pairs + G19 hard constraint). LLM + literature
        # only for pairs the deterministic layer leaves uncovered.
        level, matched, _ = kg.deterministic_level_v2(oph, sys_d)
        if level is not None:
            return ("CASCADE-DETERMINISTIC", level, matched, None)
        return (
            f"=== DRUG PROFILES ===\n{kg.full_kg_context(oph, sys_d)}\n\n"
            f"=== LITERATURE ===\n{lit_ctx(oph, sys_d, method='full_system')}\n\n"
            f"{pair}",
            None, None, None,
        )
    return pair, None, None, None

# ── API ──
def call(prompt, method="pure_llm"):
    sys_prompt = SYSTEM_FULL if method == "full_system" else SYSTEM
    for a in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":sys_prompt},{"role":"user","content":prompt}],
                temperature=0, max_tokens=10)
            return r.choices[0].message.content.strip().lower()
        except Exception as e:
            if a < 2: time.sleep(2**(a+1))
            else: return f"error:{e}"

# ── Parse level ──
def parse(raw):
    t = raw.lower()
    if "high" in t: return "high"
    if "medium" in t or "moderate" in t: return "medium"
    if "low" in t: return "low"
    return "unparseable"

# ── Metrics ──
def metrics(pairs):
    """Compute skill-required classification metrics."""
    lm = {"low":1,"medium":2,"high":3,"unknown":0}
    valid = [(lm[p["gold"]], lm[p["pred"]]) for p in pairs if p["pred"] != "unparseable"]
    if not valid: return {}
    
    # Binary: high vs rest
    tp = sum(1 for p in pairs if p["gold"]=="high" and p["pred"]=="high")
    fp = sum(1 for p in pairs if p["gold"]!="high" and p["pred"]=="high")
    fn = sum(1 for p in pairs if p["gold"]=="high" and p["pred"]!="high")
    tn = sum(1 for p in pairs if p["gold"]!="high" and p["pred"]!="high")
    sens = tp/(tp+fn) if (tp+fn)>0 else 0
    spec = tn/(tn+fp) if (tn+fp)>0 else 0
    prec = tp/(tp+fp) if (tp+fp)>0 else 0
    f1 = 2*prec*sens/(prec+sens) if (prec+sens)>0 else 0
    
    # 4-level accuracy
    exact = sum(1 for p in pairs if p["gold"]==p["pred"])
    acc4 = exact/len(pairs)
    
    # Cohen's κ
    po = sum(1 for g,p in valid if g==p)/len(valid)
    gc = Counter(g for g,_ in valid); pc = Counter(p for _,p in valid)
    pe = sum(gc.get(k,0)*pc.get(k,0) for k in range(1,4))/(len(valid)**2)
    kappa = (po-pe)/(1-pe) if (1-pe)>0 else 0
    
    return {
        "n": len(pairs),
        "sens_high": round(sens,3), "spec_high": round(spec,3), "f1_high": round(f1,3),
        "acc_4level": round(acc4,3), "cohens_kappa": round(kappa,3),
        "unparseable": sum(1 for p in pairs if p["pred"]=="unparseable"),
    }

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    records = []
    results = {m: [] for m in methods}
    
    print(f"Classification Ablation: {len(GOLD)} cases × {len(methods)} methods = {len(GOLD)*len(methods)} calls\n")
    
    for case in GOLD:
        for method in methods:
            built = build(method, case)
            if isinstance(built, tuple):
                prompt, det_level, matched_ids, _ = built
            else:
                prompt, det_level, matched_ids = built, None, None

            if det_level is not None:
                # Cascade deterministic stage: no LLM call
                raw = det_level
                pred = det_level
            else:
                raw = call(prompt, method)
                pred = parse(raw)
            
            evidence = None
            if method in ("naive_rag", "full_system") and not isinstance(built, tuple):
                evidence = lit_ctx(case["ophthalmic"], case["systemic"], method=method)
            elif method == "full_system" and isinstance(built, tuple) and det_level is None:
                evidence = lit_ctx(case["ophthalmic"], case["systemic"], method=method)
            
            records.append({
                "case_id": case["case_id"], "method": method,
                "ophthalmic": case["ophthalmic"], "systemic": case["systemic"],
                "gold": case["ddinter_level"], "predicted": pred, "raw": raw,
                "lit_evidence": evidence,
                "cascade": "deterministic" if det_level is not None else ("llm" if method == "full_system" else None),
            })
            results[method].append({
                "case_id": case["case_id"],
                "gold": case["ddinter_level"], "pred": pred,
            })
            
            if len(records) % 20 == 0:
                r20 = [r for r in records[-20:] if r["predicted"]!="unparseable"]
                acc = sum(1 for r in r20 if r["gold"]==r["predicted"])/len(r20) if r20 else 0
                print(f"  [{len(records):3d}/{len(GOLD)*len(methods)}] recent acc: {acc:.0%}")
            
            time.sleep(SLEEP)
    
    # Save
    out = ROOT / "output" / "ablation_classify.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    
    # ── Skill metrics ──
    print(f"\n{'='*70}")
    print(f"  SKILL-REQUIRED CLASSIFICATION METRICS (20 expert gold cases)")
    print(f"{'='*70}")
    print(f"{'Method':<14} {'Sens':>6} {'Spec':>6} {'F1':>6} {'Acc4':>6} {'κ':>6} {'Pass':>6}")
    print(f"{'-'*52}")
    
    all_m = {}
    for method in methods:
        m = metrics(results[method])
        all_m[method] = m
        passes = sum([
            m.get("sens_high",0) >= 0.70,
            m.get("spec_high",0) >= 0.60,
            m.get("acc_4level",0) >= 0.50,
            m.get("cohens_kappa",0) >= 0.40,
        ])
        print(f"{method:<14} {m.get('sens_high',0):.3f} {m.get('spec_high',0):.3f} {m.get('f1_high',0):.3f} {m.get('acc_4level',0):.3f} {m.get('cohens_kappa',0):.3f}  {passes}/4")
    
    # Gradient
    base = all_m["pure_llm"]
    print(f"\n  Δ vs pure_llm (F1={base['f1_high']:.3f}, κ={base['cohens_kappa']:.3f}):")
    for m in ["naive_rag","lightrag","full_system"]:
        d_f1 = all_m[m]["f1_high"] - base["f1_high"]
        d_k = all_m[m]["cohens_kappa"] - base["cohens_kappa"]
        print(f"    {m:12s}: F1={all_m[m]['f1_high']:.3f} (Δ{d_f1:+.3f})  κ={all_m[m]['cohens_kappa']:.3f} (Δ{d_k:+.3f})")
    
    print(f"\n  Results: {out}")

if __name__ == "__main__":
    main()
