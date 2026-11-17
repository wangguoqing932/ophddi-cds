# -*- coding: utf-8 -*-
"""rerun_rule_context.py — re-run only the affected rule_context baseline.

The rule_context prompt is the only baseline that uses PreciseKG.full_kg_context();
the other two baselines share the system prompt and are left unchanged. This
script re-runs rule_context on the L1 (118) and DDInter audit (92) sets at the
five temperature conditions, after correcting the exposure-band labels and the
absorption gate in the context block.

Outputs go to outputs/multiseed_per_dataset_rulecontext_fix/ so the deposited
pre-fix predictions remain intact.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
MAX_TOKENS = 600 if "flash" in MODEL else 10
kg = PreciseKG()

OUT = ROOT / "outputs" / "multiseed_per_dataset_rulecontext_fix"
TEMPERATURE = {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.9, 4: 1.2}

SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""


def parse(raw: str) -> str:
    t = raw.lower()
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unknown"


def call(prompt: str, temperature: float) -> str:
    for a in range(5):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}],
                temperature=temperature, max_tokens=MAX_TOKENS)
            return r.choices[0].message.content.strip().lower()
        except Exception:
            if a < 4:
                time.sleep(2 ** (a + 1))
    return "error"


def load_cases(dataset_id: str) -> list[dict]:
    if dataset_id == "blind_l1":
        d = json.load((ROOT / "outputs" / "blind_test" / "l1_independent.json").open(encoding="utf-8"))
        return [{"case_id": c["case_id"], "a_name": c["ophthalmic_drug"],
                 "b_name": c["systemic_drug"], "gold": str(c["gold"]).strip().lower(),
                 "subset": c.get("source", "unknown")} for c in d]
    if dataset_id == "blind_v3_ddinter":
        d = json.load((ROOT / "outputs" / "blind_test" / "blind_set_v3_ddinter.json").open(encoding="utf-8"))
        items = d if isinstance(d, list) else d.get("cases", [])
        return [{"case_id": c["case_id"], "a_name": c["ophthalmic_drug"],
                 "b_name": c["systemic_drug"], "gold": str(c["proposed_gold"]).strip().lower()}
                for c in items]
    raise KeyError(dataset_id)


def run_one(case: dict, dataset_id: str, seed: int) -> dict:
    pair = f"Drug pair: ophthalmic {case['a_name']} (eye drops) + systemic {case['b_name']} (oral/IV)\nRisk level:"
    prompt = f"Drug profiles:\n{kg.full_kg_context(case['a_name'], case['b_name'])}\n\n{pair}"
    raw = call(prompt, TEMPERATURE[seed])
    return {
        "dataset_id": dataset_id,
        "dataset_role": "external_validation",
        "case_id": case["case_id"],
        "a_name": case["a_name"],
        "b_name": case["b_name"],
        "subset": case.get("subset", ""),
        "gold_risk": case["gold"],
        "method": "lightrag",
        "seed": seed,
        "temperature": TEMPERATURE[seed],
        "predicted": parse(raw) if raw != "error" else "error",
        "raw": raw,
        "synthetic": False,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset_id in ["blind_l1", "blind_v3_ddinter"]:
        cases = load_cases(dataset_id)
        for seed in range(5):
            out_file = OUT / f"{dataset_id}__seed{seed}.jsonl"
            if out_file.exists():
                rows = [json.loads(l) for l in out_file.read_text(encoding="utf-8").splitlines() if l.strip()]
                if len(rows) == len(cases) and all(r.get("predicted") != "error" for r in rows):
                    print(f"[skip] {dataset_id} seed={seed} complete", flush=True)
                    continue
            print(f"[run] {dataset_id} seed={seed} n={len(cases)}", flush=True)
            with ThreadPoolExecutor(max_workers=4) as ex:
                rows = list(ex.map(lambda c: run_one(c, dataset_id, seed), cases))
            with open(out_file, "w", encoding="utf-8", newline="\n") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
            n_err = sum(1 for r in rows if r["predicted"] == "error")
            print(f"[done] {dataset_id} seed={seed} errors={n_err}", flush=True)


if __name__ == "__main__":
    main()
