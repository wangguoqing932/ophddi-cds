"""Evaluate four-level DDI-risk predictions from JSONL files, entirely offline."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

RISK_LEVELS = ("high", "medium", "low", "unknown")


def normalize_level(value: object) -> str:
    """Return a supported risk level, treating missing or invalid values as unknown."""
    level = str(value or "unknown").strip().lower()
    return level if level in RISK_LEVELS else "unknown"


def _safe_divide(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _round(value: float | None) -> float | None:
    return round(value, 4) if value is not None else None


def classification_metrics(records: Iterable[dict]) -> dict:
    """Calculate exact accuracy, macro-F1, high-risk binary metrics, and Cohen's kappa.

    Rows without a valid ``gold_risk`` are excluded. Invalid predictions are retained as
    ``unknown`` so that malformed model output cannot silently improve a score.
    """
    pairs = []
    for row in records:
        raw_gold = row.get("gold_risk", row.get("severity"))
        if str(raw_gold or "").strip().lower() not in RISK_LEVELS:
            continue
        pairs.append((normalize_level(raw_gold), normalize_level(row.get("predicted"))))
    n = len(pairs)
    confusion = {gold: {predicted: 0 for predicted in RISK_LEVELS} for gold in RISK_LEVELS}
    for gold, predicted in pairs:
        confusion[gold][predicted] += 1

    per_level = {}
    f1_values = []
    for level in RISK_LEVELS:
        tp = confusion[level][level]
        fp = sum(confusion[gold][level] for gold in RISK_LEVELS if gold != level)
        fn = sum(confusion[level][predicted] for predicted in RISK_LEVELS if predicted != level)
        precision = _safe_divide(tp, tp + fp)
        recall = _safe_divide(tp, tp + fn)
        f1 = _safe_divide(2 * tp, 2 * tp + fp + fn)
        per_level[level] = {"precision": _round(precision), "recall": _round(recall), "f1": _round(f1), "support": sum(confusion[level].values())}
        f1_values.append(f1 or 0.0)

    high_tp = confusion["high"]["high"]
    high_fn = sum(confusion["high"][predicted] for predicted in RISK_LEVELS if predicted != "high")
    high_fp = sum(confusion[gold]["high"] for gold in RISK_LEVELS if gold != "high")
    high_tn = n - high_tp - high_fn - high_fp
    observed = _safe_divide(sum(confusion[level][level] for level in RISK_LEVELS), n)
    expected = _safe_divide(
        sum(sum(confusion[level].values()) * sum(confusion[gold][level] for gold in RISK_LEVELS) for level in RISK_LEVELS),
        n * n,
    )
    kappa = None if expected is None or expected == 1 else (observed - expected) / (1 - expected)
    return {
        "n": n,
        "exact_accuracy": _round(observed),
        "macro_f1": _round(sum(f1_values) / len(RISK_LEVELS)),
        "cohen_kappa": _round(kappa),
        "high_risk_sensitivity": _round(_safe_divide(high_tp, high_tp + high_fn)),
        "high_risk_specificity": _round(_safe_divide(high_tn, high_tn + high_fp)),
        "per_level": per_level,
        "confusion_matrix": confusion,
    }


def evaluate_predictions(records: Iterable[dict]) -> dict[str, dict]:
    """Return metrics grouped by the required prediction ``method`` field."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("method", "unspecified"))].append(record)
    return {method: classification_metrics(grouped[method]) for method in sorted(grouped)}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            rows.append(value)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Prediction JSONL file")
    parser.add_argument("--output", type=Path, help="Write metrics JSON to this path")
    args = parser.parse_args()
    metrics = evaluate_predictions(load_jsonl(args.input))
    result = {"input": str(args.input), "metrics": metrics}
    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
