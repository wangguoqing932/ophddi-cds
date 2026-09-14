"""Run reproducible baseline predictions.

This offline implementation requires ``--synthetic``. It never substitutes synthetic
predictions for a real LLM/RAG/system evaluation without an explicit opt-in.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_cases import case_metadata, generate_cases

METHODS = ("pure_llm", "naive_rag", "lightrag", "full_system")


def _synthetic_prediction(case: dict, method: str, seed: int) -> str:
    """Produce deterministic surrogate predictions for pipeline testing only."""
    gold = case["gold_risk"]
    # Fixed method-specific error rates make the option useful for integration tests,
    # while the hash makes results independent of execution order and platform.
    error_threshold = {"pure_llm": 38, "naive_rag": 28, "lightrag": 20, "full_system": 0}[method]
    digest = hashlib.sha256(f"{seed}|{method}|{case['case_id']}".encode()).digest()[0] % 100
    if digest >= error_threshold:
        return gold
    levels = ("high", "medium", "low", "unknown")
    alternatives = tuple(level for level in levels if level != gold)
    return alternatives[hashlib.sha256(f"alternate|{seed}|{method}|{case['case_id']}".encode()).digest()[0] % len(alternatives)]


def run_baselines(cases: list[dict], *, seed: int = 0, synthetic: bool = False) -> tuple[list[dict], dict]:
    """Run all baseline labels and return prediction rows with reproducibility metadata."""
    if not synthetic:
        raise ValueError("Real baseline execution is not implemented offline; pass synthetic=True explicitly.")
    predictions = []
    for case in cases:
        for method in METHODS:
            predictions.append({
                "method": method, "case_id": case["case_id"], "a_id": case["a_id"], "a_name": case["a_name"],
                "b_id": case["b_id"], "b_name": case["b_name"], "gold_risk": case["gold_risk"],
                "predicted": _synthetic_prediction(case, method, seed), "synthetic": True,
            })
    metadata = {
        "mode": "synthetic", "seed": seed, "methods": list(METHODS), "case_metadata": case_metadata(cases, seed=seed, max_cases=len(cases)),
        "prediction_count": len(predictions), "generated_at": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "offline": True,
    }
    return predictions, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "baseline_predictions.jsonl")
    parser.add_argument("--metadata-output", type=Path, help="Destination run metadata JSON")
    parser.add_argument("--max-cases", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--synthetic", action="store_true", help="Run deterministic offline surrogate baselines.")
    args = parser.parse_args()
    if not args.synthetic:
        parser.error("--synthetic is required for the offline baseline runner")
    cases = generate_cases(seed=args.seed, max_cases=args.max_cases)
    predictions, metadata = run_baselines(cases, seed=args.seed, synthetic=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in predictions), encoding="utf-8")
    metadata_path = args.metadata_output or args.output.with_suffix(".metadata.json")
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"predictions": len(predictions), "metadata": str(metadata_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
