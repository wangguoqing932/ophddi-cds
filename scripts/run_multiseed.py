"""Execute deterministic synthetic baseline runs over multiple random seeds."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate import evaluate_predictions
from generate_cases import generate_cases
from run_baselines import run_baselines


def run_multiseed(*, seeds: list[int], max_cases: int, synthetic: bool) -> tuple[list[dict], dict]:
    """Run baselines independently per seed and return rows plus aggregate metrics."""
    if not synthetic:
        raise ValueError("Offline multiseed runs require synthetic=True explicitly.")
    rows: list[dict] = []
    by_seed: dict[str, dict] = {}
    for seed in seeds:
        cases = generate_cases(seed=seed, max_cases=max_cases)
        predictions, metadata = run_baselines(cases, seed=seed, synthetic=True)
        for prediction in predictions:
            prediction["seed"] = seed
        rows.extend(predictions)
        by_seed[str(seed)] = {"metadata": metadata, "metrics": evaluate_predictions(predictions)}
    return rows, {"mode": "synthetic", "offline": True, "seeds": seeds, "max_cases": max_cases, "per_seed": by_seed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--max-cases", type=int, default=20)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "multiseed_predictions.jsonl")
    parser.add_argument("--metrics-output", type=Path, help="Destination multiseed metrics JSON")
    parser.add_argument("--synthetic", action="store_true", help="Run deterministic offline surrogate baselines.")
    args = parser.parse_args()
    if not args.synthetic:
        parser.error("--synthetic is required for the offline multiseed runner")
    rows, summary = run_multiseed(seeds=args.seeds, max_cases=args.max_cases, synthetic=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    metrics_path = args.metrics_output or args.output.with_suffix(".metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"predictions": len(rows), "metrics": str(metrics_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
