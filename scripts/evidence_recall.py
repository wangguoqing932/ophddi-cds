#!/usr/bin/env python3
"""evidence_recall.py — 20 gold cases × 4 methods: mechanism recall + hallucination rate"""

import asyncio, csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi

load_dotenv(ROOT / ".env")

# ── Config ──
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
TEMPERATURE = 0
SLEEP = 0.5

# ── Load gold ──
with open(ROOT / "data" / "gold_mechanisms.json", encoding="utf-8") as f:
    GOLD = json.load(f)

# ── Load evidence ──
chunks = []
with open(ROOT / "data" / "seed" / "evidence_chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            chunks.append(json.loads(line))
texts = [c.get("text", c.get("content", "")) for c in chunks]
bm25 = BM25Okapi([t.lower().split() for t in texts])

# ── Load rules context ──
import yaml
with open(ROOT / "configs" / "rules.yaml", encoding="utf-8") as f:
    rules_config = yaml.safe_load(f)

# Build rule lookup: (drug_class or flag) -> rule texts
def get_rule_context(ophthalmic_class, systemic_class):
    """Find relevant rules for this drug pair."""
    relevant = []
    for rule in rules_config.get("rules", []):
        rationale = rule.get("rationale", "")
        if not rationale:
            continue
        # Simple class-based matching
        a_flags = rule.get("entity_a_flags", [])
        relevant.append(f"[{rule['id']}] severity={rule['severity']}: {rationale}")
    # Return top-5 most relevant
    return "\n".join(relevant[:5])

# ── Context builders ──
def get_literature(oph, sys_d, top_k=3):
    query = f"{oph} {sys_d} ophthalmic interaction mechanism"
    scores = bm25.get_scores(query.lower().split())
    top_idx = scores.argsort()[-top_k:][::-1]
    snips = []
    for i in top_idx:
        c = chunks[i]
        snips.append(f"[{c.get('doc_id', i)}] {texts[i][:400]}")
    return "\n".join(snips) if snips else "No relevant literature found."

def get_lightrag(oph, sys_d):
    try:
        from ophthalmic_ddi_cds_agent.lightrag_adapter import LightRAGAdapter
        async def _q():
            adapter = LightRAGAdapter()
            return await adapter.query(
                f"What is the known interaction mechanism between ophthalmic {oph} and systemic {sys_d}?",
                mode="hybrid",
            )
        return asyncio.run(_q())
    except Exception as e:
        return f"[LightRAG unavailable: {e}]"

# ── System prompt ──
SYSTEM = """You are a clinical pharmacologist. Identify known drug interaction mechanisms.

For the given drug pair, list ALL known pharmacological interaction mechanisms.
For each mechanism, provide:
1. Mechanism name (e.g., "additive_beta_blockade", "CYP3A4_inhibition")
2. Brief description (1 sentence)
3. Whether it applies at OPHTHALMIC doses (consider systemic absorption from eye drops)

If NO known interaction exists, explicitly state: "No clinically significant interaction mechanism identified."

Format your response as:
Mechanism 1: [name] — [description] — [applies at ophthalmic dose? yes/no/uncertain]
Mechanism 2: ...

Do NOT fabricate mechanisms. If uncertain, say so."""

# ── Prompt builders ──
def build_prompt(method, case):
    oph = case["ophthalmic"]
    sys_d = case["systemic"]
    oph_cls = case.get("ophthalmic_class", "")
    sys_cls = case.get("systemic_class", "")

    pair_info = (
        f"Drug pair:\n"
        f"  Ophthalmic: {oph} ({oph_cls}, eye drops)\n"
        f"  Systemic:   {sys_d} ({sys_cls}, {case.get('systemic_route', 'oral')})\n\n"
        f"Identify all known interaction mechanisms:"
    )

    if method == "pure_llm":
        return pair_info

    elif method == "naive_rag":
        lit = get_literature(oph, sys_d)
        return f"Relevant literature:\n{lit}\n\n---\n\n{pair_info}"

    elif method == "lightrag":
        lrag = get_lightrag(oph, sys_d)
        return f"Knowledge graph context:\n{lrag}\n\n---\n\n{pair_info}"

    elif method == "full_system":
        rules = get_rule_context(oph_cls, sys_cls)
        lrag = get_lightrag(oph, sys_d)
        lit = get_literature(oph, sys_d)
        return (
            f"Rule engine context:\n{rules}\n\n"
            f"Knowledge graph context:\n{lrag}\n\n"
            f"Relevant literature:\n{lit}\n\n"
            f"---\n\n{pair_info}"
        )
    return pair_info

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
                temperature=TEMPERATURE,
                max_tokens=300,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
            else:
                return f"ERROR: {e}"

# ── Parse mechanisms from LLM response ──
def extract_mechanisms(text):
    """Extract mechanism names from LLM response text."""
    text_lower = text.lower()
    mechs = []

    # Known mechanism patterns (from gold + common pharmacology)
    KNOWN_PATTERNS = [
        # Beta blockade
        (r"additive.?beta.?blockade", "additive_beta_blockade"),
        (r"additive.?bradycardia", "additive_bradycardia"),
        (r"additive.?av.?conduction", "additive_AV_conduction_delay"),
        (r"additive.?cardiodepression", "additive_cardiodepression"),
        (r"additive.?negative.?inotropic", "additive_cardiodepression"),
        # CNS
        (r"additive.?cns.?depression", "additive_CNS_depression"),
        (r"additive.?sedation", "additive_CNS_depression"),
        (r"additive.?hypotension", "additive_hypotension"),
        (r"respiratory.?depression", "additive_CNS_depression"),
        # Anticholinergic
        (r"additive.?anticholinergic", "additive_anticholinergic_burden"),
        (r"anticholinergic.?burden", "additive_anticholinergic_burden"),
        (r"anticholinergic.?toxicity", "additive_anticholinergic_burden"),
        # Electrolyte / acidosis
        (r"additive.?metabolic.?acidosis", "additive_metabolic_acidosis"),
        (r"additive.?electrolyte", "additive_electrolyte_disturbance"),
        (r"electrolyte.?disturbance", "additive_electrolyte_disturbance"),
        (r"hypokalemia", "additive_electrolyte_disturbance"),
        (r"carbonic.?anhydrase.?inhibit", "additive_carbonic_anhydrase_inhibition"),
        # Bleeding
        (r"additive.?bleeding", "additive_bleeding_risk"),
        (r"bleeding.?risk", "additive_bleeding_risk"),
        (r"enhanced.?anticoagul", "additive_bleeding_risk"),
        # Corticosteroid
        (r"additive.?corticosteroid", "additive_corticosteroid_effects"),
        (r"adrenal.?suppression", "additive_corticosteroid_effects"),
        # CYP (trap — should NOT be mentioned for ophthalmic)
        (r"cyp1a2.?inhibit", "CYP1A2_inhibition"),
        (r"cyp3a4.?inhibit", "CYP3A4_inhibition"),
        (r"cyp3a4.?induct", "CYP3A4_induction"),
        (r"cyp2d6", "CYP2D6_metabolism"),
        # QT (trap)
        (r"qt.?prolong", "QT_prolongation"),
        (r"qtc.?prolong", "QT_prolongation"),
        (r"torsade", "QT_prolongation"),
        # General "no interaction"
        (r"no.?clinically.?significant", "NO_INTERACTION"),
        (r"no.?known.?interact", "NO_INTERACTION"),
        (r"no.?interaction", "NO_INTERACTION"),
        (r"no.?pharmacological", "NO_INTERACTION"),
    ]

    for pattern, name in KNOWN_PATTERNS:
        if re.search(pattern, text_lower):
            if name not in mechs:
                mechs.append(name)

    return mechs

# ── Evaluate ──
def evaluate_case(case, response_text, method):
    gold_mechs = set(case["true_mechanisms"])
    found_mechs = set(extract_mechanisms(response_text))
    gold_empty = len(gold_mechs) == 0

    if gold_empty:
        # This should be "no interaction" — check for hallucination
        hallucinations = found_mechs - {"NO_INTERACTION"}
        recall = 1.0 if "NO_INTERACTION" in found_mechs else 0.0
        hall_rate = 1.0 if len(hallucinations) > 0 else 0.0
        return {
            "recall": recall,
            "hallucination": hall_rate,
            "hall_mechs": list(hallucinations),
            "found": list(found_mechs),
            "gold": [],
            "correct_no_interaction": "NO_INTERACTION" in found_mechs,
        }
    else:
        # Should find specific mechanisms
        recalled = gold_mechs & found_mechs
        hallucinations = found_mechs - gold_mechs - {"NO_INTERACTION"}
        # Remove "NO_INTERACTION" from found for positive cases (it's a false negative)
        recall_rate = len(recalled) / len(gold_mechs) if gold_mechs else 1.0
        hall_rate = 1.0 if len(hallucinations) > 0 else 0.0
        return {
            "recall": recall_rate,
            "hallucination": hall_rate,
            "hall_mechs": list(hallucinations),
            "found": list(found_mechs),
            "gold": list(gold_mechs),
            "recalled": list(recalled),
            "missed": list(gold_mechs - found_mechs),
        }

# ── Main ──
def main():
    methods = ["pure_llm", "naive_rag", "lightrag", "full_system"]
    total = len(GOLD) * len(methods)
    results = []
    count = 0

    print(f"Evidence Recall Experiment: {len(GOLD)} cases × {len(methods)} methods = {total} calls")
    print(f"Model: {MODEL}")
    print("-" * 60)

    for case in GOLD:
        for method in methods:
            count += 1
            prompt = build_prompt(method, case)
            raw = call_llm(prompt)
            eval_result = evaluate_case(case, raw, method)

            results.append({
                "case_id": case["case_id"],
                "method": method,
                "ophthalmic": case["ophthalmic"],
                "systemic": case["systemic"],
                "gold_mechanisms": case["true_mechanisms"],
                "llm_response": raw,
                "found_mechanisms": eval_result["found"],
                "recall": eval_result["recall"],
                "hallucination": eval_result["hallucination"],
                "hall_mechanisms": eval_result.get("hall_mechs", []),
            })

            marker = ""
            if eval_result["hallucination"]: marker = " ⚡HALLUCINATION"
            status = f"R={eval_result['recall']:.0%}" if eval_result['recall'] < 1 else "R=OK"
            print(f"  [{count:3d}/{total}] {case['case_id']} | {method:12s} → {status}{marker}")

            time.sleep(SLEEP)

    # Save
    out_path = ROOT / "output" / "evidence_recall_results.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── Summary ──
    print("\n" + "=" * 70)
    print("  EVIDENCE RECALL RESULTS (20 gold cases)")
    print("=" * 70)

    for method in methods:
        mres = [r for r in results if r["method"] == method]

        # Mean recall on positive cases (G01-G12, those with mechanisms)
        pos = [r for r in mres if len(r["gold_mechanisms"]) > 0]
        neg = [r for r in mres if len(r["gold_mechanisms"]) == 0]
        mean_recall = sum(r["recall"] for r in pos) / len(pos) if pos else 0
        hall_rate = sum(r["hallucination"] for r in mres) / len(mres) if mres else 0

        # Trap cases specifically
        traps = [r for r in mres if r["case_id"] in ("G16", "G19")]
        trap_hall = sum(r["hallucination"] for r in traps)
        trap_pass = len(traps) - trap_hall

        # Perfect: recall=1.0 on positive AND no hallucination on negative
        perfect_pos = sum(1 for r in pos if r["recall"] == 1.0)
        perfect_neg = sum(1 for r in neg if r["hallucination"] == 0)

        print(f"\n  {method}:")
        print(f"    Mechanism recall (pos cases, n={len(pos)}): {mean_recall:.1%}  ({perfect_pos}/{len(pos)} perfect)")
        print(f"    Hallucination rate (all, n={len(mres)}):      {hall_rate:.1%}  ({len(mres) - int(sum(r['hallucination'] for r in mres))}/{len(mres)} clean)")
        print(f"    No-interaction correct (neg cases, n={len(neg)}): {perfect_neg}/{len(neg)}")
        print(f"    Trap cases (G16,G19): {trap_pass}/{len(traps)} passed (no hallucination)")

    print(f"\n  Results saved: {out_path}")

if __name__ == "__main__":
    main()
