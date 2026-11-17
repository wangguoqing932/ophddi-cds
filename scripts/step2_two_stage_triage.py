#!/usr/bin/env python3
"""step2_two_stage_triage.py — LLM 独立复核规则引擎的筛查标记"""

import csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")

# ── Load rule engine results ──
rule_df = pd.read_csv(ROOT / "phase5_audit" / "phase5_v2_int_results.csv")

# ── Load entity names ──
name_a = {}
with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        name_a[row["topical_ophthalmic_medications_id"]] = row["primary_name"]
name_b = {}
with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        name_b[row["entity_b_id"]] = row["generic_name"]

# ── Build triage pool: rule engine says medium+high ──
triage = rule_df[rule_df["system_level"].isin(["medium", "high"])].copy()
triage["oph_name"] = triage["entity_a_id"].map(name_a)
triage["sys_name"] = triage["entity_b_id"].map(name_b)

fp_count = int((triage["ddinter_level"] == "low").sum())
tp_count = int((triage["ddinter_level"].isin(["medium", "high"])).sum())

print(f"规则引擎筛查阳性: {len(triage)} / {len(rule_df)}")
print(f"  其中 DDInter=low: {fp_count} (需要降级的假阳性)")
print(f"  其中 DDInter=medium/high: {tp_count} (真阳性)")

# ── Prompts ──
OLD_SYSTEM = """You are a clinical pharmacologist. 
Assess the DDI risk level for topical ophthalmic drugs.
Reply with exactly one word: low, medium, or high."""

OLD_USER = """Drug pair: {ophthalmic} (ophthalmic) × {systemic} (systemic)

Rule engine assessment: {rule_level}

Based on the above, what is the risk level?"""

NEW_SYSTEM = """You are a clinical pharmacologist specializing in ophthalmic drug safety.
A screening system has flagged a drug pair for potential interaction risk.
The screening system is conservative — it catches most real risks but also 
produces many false positives.

Your job: INDEPENDENTLY verify this flag. Consider:
1. The actual systemic exposure from ophthalmic administration (often <1% of oral dose)
2. Whether the interaction mechanism is clinically plausible at ophthalmic doses
3. Whether the evidence supports upgrading or downgrading the screening flag

Reply with exactly one word: low, medium, or high."""

NEW_USER = """Drug pair: {ophthalmic} (ophthalmic) × {systemic} (systemic)

Screening system flagged as: {rule_level}
(This is a preliminary screening flag, not a final assessment. It may be wrong.)

Based on ophthalmic pharmacokinetics and clinical evidence, 
what is your INDEPENDENT assessment?
Risk level:"""

# ── Parse ──
def parse_level(text):
    t = text.lower()
    if "high" in t: return "high"
    if "medium" in t or "moderate" in t: return "medium"
    if "low" in t or "minimal" in t or "negligible" in t: return "low"
    return "unparseable"

def call_llm(system_prompt, user_prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=10,
            )
            return parse_level(resp.choices[0].message.content.strip())
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
            else:
                return f"ERROR: {e}"

# ── Run ──
results = []
for i, (_, row) in enumerate(triage.iterrows()):
    case_id = row["case_id"]
    oph = row["oph_name"]
    sys_d = row["sys_name"]
    rule_level = row["system_level"]
    ddinter = row["ddinter_level"]

    old_prompt = OLD_USER.format(ophthalmic=oph, systemic=sys_d, rule_level=rule_level)
    old_decision = call_llm(OLD_SYSTEM, old_prompt)

    new_prompt = NEW_USER.format(ophthalmic=oph, systemic=sys_d, rule_level=rule_level)
    new_decision = call_llm(NEW_SYSTEM, new_prompt)

    results.append({
        "case_id": case_id,
        "ophthalmic": oph,
        "systemic": sys_d,
        "rule_level": rule_level,
        "ddinter_level": ddinter,
        "old_prompt_decision": old_decision,
        "new_prompt_decision": new_decision,
    })

    if (i + 1) % 15 == 0 or (i + 1) == len(triage):
        print(f"  进度: {i+1}/{len(triage)}")
    time.sleep(0.5)

# ── Save ──
out_path = ROOT / "output" / "two_stage_triage_results.jsonl"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ── Analyze ──
results_df = pd.DataFrame(results)

fp_mask = results_df["ddinter_level"] == "low"
tp_mask = results_df["ddinter_level"].isin(["medium", "high"])

old_fp_corrected = int((results_df.loc[fp_mask, "old_prompt_decision"] == "low").sum())
new_fp_corrected = int((results_df.loc[fp_mask, "new_prompt_decision"] == "low").sum())
total_fp = int(fp_mask.sum())

old_tp_kept = int((results_df.loc[tp_mask, "old_prompt_decision"].isin(["medium", "high"])).sum())
new_tp_kept = int((results_df.loc[tp_mask, "new_prompt_decision"].isin(["medium", "high"])).sum())
total_tp = int(tp_mask.sum())

print("\n" + "=" * 70)
print("  两阶段复核结果")
print("=" * 70)

print(f"\n  假阳性纠正（特异性提升）:")
print(f"    旧 prompt (盲从版):    {old_fp_corrected}/{total_fp} 被正确降级 ({old_fp_corrected/total_fp*100:.1f}%)" if total_fp else "    旧 prompt: N/A")
print(f"    新 prompt (独立审核版): {new_fp_corrected}/{total_fp} 被正确降级 ({new_fp_corrected/total_fp*100:.1f}%)" if total_fp else "    新 prompt: N/A")

print(f"\n  真阳性保持（敏感度维持）:")
print(f"    旧 prompt: {old_tp_kept}/{total_tp} 保持阳性 ({old_tp_kept/total_tp*100:.1f}%)" if total_tp else "    旧 prompt: N/A")
print(f"    新 prompt: {new_tp_kept}/{total_tp} 保持阳性 ({new_tp_kept/total_tp*100:.1f}%)" if total_tp else "    新 prompt: N/A")

# Decision changes
print(f"\n  决策变化:")
changes = results_df[results_df["old_prompt_decision"] != results_df["new_prompt_decision"]]
if len(changes) > 0:
    for _, r in changes.iterrows():
        direction = "↑升级" if r["new_prompt_decision"] in ["medium","high"] and r["old_prompt_decision"]=="low" else "↓降级"
        correct = "✅" if r["new_prompt_decision"] == r["ddinter_level"] else "❌"
        print(f"    {r['case_id']}: {r['ophthalmic']} × {r['systemic']} | "
              f"规则={r['rule_level']} DDInter={r['ddinter_level']} | "
              f"旧→新: {r['old_prompt_decision']}→{r['new_prompt_decision']} {direction} {correct}")
else:
    print("    （无变化）")

print(f"\n  完整结果: {out_path}")
