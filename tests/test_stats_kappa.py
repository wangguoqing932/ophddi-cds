from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from stats_tests import cohens_kappa

# 12 例专家评审的实测序列（与手稿 Section 3.8 / Table 6 一致）。
# E1/E2 为两位专家各自的记录值；SHOWN 为问卷上印刷的展示值。
GOLD = ["medium", "high", "medium", "high", "high", "high",
        "low", "medium", "medium", "low", "low", "medium"]
SHOWN = ["medium", "high", "medium", "high", "high", "high",
         "low", "medium", "medium", "medium", "medium", "medium"]
E1 = ["low", "medium", "low", "medium", "medium", "medium",
      "low", "medium", "low", "low", "low", "low"]
E2 = ["low", "medium", "low", "medium", "medium", "medium",
      "low", "high", "low", "low", "low", "low"]


def test_quadratic_kappa_uses_ordinal_order_not_alphabetical() -> None:
    """回归测试：加权 kappa 的类别顺序必须来自 levels（low<medium<high）。

    此前 _kappa_core 用 sorted(set(labels)) 建混淆矩阵，字母序为
    high<low<medium，二次加权 kappa 因此算成 -0.630/-0.793。修正后应为
    +0.355（E1 vs 展示值）、+0.313（E2 vs 展示值）、+0.875（专家间）。
    """
    assert round(cohens_kappa(E1, SHOWN, weights="quadratic"), 3) == 0.355
    assert round(cohens_kappa(E2, SHOWN, weights="quadratic"), 3) == 0.313
    assert round(cohens_kappa(E1, E2, weights="quadratic"), 3) == 0.875
    assert round(cohens_kappa(E1, GOLD, weights="quadratic"), 3) == 0.473
    assert round(cohens_kappa(E2, GOLD, weights="quadratic"), 3) == 0.438


def test_unweighted_kappa_is_order_invariant() -> None:
    """未加权 kappa 不受类别顺序影响，仍应等于手稿报告值。"""
    assert round(cohens_kappa(E1, SHOWN), 3) == -0.176
    assert round(cohens_kappa(E2, SHOWN), 3) == -0.257
    assert round(cohens_kappa(E1, E2), 3) == 0.840
