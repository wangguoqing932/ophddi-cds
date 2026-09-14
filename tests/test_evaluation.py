from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluate import classification_metrics, evaluate_predictions


def test_four_level_metrics_and_high_risk_binary_metrics() -> None:
    rows = [
        {"gold_risk": "high", "predicted": "high"},
        {"gold_risk": "high", "predicted": "medium"},
        {"gold_risk": "medium", "predicted": "medium"},
        {"gold_risk": "low", "predicted": "low"},
        {"gold_risk": "unknown", "predicted": "unknown"},
    ]
    metrics = classification_metrics(rows)
    assert metrics["n"] == 5
    assert metrics["exact_accuracy"] == 0.8
    assert metrics["high_risk_sensitivity"] == 0.5
    assert metrics["high_risk_specificity"] == 1.0
    assert metrics["macro_f1"] == 0.8333
    assert metrics["cohen_kappa"] == 0.7368


def test_metrics_group_by_method_and_skip_missing_gold() -> None:
    metrics = evaluate_predictions([
        {"method": "a", "gold_risk": "high", "predicted": "high"},
        {"method": "a", "predicted": "low"},
        {"method": "b", "severity": "low", "predicted": "low"},
    ])
    assert metrics["a"]["n"] == 1
    assert metrics["b"]["exact_accuracy"] == 1.0
