#!/usr/bin/env python3
"""run_multiseed_per_dataset.py — v3.0-format multiseed evaluation.

8 validation datasets x 4 methods x 5 seeds, real LLM baselines.

Methods:
  pure_llm  : 1 LLM call, no context
  naive_rag : BM25 retrieval over evidence chunks + LLM
  lightrag  : PreciseKG full_kg_context + LLM
  full_system : deterministic v2 cascade (0 LLM calls)

Seeds -> temperature schedule: seed0 = 0.0 (identical to ablation_l1_rerun protocol,
allowing exact reconciliation), seeds 1-4 sample with increasing temperature.

Resume-safe: per (dataset, seed) raw files are skipped when already complete.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG
from evaluate import classification_metrics

load_dotenv(ROOT / ".env")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MODEL = os.getenv("LLM_CHAT_MODEL", "deepseek-chat")
# Reasoning models (v4-flash) need a large token budget for the thinking chain;
# chat models answer the one-word task directly with a tiny budget.
MAX_TOKENS = 600 if "flash" in MODEL else 10
kg = PreciseKG()

SEEDS = [0, 1, 2, 3, 4]
TEMPERATURE = {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.9, 4: 1.2}
METHODS = ["pure_llm", "naive_rag", "lightrag", "full_system"]

SYSTEM = """You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.

Classify the interaction risk as: low, medium, or high.
Definitions:
- low: negligible clinical significance at ophthalmic doses
- medium: potential interaction requiring monitoring or dose adjustment
- high: clinically significant interaction; may require avoidance or strict monitoring

Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose, but some drugs like timolol, atropine, dexamethasone reach >50%).

Reply with EXACTLY ONE WORD: low, medium, or high. No explanation."""

_chunks = []
for line in (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8"):
    if line.strip():
        _chunks.append(json.loads(line))
_texts = [c.get("text", c.get("content", "")) for c in _chunks]
_bm25 = BM25Okapi([t.lower().split() for t in _texts])


def bm25_ctx(oph, sysd, k=3):
    q = f"{oph} {sysd} ophthalmic interaction"
    scores = _bm25.get_scores(q.lower().split())
    top = scores.argsort()[-k:][::-1]
    return "\n\n".join(f"[{_chunks[i].get('doc_id', i)}] {_texts[i][:400]}" for i in top) or "No evidence."


def call(prompt, temperature):
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
            else:
                return "error"


def parse(raw):
    t = raw.lower()
    if "high" in t:
        return "high"
    if "medium" in t or "moderate" in t:
        return "medium"
    if "low" in t:
        return "low"
    return "unknown"


# --------------------------------------------------------------------------
# Entity resolution for datasets keyed by entity ids (dev-ddinter, int-pubmed)
# --------------------------------------------------------------------------
def _load_entities_a() -> dict[str, str]:
    out = {}
    with (ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["topical_ophthalmic_medications_id"]] = row["primary_name"]
    return out


def _load_entities_b() -> dict[str, str]:
    out = {}
    with (ROOT / "data" / "seed" / "entities_b.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["entity_b_id"]] = row["generic_name"]
    return out


ENTITIES_A = _load_entities_a()
ENTITIES_B = _load_entities_b()


# --------------------------------------------------------------------------
# Dataset registry
# --------------------------------------------------------------------------
def load_dataset(dataset_id: str) -> list[dict]:
    """Return [{'case_id', 'a_name', 'b_name', 'gold'}]."""
    if dataset_id in ("dev-ddinter", "int-pubmed"):
        rows = []
        with (ROOT / "data" / "datasets" / dataset_id / "cases.jsonl").open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                c = json.loads(line)
                rows.append({"case_id": c["case_id"],
                             "a_name": ENTITIES_A.get(c["entity_a_id"], c["entity_a_id"]),
                             "b_name": ENTITIES_B.get(c["entity_b_id"], c["entity_b_id"]),
                             "gold": str(c["gold_risk_level"]).strip().lower()})
        return rows
    if dataset_id == "internal_validation":
        rows = []
        with (ROOT / "data" / "datasets" / dataset_id / "cases.jsonl").open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                c = json.loads(line)
                rows.append({"case_id": c["case_id"],
                             "a_name": c.get("ophthalmic_drug") or c.get("ophthalmic"),
                             "b_name": c.get("systemic_drug") or c.get("systemic"),
                             "gold": str(c["gold_risk_level"]).strip().lower()})
        return rows
    if dataset_id in ("external_validation", "external_pubmed", "consensus_validation"):
        rows = []
        with (ROOT / "data" / "datasets" / dataset_id / "cases.jsonl").open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                c = json.loads(line)
                rows.append({"case_id": c["case_id"], "a_name": c["ophthalmic_drug"],
                             "b_name": c["systemic_drug"], "gold": str(c["gold_risk_level"]).strip().lower()})
        return rows
    if dataset_id == "blind_l1":
        d = json.load((ROOT / "outputs" / "blind_test" / "l1_independent.json").open(encoding="utf-8"))
        return [{"case_id": c["case_id"], "a_name": c["ophthalmic_drug"],
                 "b_name": c["systemic_drug"], "gold": str(c["gold"]).strip().lower(),
                 "subset": c.get("source", "unknown")} for c in d]
    if dataset_id == "blind_v3_ddinter":
        d = json.load((ROOT / "outputs" / "blind_test" / "blind_set_v3_ddinter.json").open(encoding="utf-8"))
        items = d if isinstance(d, list) else d.get("cases", [])
        return [{"case_id": c["case_id"], "a_name": c["ophthalmic_drug"],
                 "b_name": c["systemic_drug"], "gold": str(c["proposed_gold"]).strip().lower()} for c in items]
    raise KeyError(dataset_id)


# NOTE: consensus_validation is EXCLUDED from performance evaluation — its gold is
# rule-derived by construction (build_consensus_val.py: T2 uses rule_level() output,
# T3 keeps only DDInter==Rules pairs, T4 = no-rule-hit negatives), so full_system
# scoring 1.000 there is definitional (tautology), not evidence. Kept only as an
# implementation-consistency note in the report. internal_validation overlaps
# blind_l1 78/78 by case_id (gold synced), so it is not an independent layer either;
# its Phase-2 threshold is computed locally by the deterministic engine.
DATASETS = [
    ("dev-ddinter", "development"),
    ("external_validation", "external_validation"),
    ("blind_l1", "external_validation"),
    ("blind_v3_ddinter", "external_validation"),
]


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------
def predict_case(oph: str, sysd: str, method: str, temperature: float) -> tuple[str, str]:
    """Return (predicted, raw). API failure -> ('error', 'error') so resume logic
    never treats a failed run as complete."""
    if method == "full_system":
        lvl, _, _ = kg.deterministic_level_v2(oph, sysd)
        return lvl, ""
    pair = f"Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)\nRisk level:"
    if method == "pure_llm":
        prompt = pair
    elif method == "naive_rag":
        prompt = f"Evidence:\n{bm25_ctx(oph, sysd)}\n\n{pair}"
    else:  # lightrag
        prompt = f"Drug profiles:\n{kg.full_kg_context(oph, sysd)}\n\n{pair}"
    raw = call(prompt, temperature)
    if raw == "error":
        return "error", "error"
    return parse(raw), raw


def run_dataset_seed(dataset_id: str, role: str, seed: int, raw_dir: Path) -> list[dict]:
    out_file = raw_dir / f"{dataset_id}__seed{seed}.jsonl"
    n_cases = len(load_dataset(dataset_id))
    if out_file.exists():
        rows = []
        with out_file.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        n_methods = len({r["method"] for r in rows})
        n_errors = sum(1 for r in rows if r.get("predicted") == "error")
        if n_methods == len(METHODS) and len(rows) == n_cases * len(METHODS) and n_errors == 0:
            print(f"  [skip] {dataset_id} seed={seed} already complete ({len(rows)} rows)")
            return rows
        if n_errors:
            print(f"  [rerun] {dataset_id} seed={seed}: {n_errors} error rows, re-running")
    cases = load_dataset(dataset_id)
    temperature = TEMPERATURE[seed]
    rows = []
    for i, c in enumerate(cases):
        for m in METHODS:
            pred, raw = predict_case(c["a_name"], c["b_name"], m, temperature)
            rows.append({"dataset_id": dataset_id, "dataset_role": role,
                         "case_id": c["case_id"], "a_name": c["a_name"], "b_name": c["b_name"],
                         "subset": c.get("subset", ""), "gold_risk": c["gold"], "method": m,
                         "seed": seed, "temperature": temperature, "predicted": pred,
                         "raw": raw, "synthetic": False})
        if (i + 1) % 25 == 0:
            print(f"  [{dataset_id} seed={seed}] {i + 1}/{len(cases)}", flush=True)
        time.sleep(0.15)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    return rows


def aggregate(raw_dir: Path, out_metrics: Path, out_all: Path) -> dict:
    all_rows = []
    for f in sorted(raw_dir.glob("*__seed*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    all_rows.append(json.loads(line))
    if not all_rows:
        raise RuntimeError("no raw rows found")
    with out_all.open("w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    failures = defaultdict(int)
    ok_rows = []
    for r in all_rows:
        if r.get("predicted") == "error":
            failures[(r["dataset_id"], r["method"], r["seed"])] += 1
        else:
            ok_rows.append(r)
    all_rows = ok_rows

    # per (dataset, method, seed) metrics
    grouped = defaultdict(list)
    for r in all_rows:
        grouped[(r["dataset_id"], r["method"], r["seed"])].append(r)
    per_cell = {}
    for (ds, method, seed), recs in grouped.items():
        m = classification_metrics([{"gold_risk": r["gold_risk"], "predicted": r["predicted"]} for r in recs])
        per_cell[f"{ds}|{method}|{seed}"] = {
            "n": m["n"], "acc4": m["exact_accuracy"], "sens": m["high_risk_sensitivity"],
            "spec": m["high_risk_specificity"], "f1": m["per_level"]["high"]["f1"],
            "kappa": m["cohen_kappa"],
        }

    # per (dataset, method): mean ± std over seeds
    per_dataset_method = {}
    for (ds, method, seed), recs in grouped.items():
        cell = per_cell[f"{ds}|{method}|{seed}"]
        key = (ds, method)
        d = per_dataset_method.setdefault(key, {"n": cell["n"], "acc4": [], "sens": [], "spec": [], "f1": [], "kappa": []})
        for metric in ("acc4", "sens", "spec", "f1", "kappa"):
            v = cell[metric]
            d[metric].append(v if v is not None else 0.0)

    # per-subset breakdown for blind_l1 (T1 / blind / guideline strata)
    def _stats(values: list[float]) -> dict:
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / len(values)
        return {"mean": round(mean, 4), "std": round(var ** 0.5, 4), "values": [round(v, 4) for v in values]}

    # per-subset breakdown for blind_l1 (T1 / blind / guideline strata)
    per_subset = {}
    subset_recs = defaultdict(list)
    for r in all_rows:
        if r["dataset_id"] == "blind_l1" and r.get("subset"):
            subset_recs[(r["subset"], r["method"], r["seed"])].append(r)
    subset_cell = {}
    for (sub, method, seed), recs in subset_recs.items():
        m = classification_metrics([{"gold_risk": r["gold_risk"], "predicted": r["predicted"]} for r in recs])
        subset_cell[f"{sub}|{method}|{seed}"] = {
            "n": m["n"], "acc4": m["exact_accuracy"], "sens": m["high_risk_sensitivity"],
            "spec": m["high_risk_specificity"], "f1": m["per_level"]["high"]["f1"], "kappa": m["cohen_kappa"]}
    for (sub, method, seed), recs in subset_recs.items():
        cell = subset_cell[f"{sub}|{method}|{seed}"]
        d = per_subset.setdefault(sub, {}).setdefault(method,
            {"n": cell["n"], "acc4": [], "sens": [], "spec": [], "f1": [], "kappa": []})
        for metric in ("acc4", "sens", "spec", "f1", "kappa"):
            v = cell[metric]
            d[metric].append(v if v is not None else 0.0)
    per_subset = {sub: {m: {metric: _stats(vals) for metric, vals in md.items() if metric != "n"}
                         | {"n": md["n"]} for m, md in methods.items()}
                  for sub, methods in per_subset.items()}

    per_dataset = {}
    for (ds, method), d in sorted(per_dataset_method.items()):
        per_dataset.setdefault(ds, {})[method] = {
            "n": d["n"],
            "acc4": _stats(d["acc4"]), "sens": _stats(d["sens"]), "spec": _stats(d["spec"]),
            "f1": _stats(d["f1"]), "kappa": _stats(d["kappa"]),
        }
    roles = dict(DATASETS)

    # generalization gap: external_validation - internal_validation (per method, mean of datasets)
    def _role_mean(role: str, metric: str) -> dict:
        acc = {}
        for ds, mdict in per_dataset.items():
            if roles.get(ds) == role:
                for method, m in mdict.items():
                    acc.setdefault(method, []).append(m[metric]["mean"])
        return {m: round(sum(v) / len(v), 4) for m, v in acc.items()}

    gap = {}
    ext = _role_mean("external_validation", "acc4")
    intl = _role_mean("internal_validation", "acc4")
    gap["acc4"] = {m: round(ext[m] - intl[m], 4) for m in ext if m in intl}
    ext_s = _role_mean("external_validation", "sens")
    intl_s = _role_mean("internal_validation", "sens")
    gap["sens"] = {m: round(ext_s[m] - intl_s[m], 4) for m in ext_s if m in intl_s}
    ext_p = _role_mean("external_validation", "spec")
    intl_p = _role_mean("internal_validation", "spec")
    gap["spec"] = {m: round(ext_p[m] - intl_p[m], 4) for m in ext_p if m in intl_p}

    summary = {
        "mode": "real_llm", "seeds": SEEDS, "temperature_schedule": TEMPERATURE,
        "methods": METHODS, "datasets": [{"dataset_id": ds, "dataset_role": role} for ds, role in DATASETS],
        "n_predictions": len(all_rows), "n_api_failures": sum(failures.values()),
        "api_failures": {f"{k[0]}|{k[1]}|seed{k[2]}": v for k, v in sorted(failures.items())},
        "per_dataset": per_dataset,
        "per_subset_l1": per_subset,
        "generalization_gap": gap, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out_metrics.parent.mkdir(parents=True, exist_ok=True)
    out_metrics.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    parser.add_argument("--datasets", nargs="+", default=[ds for ds, _ in DATASETS])
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()

    raw_dir = ROOT / "outputs" / "multiseed_per_dataset"
    if not args.aggregate_only:
        for dataset_id in args.datasets:
            role = dict(DATASETS)[dataset_id]
            print(f"== {dataset_id} ({role}) ==", flush=True)
            for seed in args.seeds:
                run_dataset_seed(dataset_id, role, seed, raw_dir)

    summary = aggregate(raw_dir, raw_dir / "multiseed_per_dataset_metrics.json", raw_dir / "predictions_all.jsonl")
    print(f"aggregated: {summary['n_predictions']} predictions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
